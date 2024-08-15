# Team Nemesis - ML Modelling

This part of the project focuses on the machine learning modelling of the hotel review data collected from the Yelp API through our data engineering pipeline. The goal is to perform sentiment analysis on the reviews to gain insights into customer satisfaction and experiences across various Canadian cities.

## Project Structure

- `data_preprocessing/`: Scripts for cleaning and preparing the data for modelling
- `feature_engineering/`: Code for creating relevant features from the raw text data
- `models/`: Implementation of different machine learning models for sentiment analysis
- `evaluation/`: Scripts for evaluating model performance and generating metrics
- `utils/`: Helper functions and utilities used across the project

## Data Preprocessing

1. Load the review data from S3 buckets (saved by the data engineering pipeline)
2. Clean the text data (remove special characters, lowercase, etc.)
3. Handle missing values and outliers
4. Tokenize the review text
5. Remove stop words and perform lemmatization

## Feature Engineering

1. Convert text to numerical features using techniques like:
   - Bag of Words (BoW)
   - Term Frequency-Inverse Document Frequency (TF-IDF)
   - Word Embeddings (e.g., Word2Vec, GloVe)
2. Extract additional features from the review metadata (e.g., review length, rating)

## Models

We implement and compare several machine learning models for sentiment analysis:

1. Naive Bayes
2. Logistic Regression
3. Support Vector Machines (SVM)
4. Random Forest

## Evaluation

We evaluate our models using the following metrics:

- Accuracy
- Precision
- Recall
- F1-score
- ROC-AUC

We also perform cross-validation to ensure the robustness of our models.

## Usage

To run the modelling pipeline:

1. Ensure that the data from the data engineering pipeline is available in the S3 buckets
2. Execute the preprocessing scripts to clean and prepare the data
3. Run the feature engineering scripts to create the input features
4. Train and evaluate the models using the scripts in the `models/` and `evaluation/` folders

## Results

The results of our sentiment analysis will provide insights into:

- Overall sentiment of hotel reviews across different Canadian cities
- Trends in customer satisfaction over time
- Comparison of sentiment between different hotel chains or types

These insights can be valuable for hotel managers, tourists, and city planners in understanding and improving the hospitality industry in Canada.

