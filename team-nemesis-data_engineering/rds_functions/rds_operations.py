from s3_functions.utils import readS3File
# import mysql.connector
from constants.rds_constants import *

# Author : Girish Sai Thiruvidhula

def getPrefix(bucket_partname,fileType):
    prefixes = readS3File(bucket_partname,fileType)
    return prefixes
    

def getRDSConnection(HOST,USERNAME,PASSWORD,DATABASE,PORT):
    '''
    connectionString1 = mysql.connector.connect(
        host=HOST,
        user=USERNAME,
        password=PASSWORD,
        database=DATABASE
        )
    '''
    defaultStr = 'mysql+pymysql://'
    connectionString = defaultStr + USERNAME + ':' + PASSWORD +'@' + HOST + ':' + PORT +'/' + DATABASE
    # engine = sqlalchemy.create_engine('mysql+pymysql://root:@localhost:3306/application')
    return connectionString