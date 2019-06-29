from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from airflow.models import Variable

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2019,6,18),
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'schedule_interval':'@once',
}

installnano = Variable.get("installnano",deserialize_json = True)
hostname = installnano["hostname"]
password = installnano["password"]
username = installnano["username"]

dag = DAG(
    'install_nano', schedule_interval='@once',default_args=default_args)
 
t1 = BashOperator(
    task_id='install_nano',
    # string = 'curl --header "Authorization: Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=" -X GET https://192.168.60.12:31001/api/v1/namespaces/_/activations/e3278f05b514812b278f05b51a81299 --insecure'
    bash_command = '''curl --header "Authorization: Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=" -d '{ "hostname":"'''+hostname+'''", "username":"'''+username+'''", "password":"'''+password+'''", "port":"22"}' -H "Content-Type: application/json" -X POST https://192.168.60.12:31001/api/v1/namespaces/_/actions/installnanopackage --insecure''',dag=dag)