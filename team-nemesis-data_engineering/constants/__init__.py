from configparser import ConfigParser
import boto3

# Author : Girish Sai Thiruvidhula

def readS3ConfFiles(response):
    # Create an empty dictionary to hold the configuration options.
    S3_configDetails = {}

    # Create a ConfigParser instance.
    configur = ConfigParser()

    # Read the configuration options from the config.ini file located in the ../config directory.
    configur.read_string(response)

    # Get the values of the main_region, backup_region, output_bucket, and backup_bucket options from the aws_account
    # section of the configuration file.
    s3_bucket_region = configur.get('aws_account', 'main_region')
    s3_bucket_backup_region = configur.get('aws_account', 'backup_region')
    s3_output_bucket = configur.get('aws_account', 'output_bucket')
    s3_backup_bucket = configur.get('aws_account', 'backup_bucket')

    # Add the values of the configuration options to the S3_configDetails dictionary with corresponding keys.
    S3_configDetails['s3_bucket_region'] = s3_bucket_region
    S3_configDetails['s3_bucket_backup_region'] = s3_bucket_backup_region
    S3_configDetails['s3_output_bucket'] = s3_output_bucket
    S3_configDetails['s3_backup_bucket'] = s3_backup_bucket

    # Return the S3_configDetails dictionary.
    return S3_configDetails


def readAPIConfDetails(response):
    # Create an empty dictionary to hold the configuration options.
    apiConfigDetails = {}

    # Create a ConfigParser instance.
    configuration = ConfigParser()

    # Read the configuration options from the config.ini file located in the ../config directory.
    configuration.read_string(response)

    # Get the values of the api_key, search_endpoint, reviews_endpoint, and yelp_api_params_path options from the
    # yelp_api section of the configuration file.
    api_key = configuration.get('yelp_api', 'api_key')
    api_key_backup = configuration.get('yelp_api', 'api_key_backup')
    search_endpoint = configuration.get('yelp_api', 'search_endpoint')
    reviews_endpoint = configuration.get('yelp_api', 'reviews_endpoint')
    yelp_api_params_path = configuration.get('yelp_api', 'yelp_api_params_path')

    # Add the values of the configuration options to the apiConfigDetails dictionary with corresponding keys.
    apiConfigDetails['api_key'] = api_key
    apiConfigDetails['api_key_backup'] = api_key_backup
    apiConfigDetails['search_endpoint'] = search_endpoint
    apiConfigDetails['reviews_endpoint'] = reviews_endpoint
    apiConfigDetails['yelp_api_params_path'] = yelp_api_params_path

    # Return the apiConfigDetails dictionary.
    return apiConfigDetails



def readMySQLConfDetails(response):
    # Create an empty dictionary to hold the configuration options.
    mySqlConfigDetails = {}

    # Create a ConfigParser instance.
    configuration = ConfigParser()

    # Read the configuration options from the config.ini file located in the ../config directory.
    configuration.read_string(response)

    # Get the values of the mysql, connection name, host, username and password options from the
    # mysql section of the configuration file.
    connect_name = configuration.get('mysql', 'connection_name')
    host = configuration.get('mysql', 'host')
    port = configuration.get('mysql', 'port')
    username = configuration.get('mysql', 'username')
    password = configuration.get('mysql', 'password')

    # Add the values of the configuration options to the mysqlConfigDetails dictionary with corresponding keys.
    mySqlConfigDetails['connect_name'] = connect_name
    mySqlConfigDetails['host'] = host
    mySqlConfigDetails['port'] = port
    mySqlConfigDetails['username'] = username
    mySqlConfigDetails['password'] = password

    # Return the mysqlConfigDetails dictionary.
    return mySqlConfigDetails


def readAPIConfigDataS3():
    # Create an S3 client
    s3 = boto3.client('s3')

    # Filter the bucket names based on a condition
    # bucket_names = [bucket.name for bucket in s3.buckets.all() if 'conf' in bucket.name]

    configuration_file_bucket = 'nemesis-conf-files'
    configuration_file_key = "config/config.ini"

    responseObject = s3.get_object(Bucket=configuration_file_bucket, Key=configuration_file_key)
    response = responseObject['Body'].read().decode()
    apiConfData = readAPIConfDetails(response)
    return apiConfData


def readS3ConfigDataFromS3():
    # Create an S3 client
    s3 = boto3.client('s3')

    # Filter the bucket names based on a condition
    # bucket_names = [bucket.name for bucket in s3.buckets.all() if 'conf' in bucket.name]

    configuration_file_bucket = 'nemesis-conf-files'
    configuration_file_key = "config/config.ini"

    responseObject = s3.get_object(Bucket=configuration_file_bucket, Key=configuration_file_key)
    response = responseObject['Body'].read().decode()
    S3ConfigData = readS3ConfFiles(response)
    return S3ConfigData


def readMySQLConfigDataFromS3():
    # Create an S3 client
    s3 = boto3.client('s3')

    # Filter the bucket names based on a condition
    # bucket_names = [bucket.name for bucket in s3.buckets.all() if 'conf' in bucket.name]

    configuration_file_bucket = 'nemesis-conf-files'
    configuration_file_key = "config/config.ini"

    responseObject = s3.get_object(Bucket=configuration_file_bucket, Key=configuration_file_key)
    response = responseObject['Body'].read().decode()
    mySQLConfigData = readMySQLConfDetails(response)
    return mySQLConfigData