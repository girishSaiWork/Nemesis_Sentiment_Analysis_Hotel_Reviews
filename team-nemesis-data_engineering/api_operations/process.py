from constants.api_constants import YELP_API_KEY, YELP_SEARCH_END_POINT, YELP_REVIEWS_END_POINT, YELP_API_KEY_BACKUP
from api_operations.operations import *
from s3_functions.utils import saveToS3

# Author : Girish Sai Thiruvidhula
# Date : 6-Feb-2023

# This code retrieves business data and reviews for hotels using Yelp API and saves the data in S3 buckets.
# Retrieve business parameters to get the data from Yelp API.

business_params = getBusinessParams()

# Accessing locations from business parameters

for business_location in business_params['location']:
    location = business_location
    # Get business data from Yelp API for the specified location and business type.
    business_data = getBusinesses(business_location, 'hotel', YELP_API_KEY, YELP_SEARCH_END_POINT,
                                  YELP_API_KEY_BACKUP)
    if business_data:  # business_data list is not empty
        # Convert the business data into a pandas DataFrame.
        business_data_DF = getBusinessData(business_data, location)
        print(f'Total number of businessIDs for the location {business_location} : {business_data_DF.shape[0]}')
        # Save the business data to an S3 bucket.
        hotel_name_with_location = 'hotel_business' + business_location
        saveToS3(business_data_DF, hotel_name_with_location, 'business_data')
        # Get reviews data for each business in the business data DataFrame from Yelp API.
        reviewsData, failed_BusinessIDs = getReviewsData(business_data_DF, YELP_REVIEWS_END_POINT, YELP_API_KEY,
                                                         YELP_API_KEY_BACKUP)
        print(f'Total number of obtained reviews for businessIDs for the location {location} : {reviewsData.shape[0]}')
        print(f'Total number of failed businessIDs for the location {location} : {len(failed_BusinessIDs)}')
        # Save the reviews data to an S3 bucket.
        reviews_name_with_location = 'hotel_reviews' + business_location
        saveToS3(reviewsData, reviews_name_with_location, 'hotel_data')
        runCounter = 0
        if failed_BusinessIDs:  # Check if there are unprocessed BusinessIDs
            if runCounter == 0:  # Check if this is the first run
                # Create a dataframe with the failed BusinessIDs and pass it to getReviewsData function
                business_Unprocessed_data = pd.DataFrame({'businessId': failed_BusinessIDs})
                reviewsData, failed_BusinessIDs = getReviewsData(business_Unprocessed_data, YELP_REVIEWS_END_POINT,
                                                                 YELP_API_KEY,
                                                                 YELP_API_KEY_BACKUP)
                print(f'Total number of businessIDs for the location {location} : {reviewsData.shape[0]}')
                saveToS3(reviewsData, 'hotel_reviews', 'hotel_data')  # Save the reviews data to S3
                runCounter += 1  # Increment the run counter
            else:
                # If there are still the unprocessed business IDs consider them as Non-operational business
                print(f'Business ID that are offline/not operational {failed_BusinessIDs}')
                exit(1)