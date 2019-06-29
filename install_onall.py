from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from datetime import datetime, timedelta
from airflow.models import Variable

default_args = {
    'owner': 'airflow',
    'start_date': datetime.now(),
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(days=100),
    'schedule_interval': '@once',
}

installonall = Variable.get("install_onvms",deserialize_json = True)
hostname = installonall["hostname"]
password = installonall["password"]
username = installonall["username"]
packages = installonall["packages"]

dag = DAG(
    'install_onvms', schedule_interval='@once',default_args=default_args)
 
t1 = BashOperator(
    task_id='install_onvms',
    # string = 'curl --header "Authorization: Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=" -X GET https://192.168.60.12:31001/api/v1/namespaces/_/activations/e3278f05b514812b278f05b51a81299 --insecure'
    bash_command = '''curl --header "Authorization: Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=" -d '{ "vm" : [{   "hostname":"'''+hostname+'''", "username":"'''+username+'''", "password":"'''+password+'''", "port":"22" }, { "hostname":"'''+hostname+'''", "username":"'''+username+'''", "password":"'''+password+'''", "port":"22" }], "packages":"'''+packages+'''"}' -H "Content-Type: application/json" -X POST https://192.168.60.12:31001/api/v1/namespaces/_/actions/installonvms --insecure''',dag=dag)