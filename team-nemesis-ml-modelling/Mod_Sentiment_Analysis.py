import pandas as pd  # imports the pandas library and renames it as "pd".
import re  # regular expression library that provides powerful tools for pattern matching and string manipulation.

import nltk  # nltk library provides tools and resources for working with human language data.

nltk.download('omw-1.4')
from nltk.corpus import \
    stopwords  # imports the stopwords corpus from the nltk library. The stopwords corpus is a collection of common stopwords for different languages that can be used to remove these words from text data.
from nltk.stem import \
    WordNetLemmatizer  # Lemmatization is the process of reducing a word to its base or root form, which can be useful for reducing the number of unique words in a text corpus.

from sklearn.feature_extraction.text import \
    CountVectorizer  # CountVectorizer is a method for converting text data into a matrix of token counts, which is a common way of representing text data in machine learning applications.
from sklearn.model_selection import \
    GridSearchCV  # GridSearchCV is a method for tuning hyperparameters of a machine learning model using a grid search over a specified parameter space.
from sklearn.ensemble import \
    RandomForestClassifier  # imports the RandomForestClassifier class from the sklearn.ensemble module. RandomForestClassifier is a type of ensemble learning algorithm that fits a number of decision tree classifiers on various sub-samples of the dataset and uses averaging to improve the predictive accuracy and control overfitting.
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, roc_curve, \
    classification_report
import ssl
from sklearn.model_selection import train_test_split
from sklearn import metrics
import numpy as np
import itertools
# train a random forest classifier
from sklearn.ensemble import RandomForestClassifier
from sqlalchemy import *
import pymysql

pymysql.install_as_MySQLdb()  # Install PyMySQL as the MySQL connector for SQLAlchemy


class Sentiment_Analysis:

    def __init__(self):
        # set the SSL certificate to default to avoid errors
        ssl._create_default_https_context = ssl._create_unverified_context

        # specify the packages to download
        packages = ['stopwords', 'wordnet']

        # download the packages
        for package in packages:
            nltk.download(package)

    def get_data(self):
        rdsConnection = create_engine(
            "mysql+mysqldb://admin:passwordRDS@nemesisrds.cjmjlsxabz75.us-east-1.rds.amazonaws.com/nemesis_data")
        table_name = 'hotelAndReviewDataBackup'
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql(query, rdsConnection)
        # Close the database connection
        rdsConnection.dispose()
        return df

    def text_transformation(self, df_col):
        lm = WordNetLemmatizer()
        corpus = []  # A new empty list, corpus, is created to store the transformed text data.
        for review in df_col:
            new_review = re.sub('[^a-zA-Z]', ' ', str(review))
            new_review = new_review.lower()  # transformed text data is then converted to lowercase
            new_review = new_review.split()  # transformed text data is then split into individual words
            new_review = [lm.lemmatize(word) for word in new_review if word not in set(stopwords.words('english'))]
            corpus.append(' '.join(str(x) for x in
                                   new_review))  # The lemmatized and filtered words are then joined back into a single string using the join() method, with a space as the separator. The resulting string is added to the corpus list using the append() method.
        return corpus  # returns the list of transformed text data, corpus.

    def preprocess(self):
        df = self.get_data()
        corpus = self.text_transformation(df['user_review'])
        cv = CountVectorizer(ngram_range=(1, 2))
        train_data = cv.fit_transform(corpus)
        return cv, train_data

    def train(self):
        try:
            df = self.get_data()
            df['rating'].replace([1, 2, 3, 4, 5], ['negative', 'negative', 'neutral', 'positive', 'positive'],
                                 inplace=True)
            # Encoding----
            df['rating'].replace(['positive', 'neutral', 'negative'], [1, 2, 3], inplace=True)
            cv, train_data = self.preprocess()
            X = train_data
            y = df.rating
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=0)
            rf = RandomForestClassifier(max_features='sqrt',
                                        max_depth=None,
                                        n_estimators=500,
                                        min_samples_split=5,
                                        min_samples_leaf=2,
                                        bootstrap=False)
            rf.fit(X, y)

        except Exception as e:
            print(f'Error creating model, the error message is {e}')

        return cv, rf

    def expression_check(self, prediction_input):
        if prediction_input == 1:
            return "Positive"
        elif prediction_input == 2:
            return "Neutral"
        else:
            return "Negative"

    def sentiment_predictor(self, cv, rf):
        """

        Args:
            review: 'sentence/review'

        Returns:Sentiment and  keywords from reviews and the specific sentiment

        """
        df = self.get_data()
        corpus = self.text_transformation(df['user_review'])
        test_data = cv.transform(corpus)
        y_pred = rf.predict(test_data)
        for index, row in df.iterrows():
            prediction = self.expression_check(row["user_review"])
            df.loc[index, "prediction"] = prediction


rdsConnection = create_engine(
    "mysql+mysqldb://admin:passwordRDS@nemesisrds.cjmjlsxabz75.us-east-1.rds.amazonaws.com/nemesis_data")

SentimentModule = Sentiment_Analysis()
df_pred = SentimentModule.get_data()

# Define the column name and data type for the new column
new_column_name = "prediction"
new_column_data_type = "VARCHAR(255)"

# Reflect the existing table to retrieve its metadata
metadata = MetaData()
metadata.reflect(rdsConnection)
table = Table(table_name, metadata)

if new_column_name not in table.columns:
    try:
        # Execute the ALTER TABLE statement to add the new column
        with rdsConnection.connect() as conn:
            conn.execute(f"ALTER TABLE {table_name} ADD COLUMN {new_column_name} {new_column_data_type}")
    except Exception as e:
        print(f"Error adding column: {e}")

cv, rf = SentimentModule.train()
SentimentModule.sentiment_predictor(cv, rf)

df_pred.to_sql(
    name='hotelAndReviewDataBackup',
    con=rdsConnection,
    index=False,
    if_exists='replace'
)

# Close the database connection
rdsConnection.dispose()
