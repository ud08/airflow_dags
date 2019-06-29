from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta



dag = DAG(
    'fetch_ip', default_args=default_args, schedule_interval=timedelta(days=1))

t1 = BashOperator(
    task_id='fetch_ip',
    # string = '''curl --header "Authorization: Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=" -X GET https://192.168.60.12:31001/api/v1/namespaces/_/activations/e3278f05b514812b278f05b51a81299 --insecure'
    bash_command = '''curl --header "Authorization: Basic MjNidefault_args = {
    'owner': 'airflow',
    'start_date': datetime.now(),
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,       
    'retry_delay': timedelta(days=100),
    'schedule_interval': '@once',
}YzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=" -X POST https://192.168.60.12:31001/api/v1/namespaces/_/actions/fetchip --insecure'''
    ,dag=dag)