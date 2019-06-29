from airflow.models import DAG
from airflow.operators import PythonOperator
from datetime import datetime, timedelta
import os
import json
import requests
import urllib3
import time


def install_pkg(parent_name,child_name,**context):
    global vRA_IP
    vRA_IP = context['task_instance'].xcom_pull(dag_id='main.fetch_ip',task_ids='fetch_ip')
    print("*************************************************************Post Provisioning Activities*****************************************************")
    urllib3.disable_warnings()
    url = "https://192.168.60.12:31001/api/v1/namespaces/_/actions/installnanopackage"
    headers = {
        "Authorization": "Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=",
        "Content-Type" : "application/json",
        "Accept" : "application/json"
    }
    data = {"hostname":vRA_IP,"username":"root","password":"pM0dularc"}
    data = json.dumps(data)
    output = requests.post(url,headers=headers,data=data,verify=False)
    output = output.json()
    Id = output["activationId"]

    url = "https://192.168.60.12:31001/api/v1/namespaces/_/activations/"+Id
    headers = {
        "Authorization": "Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A="
    }
    time.sleep(2)
    output = requests.get(url,headers=headers,verify=False)
    output = output.json()
    print(output["response"]["status"])

def sub_dag(parent_dag_name, child1_dag_name,child3_dag_name, start_date, schedule_interval):
    dag3 = DAG(
    '%s.%s' % (parent_dag_name, child3_dag_name),
    schedule_interval=schedule_interval,
    start_date=start_date,)
    
    t1 = PythonOperator(
        task_id='install_nano',
        provide_context=True,
        python_callable=install_pkg,
        op_args={parent_dag_name,child1_dag_name},
        dag=dag3
    )
    return dag3