from io import StringIO  # python3; python2: BytesIO
import boto3,re
from constants.s3_constants import OUTPUT_S3_BUCKET, OUTPUT_S3_BUCKET_BACKUP
from time import gmtime, strftime
import pandas as pd
from utilities.timecals import time_it

# Author : Girish Sai Thiruvidhula


@time_it
def saveToS3(hotelDataDF, filename, path_part):
    # Get the current timestamp and current time in UTC.
    current_timestamp = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    current_time = strftime("%Y-%m-%d", gmtime())

    # Create a file name for the CSV file to be saved to S3.
    fileName = current_time + "/" + path_part + "/" + filename + '_' + current_time + '.csv'

    # Set the name of the S3 bucket where the CSV file will be saved.
    bucket = OUTPUT_S3_BUCKET  # already created on S3

    # Set the name of the backup S3 bucket where the CSV file will be saved.
    backup_bucket = OUTPUT_S3_BUCKET_BACKUP  # already created backup on S3

    # Create an in-memory buffer to hold the CSV file contents.
    csv_buffer = StringIO()

    # Write the contents of the hotelDataDF DataFrame to the CSV buffer.
    hotelDataDF.to_csv(csv_buffer, index=False)

    # Create an instance of the boto3 S3 resource.
    s3_resource = boto3.resource('s3')

    # Put the contents of the CSV buffer into the S3 bucket.
    s3_resource.Object(bucket, fileName).put(Body=csv_buffer.getvalue())

    # Put the contents of the CSV buffer into the backup S3 bucket.
    s3_resource.Object(backup_bucket, fileName).put(Body=csv_buffer.getvalue())


@time_it
def getAllBuckets():
    # Retrieve the list of existing buckets
    s3 = boto3.client('s3')
    response = s3.list_buckets()
    bucketsList = []
    # Output the bucket names
    for bucket in response['Buckets']:
        bucketsList.append(bucket["Name"])
    return bucketsList



@time_it
def readS3File(bucketType,filename):
    # Create an S3 client
    s3 = boto3.client('s3')
    
    if bucketType == 'conf':
        # Retrieve the list of existing buckets
        bucketsList = getAllBuckets()
        # Filter the bucket names based on a condition
        bucket_names = [bucket for bucket in bucketsList if bucketType in bucket]

        configuration_file_bucket = bucket_names[0]
        configuration_file_key = "static/" + filename

        responseObject = s3.get_object(Bucket=configuration_file_bucket, Key=configuration_file_key)
        response = responseObject['Body'].read().decode()
    else:
        # Getting all the prefixes from the S3 bucket
        responseObj = s3.list_objects_v2(Bucket=OUTPUT_S3_BUCKET, Prefix='', Delimiter='/')
        # Fetching the lastest prefix(Date) from S3 bucket
        latest_Prefix = responseObj['CommonPrefixes'][-1]['Prefix']
        # Getting the list of objects from the latest prefix of S3 bucket
        responseJSON = s3.list_objects_v2(Bucket=OUTPUT_S3_BUCKET, Prefix=latest_Prefix, Delimiter='/')
        response = responseJSON['CommonPrefixes']
    return response


@time_it
def getDataFromS3(bucket_name,prefix,cols_list):
    s3 = boto3.client('s3')
    file_keys = s3.list_objects_v2(Bucket=bucket_name, Prefix=prefix, Delimiter='/')
    fileKeys = [file_keys['Contents'][idx]['Key'] for idx,val in enumerate(file_keys['Contents'])]
    # A master dataframe masterDF is initialized to collect the reviews data for all the business IDs.
    masterDF = pd.DataFrame(columns=cols_list)
    # Loop through each object and read it into a DataFrame
    for index,file in enumerate(fileKeys):
        object_key = file
        regex = r"[A-Z][^_]*"
        cityName = re.findall(regex, file)
        # print(cityName)
        csv_obj = s3.get_object(Bucket=bucket_name, Key=object_key)
        body = csv_obj['Body']
        csv_string = body.read().decode('utf-8')
        tempDF = pd.read_csv(StringIO(csv_string))
        # temp_cols = list(tempDF.columns)
        # if temp_cols.isin(cityName):
        #     tempDF=tempDF.loc[tempDF['City'].isin(cityName)]
        # else:
        #    pass
        masterDF = pd.concat([masterDF, tempDF])
        # Empty the DataFrame without losing schema
        tempDF.drop(index=tempDF.index, inplace=True)
    print(masterDF.shape)
    return masterDF
    
