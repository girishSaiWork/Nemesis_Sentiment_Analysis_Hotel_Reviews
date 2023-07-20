# Importing Project Specific Modules
from rds_functions.rds_operations import getPrefix,getRDSConnection
from s3_functions.utils import getDataFromS3
from constants.s3_constants import OUTPUT_S3_BUCKET
from constants.rds_constants import *
# Importing Python Packages
import pandas as pd
from datetime import datetime
from sqlalchemy import *
import pymysql
pymysql.install_as_MySQLdb()

# Getting Current timestamp
current_timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

projectPrefixes = getPrefix('dev','*.csv')

prefixList = [prefix['Prefix'] for prefix in projectPrefixes]
businessCols = ['businessId', 'hotelAlias', 'hotelName', 'is_closed', 'review_count', 
                'hotelRating', 'phoneNumber_formatted', 'distance', 'latitude',
                'longitude', 'Address', 'City', 'postal_code', 'country', 'state', 'hotelType', 
                'hotel_categoery']
    
reviewCols = ['hotelId','user_review','creation_time','user_id','user_profile_url',
              'user_name','business_id','rating']

busineesFolderName = prefixList[0]
businessData = getDataFromS3(OUTPUT_S3_BUCKET,busineesFolderName,businessCols)
businessData['is_closed'] = businessData['is_closed'].astype(bool)
# rdsConnection = getRDSConnection(HOST,USERNAME,PASSWORD,'nemesis_data')
rdsConnection = create_engine("mysql+mysqldb://admin:passwordRDS@nemesisrds.cjmjlsxabz75.us-east-1.rds.amazonaws.com/nemesis_data")

reviewsFolderName = prefixList[1]
reviewsData = getDataFromS3(OUTPUT_S3_BUCKET,reviewsFolderName,reviewCols)

# Write hotels Data DataFrame to MySQL database
businessData.to_sql(name='hotelsData', con=rdsConnection, if_exists='replace', index=False)
print(businessData.head())

# Write reviews Data DataFrame to MySQL database
reviewsData.to_sql(name='reviewsData', con=rdsConnection, if_exists='replace', index=False)
# Join dataframes based on businessId
joinedData = pd.merge(businessData, reviewsData, left_on='businessId', right_on='business_id',how='inner')
# Write reviews and hotel Data DataFrame to MySQL database
joinedData.to_sql(name='hotelAndReviewData', con=rdsConnection, if_exists='replace', index=False)

# Taking backup dataframes of businessData,hotelsData and hotelAndReviewData and adding the current timestamp 

businessDataBackUp = businessData.copy()
businessDataBackUp['dataCreatedDate'] = current_timestamp
# Write hotels Data DataFrame to MySQL backup database
businessDataBackUp.to_sql(name='hotelsDataBackup', con=rdsConnection, if_exists='append',index=False)

reviewsDataBackUp = reviewsData.copy()
reviewsDataBackUp['dataCreatedDate'] = current_timestamp
# Write reviews Data DataFrame to MySQL backup database
reviewsDataBackUp.to_sql(name='reviewsData_BackUp', con=rdsConnection, if_exists='append', index=False)

joinedDataBackUp = joinedData.copy()
joinedDataBackUp['dataCreatedDate'] = current_timestamp
# Write reviews  and hotles Data DataFrame to MySQL backup database
joinedDataBackUp.to_sql(name='hotelAndReviewDataBackup', con=rdsConnection, if_exists='append', index=False)