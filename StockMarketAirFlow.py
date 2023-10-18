from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dummy_operator import DummyOperator
import boto3
import psycopg2
import writeSummariesToDatabase as ws
import removeSummaryCsvFiles as rs
from airflow.providers.amazon.aws.sensors.step_function import StepFunctionExecutionSensor
from airflow.providers.amazon.aws.operators.step_function import StepFunctionStartExecutionOperator
from pytz import timezone
import json
import uuid

eastern_tz = timezone('US/Eastern')
STATEMACHINEARN = "YOUR_STATE_MACHINE_ARN"

default_args = {
    'owner': 'Minsoo Han',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1, tzinfo=eastern_tz),
    'retries': 3,
    'retry_delay': timedelta(minutes=2),
}

# at 30 mins interval 9AM to 4PM Mon-Fri
schedule ='30 9-16 * * 1-5'

dag = DAG(
    'get_summraies_using_stepfunction_and_write-to-database',
    default_args=default_args,
    schedule_interval=schedule,
    catchup=False,
    max_active_runs=1,
)
# If today is holiday for U.S market
# it skips a dag exceution
def checkHoliday(**kwargs):
    today = datetime.now()
    # Christmas
    if today.month == 12 and today.day == 25:
        return "skip_dag_execution"
    # You can add more closure dates below
    return "continue_dag_execution"

# Write summaries to the database
def etlTask():
    ws.writeSummariesToDatabase()

# Dummy Operators
start = DummyOperator(task_id='start', dag=dag)
end = DummyOperator(task_id='end', dag=dag)

checkHolidayTask = PythonOperator(
        task_id = 'check-holiday',
        python_callable=checkHoliday,
        provide_context=True,
        dag=dag,
)
# Hash values for naming a step function
execution_name = str(uuid.uuid4())

# Invoke the step function
start_step_function = StepFunctionStartExecutionOperator(
    task_id='start_step_function',
    state_machine_arn=STATEMACHINEARN,
    name=execution_name,
    aws_conn_id='aws_default',
    do_xcom_push=True,
    dag=dag,
)

# Wait until the step function ends
wait_for_step_function = StepFunctionExecutionSensor(
    task_id='wait_for_step_function',
    execution_arn="{{ task_instance.xcom_pull(task_ids='start_step_function', key='return_value') }}",
    aws_conn_id='aws_default',
    dag=dag,
)

databaseTask = PythonOperator(
        task_id='writeProfilesToDatabase',
        python_callable=etlTask,
        dag=dag,
)

# Remove CSV files used for getting summaries
removeCsvTask = PythonOperator(
        task_id='remove-summary-csv-files',
        python_callable=rs.removeCsvFiles,
        dag=dag,
)

start >> checkHolidayTask >> start_step_function >> wait_for_step_function >> databaseTask >> removeCsvTask >> end