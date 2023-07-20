from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
# from config.config import project_path
import logging
import pendulum

local_tz = pendulum.timezone("America/Toronto")

# Set default arguments for the DAG
default_args = {
    'owner': 'Girish Sai',
    'depends_on_past': False,
    'start_date': pendulum.datetime(2023, 3, 19, tz='EST'),
    'retries': 1
}

# Define the DAG
dag = DAG(
    'nemesis_data_collection',
    default_args=default_args,
    schedule_interval='0 20 * * *',  # Run at 8 PM every day
)

# Define the start and end tasks
start_task = DummyOperator(task_id='start_task', dag=dag)
end_task = DummyOperator(task_id='end_task', dag=dag)

project_path='/mnt/c/Users/giris/PycharmProjects/nemesis_hotel_sentiment_analysis/'
# Bash command
command = 'cd {} && python -m api_operations.process'.format(project_path)

# Define the BashOperator that triggers the Data Collection Python script
data_collection_task = BashOperator(
    task_id='data_collection_task',
    bash_command=command,
    dag=dag
)

rds_command = 'cd {} && python -m rds_functions.rds_process'.format(project_path)

# Define the BashOperator that triggers the RDS Ingestion Python script
rds_ingestion_task = BashOperator(
    task_id='rds_ingestion_task',
    bash_command=rds_command,
    dag=dag
)


# Set task dependencies
start_task >> data_collection_task >> rds_ingestion_task >> end_task

# Define a Python function to log a message
def log_message():
    logging.info('The DAG ran successfully.')

# Define a PythonOperator to run the log_message function
log_task = PythonOperator(
    task_id='log_task',
    python_callable=log_message,
    dag=dag,
)

# Set the log_task to run after the end_task has completed
end_task >> log_task