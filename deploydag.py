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

data = Variable.get("vmdeploy",deserialize_json = True)
username = data["username"]
password = data["password"]
tenant = data["tenant"]
baseurl = data["url"]
catalogname = data["catalog"]
subnetmask = data["subnetmask"]
gateway=data["gateway"]
dns = data["dns"]
name = data["name"]
ip = data["ip"]
suffix= data["suffix"]

dag = DAG('deploy_vm', schedule_interval='@once',default_args=default_args)

t1 = BashOperator(
    task_id='deploy_vm',
    bash_command = '''curl --header "Authorization: Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=" -d '{"username":"'''+username+'''","password":"'''+password+'''","tenant":"'''+tenant+'''","BASE_URL":"'''+baseurl+'''","catalog_name":"'''+catalogname+'''","subnetmask":"'''+subnetmask+'''","gateway":"'''+gateway+'''","dns":"'''+dns+'''","suffix":"'''+suffix+'''","ip":"'''+ip+'''","name":"'''+name+'''"}' -H "Content-Type: application/json" -X POST https://192.168.60.12:31001/api/v1/namespaces/_/actions/deployvm --insecure'''
    ,dag=dag)