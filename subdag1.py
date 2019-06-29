from airflow.models import DAG
from airflow.operators import PythonOperator
from datetime import datetime, timedelta
import os
import json
import requests
import urllib3
import time



def fetch_ip(ds, **kwargs):
    print("*************************************************************Fetch IP*****************************************************")
    urllib3.disable_warnings()
    prefix = "192.168.57.0/25"
    count = 1
    url = "https://192.168.60.12:31001/api/v1/namespaces/_/actions/fetch_ip_range"
    headers = {
        "Authorization": "Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=",
        "Content-Type" : "application/json",
        "Accept" : "application/json"
    }
    data = {"prefix":prefix,"number":count}
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
    IP = output["response"]["result"]["Available IPs"][0]
    global vRA_IP
    vRA_IP = IP[:-3]
    print("Fetched IP : ",vRA_IP)
    return vRA_IP

def sub_dag(parent_dag_name, child_dag_name, start_date, schedule_interval):
    dag1 = DAG(
    '%s.%s' % (parent_dag_name, child_dag_name),
    schedule_interval=schedule_interval,
    start_date=start_date,)
    
    t1 = PythonOperator(
        task_id='fetch_ip',
        provide_context=True,
        python_callable=fetch_ip,
        dag=dag1
    )
    return dag1