from airflow import DAG
from airflow.operators.bash_operator import BashOperator
import json
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

fetch_ip = Variable.get("fetch_ip",deserialize_json = True)
prefix = fetch_ip["prefix"]
count = fetch_ip["number"]

data = Variable.get("vmdeploy",deserialize_json = True)
username1 = data["username"]
password1 = data["password"]
tenant = data["tenant"]
baseurl = data["url"]
catalogname = data["catalog"]
subnetmask = data["subnetmask"]
gateway=data["gateway"]
dns = data["dns"]
suffix= data["suffix"]

installnano = Variable.get("installnano",deserialize_json = True)
hostname = installnano["hostname"]
password = installnano["password"]
username = installnano["username"]

dag = DAG('finaldag', schedule_interval='@once',default_args=default_args)

t1 = BashOperator(
    task_id='fetch_ip_range',xcom_push=True,
    # string = '''curl --header "Authorization: Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=" -X GET https://192.168.60.12:31001/api/v1/namespaces/_/activations/e3278f05b514812b278f05b51a81299 --insecure'
    bash_command = '''curl --header "Authorization: Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=" -d '{"prefix":"'''+prefix+'''","number":'''+str(count)+'''}' -H "Content-Type: application/json" -X POST https://192.168.60.12:31001/api/v1/namespaces/_/actions/fetch_ip_range --insecure ; echo $?'''
    ,dag=dag)

t2 = BashOperator(
    task_id='deploy_vm',
    bash_command = '''curl --header "Authorization: Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=" -d '{"username":"'''+username1+'''","password":"'''+password1+'''","tenant":"'''+tenant+'''","BASE_URL":"'''+baseurl+'''","catalog_name":"'''+catalogname+'''","subnetmask":"'''+subnetmask+'''","gateway":"'''+gateway+'''","dns":"'''+dns+'''","suffix":"'''+suffix+'''"}' -H "Content-Type: application/json" -X POST https://192.168.60.12:31001/api/v1/namespaces/_/actions/deployvm --insecure'''
    ,dag=dag)
print("hi")
print(t2)
print("by")
t3 = BashOperator(
    task_id='install_nano',
    # string = 'curl --header "Authorization: Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=" -X GET https://192.168.60.12:31001/api/v1/namespaces/_/activations/e3278f05b514812b278f05b51a81299 --insecure'
    bash_command = '''curl --header "Authorization: Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=" -d '{ "hostname":"'''+hostname+'''", "username":"'''+username+'''", "password":"'''+password+'''", "port":"22"}' -H "Content-Type: application/json" -X POST https://192.168.60.12:31001/api/v1/namespaces/_/actions/installnanopackage --insecure''',dag=dag)

print(t1)
print(t2)
print(t3)
t2.set_upstream(t1)
t3.set_upstream(t2)
