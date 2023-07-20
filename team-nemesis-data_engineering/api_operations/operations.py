import json
import requests
import pandas as pd
from s3_functions.utils import readS3File
from utilities.timecals import time_it

# Author : Girish Sai Thiruvidhula

@time_it
def getBusinessParams():
    # This function reads the Yelp API business parameters from a JSON file located in S3 bucket.
    businessParameters = readS3File('conf','params.json')
    # The file contains information like the location of businesses to search, the search radius, and the
    # limit of results to return. Open the JSON file containing the Yelp API business parameters.
    if len(businessParameters) == '':
        with open('../static/params.json', 'r') as f:
            # Load the JSON data into a dictionary.
            business_params = json.load(f)
    else:
        business_params = json.loads(businessParameters)
    # Return the dictionary containing the Yelp API business parameters.
    return business_params


@time_it
def getBusinesses(business_params, term, YELP_API_KEY, search_end_point, YELP_API_KEY_BACKUP):
    # This function is used to get the YELP business details through the API by taking term i.e., hotels and location
    # Set the Authorization header with the Yelp API key
    headers = {'Authorization': 'Bearer %s' % YELP_API_KEY}
    # Define the URL of the Yelp API endpoint
    url = f'{search_end_point}'

    # Initialize an empty list to store the retrieved businesses data
    business_data = []
    # Loop over the offsets, in steps of 50, to append through the results
    for offset in range(0, 1000, 50):
        # Define the request parameters including limit, location, term, and offset
        # Ref : https://stackoverflow.com/questions/35525994/how-to-request-more-than-20-results-from-yelp-api
        # Yelp API is giving only 50 records per request, So if we send the request we are getting only the first
        # request data again. To fix this issue, we have added the offset parameter and for every iteration it will
        # change the offset and get the data from next offset i.e., as the limit = 50 we will fetch from 51th
        # business ID from API
        params = {
            'limit': 50,
            'location': business_params,
            'term': term,
            'offset': offset
        }
        # Send an HTTP GET request with the URL, headers, and parameters
        response = requests.get(url=url, headers=headers, params=params)
        # If the response status code is 200, add the businesses data to the list
        if response.status_code == 200:
            business_data += response.json()['businesses']
        # If the response status code is 400, print an error message and break the loop
        elif response.status_code in [401, 403, 413, 429]:
            print('Using the Backup Key for getting Hotel business IDs')
            headers = {'Authorization': 'Bearer %s' % YELP_API_KEY_BACKUP}
            response = requests.get(url=url, headers=headers, params=params)
            business_data += response.json()['businesses']
        elif response.status_code == 400:
            # If the request was unsuccessful, print a message indicating that it was a bad request break the response.
            print('400 Bad Request')
            print(response.json())
            break
        else:
            pass
    # Return the list of businesses data
    return business_data


@time_it
def getBusinessData(jsonData,location):
    # This function takes a JSON object as input, converts it to a pandas DataFrame, performs several transformations
    # on the DataFrame, and returns a new DataFrame containing curated hotel data.
    # The input JSON object contains information about hotels obtained from the Yelp API, which includes details
    # such as hotel name, location, rating, phone number, etc.
    jsonDataFrame = pd.json_normalize(jsonData)
    # The function first normalizes the JSON data into a pandas DataFrame using the pd.json_normalize function.
    # We are using the explode function to create multiple rows for each category assigned to the hotel.
    # as it contains the list as column data
    json_Explode_DataFrame = jsonDataFrame.explode('categories')
    # Extracting the Title from categories, as it contains the JSON data for explode
    hotelTypeDF = pd.DataFrame(json_Explode_DataFrame.categories.apply(pd.Series).title)
    # Join two columns
    # The json_Join_data DataFrame is created by joining the json_Explode_DataFrame and hotelTypeDF
    # DataFrames based on their indices.
    json_Join_data = json_Explode_DataFrame.join(hotelTypeDF)
    # unwanted columns list
    unWantedColsList = ['price', 'transactions', 'image_url', 'location.display_address', 'location.address2',
                        'location.address3', 'categories', 'url','phone']
    json_unWanted_DataFrame = json_Join_data.loc[:, ~json_Join_data.columns.isin(unWantedColsList)]
    # Renaming Cols
    colsDict = {'id': 'businessId', 'alias': 'hotelAlias', 'name': 'hotelName', 'rating': 'hotelRating',
                'title': 'hotelType', 'display_phone': 'phoneNumber_formatted','coordinates.latitude': 'latitude', 
                'coordinates.longitude': 'longitude','location.address1': 'Address', 'location.city': 'City', 
                'location.zip_code': 'postal_code','location.country': 'country', 'location.state': 'state'}
    json_renamed_DataFrame = json_unWanted_DataFrame.rename(columns=colsDict)
    json_cityFiltered = json_renamed_DataFrame.loc[json_renamed_DataFrame['City'] == location ]
    nullIgnoreCols = ['hotelAlias','Address','hotelType','phoneNumber_formatted']
    cols_to_dropna = [col for col in list(json_cityFiltered.columns) if col not in nullIgnoreCols]
    # filter rows based on missing or null values
    mask = json_cityFiltered[cols_to_dropna].isnull().any(axis=1)
    nullFixingData = json_cityFiltered[~mask]  # keep rows where all columns are non-null
    nullDroppedDdata = json_cityFiltered[mask]  # drop rows where any column is null
    # define dictionary of columns to fill with their respective fill values
    fill_dict = {'hotelAlias': nullFixingData['hotelName'], 'Address': nullFixingData['City'],
                 'hotelType':'hotel', 'phoneNumber_formatted': '+0 000-000-0000'}
    if nullFixingData.isna().any().any() or (nullFixingData.applymap(str) == '').any().any():
        # fill missing values with fill_dict
        json_curated_DataFrame = nullFixingData.fillna(value=fill_dict)
    else:
        json_curated_DataFrame = nullFixingData
    json_hotelData = json_curated_DataFrame.assign(hotel_categoery='hotel')
    return json_hotelData


@time_it
def getReviewsData(businessDFdata, reviews_endpoint, YELP_API_KEY, YELP_API_KEY_BACKUP):
    # This function is used to get the reviews for the businessID's we got from the above get_businesses method
    # Set the Authorization header with the Yelp API key
    headers = {'Authorization': 'Bearer %s' % YELP_API_KEY}
    # Define the reviews URL of the Yelp API endpoint
    url = f'{reviews_endpoint}'
    # Declare a list for unprocessed Business IDs in the current run
    failed_businessIDs = []
    # Dropping duplicates from the list of business IDs
    businessIDs = list(set([ele for ele in businessDFdata['businessId'].values]))
    FIELDS = ["id", "url", "text", "time_created", "user.id", "user.profile_url", "user.image_url", "user.name",
              "business_id"]
    # The FIELDS variable contains the list of fields to be extracted from Yelp API's response.
    # A master dataframe masterDF is initialized to collect the reviews data for all the business IDs.
    masterDF = pd.DataFrame(columns=FIELDS)
    # For each business ID in businessIDs list, the method makes a request to Yelp API to get the reviews data for
    # that particular business ID. If the response is successful, the reviews data is extracted and added to the
    # masterDF dataframe.
    for business_id in businessIDs:
        review_response_data = requests.get(url.format(business_id=business_id), headers=headers)
        # Check if the status code of the response is 200, which indicates a successful request.
        if review_response_data.status_code == 200:
            # If the request was successful, normalize the JSON data and assign the current business ID
            # to a new column in the resulting DataFrame.
            businessDF = pd.json_normalize(review_response_data.json()['reviews']).assign(business_id=business_id)
            # Concatenate the current DataFrame to the master DataFrame containing all the reviews.
            masterDF = pd.concat([masterDF, businessDF])
        elif review_response_data.status_code in [401, 403, 413, 429]:
            # Check if the status code of the response is in the list of known error codes.
            print('Using the Backup Key for getting reviews')  # Processing the request using Back up API key
            headers = {'Authorization': 'Bearer %s' % YELP_API_KEY_BACKUP}
            review_response_data = requests.get(url.format(business_id=business_id), headers=headers)
            businessDF = pd.json_normalize(review_response_data.json()['reviews']).assign(business_id=business_id)
            masterDF = pd.concat([masterDF, businessDF])
        elif review_response_data.status_code == 400:
            # If the request was unsuccessful, print a message indicating that it was a bad request, and
            # append the current business ID to the list of failed IDs.
            print('400 Bad Request')
            failed_businessIDs.append(business_id)
        else:
            pass
    # unwanted columns list
    unWantedColsList = ['url', 'user.image_url']
    # unWantedColsList contains a list of columns that are not required, which are dropped from the masterDF dataframe
    reviews_DataFrame = masterDF.loc[:, ~masterDF.columns.isin(unWantedColsList)]
    # Renaming Cols list
    rename_colsDict = {'id': 'hotelId', 'text': 'user_review', 'time_created': 'creation_time',
                       'user.id': 'user_id', 'user.profile_url': 'user_profile_url', 'user.name': 'user_name'}
    # remaining columns in the dataframe are then renamed using the rename_colsDict.
    reviews_renameData = reviews_DataFrame.rename(columns=rename_colsDict)
    if reviews_renameData.isna().any().any() or (reviews_renameData.applymap(str) == '').any().any():
        reviews_Data = reviews_renameData.dropna()
    else:
        reviews_Data = reviews_renameData
    return reviews_Data, failed_businessIDs
