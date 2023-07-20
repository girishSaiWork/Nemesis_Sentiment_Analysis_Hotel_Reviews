from constants import readAPIConfigDataS3

apiConfigData = readAPIConfigDataS3()
YELP_API_KEY = apiConfigData['api_key']
YELP_API_KEY_BACKUP = apiConfigData['api_key_backup']
YELP_SEARCH_END_POINT = apiConfigData['search_endpoint']
YELP_REVIEWS_END_POINT = apiConfigData['reviews_endpoint']
YELP_PARAMS_PATH = apiConfigData['yelp_api_params_path']

YELP_ITER_LIMIT = 50
YELP_MAX_LIMIT = 1000
