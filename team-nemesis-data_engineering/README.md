# team-nemesis
Sentimental analysis using Goggle Reviews
# Team Nemesis - Data Engineering

This part of project focuses on collecting and processing hotel data from Yelp API for sentiment analysis. The data engineering pipeline retrieves business information and reviews for hotels in various Canadian cities.

## Project Structure

- `api_operations/`: Contains scripts for interacting with the Yelp API
  - `process.py`: Main script for retrieving business data and reviews
  - `operations.py`: Helper functions for API operations
- `constants/`: Stores API constants and configuration
- `s3_functions/`: Includes utilities for saving data to Amazon S3
- `static/`: Contains static files
  - `params.json`: Parameters for API requests (search terms, locations, limits)

## Data Collection Process

1. The script reads search parameters from `static/params.json`.
2. For each specified location (Toronto, Vancouver, Montreal, etc.):
   a. Retrieves business data for hotels using the Yelp API.
   b. Converts business data to a pandas DataFrame.
   c. Saves business data to an S3 bucket.
   d. Fetches reviews for each business.
   e. Saves review data to an S3 bucket.
3. Handles any failed API requests by retrying once.

## Key Features

- Uses both primary and backup Yelp API keys for resilience.
- Saves data in separate S3 buckets for business and review data.
- Implements error handling and retries for failed API requests.
- Processes multiple Canadian cities as specified in the parameters file.

## Usage

To run the data collection process, execute the `process.py` script in the `api_operations` folder. Ensure that all required dependencies are installed and API keys are properly configured.

## Data Output

- Business data: Saved as 'hotel_business{location}' in the 'business_data' S3 bucket
- Review data: Saved as 'hotel_reviews{location}' in the 'hotel_data' S3 bucket

This data can be used for further analysis, including sentiment analysis of hotel reviews across different Canadian cities.
