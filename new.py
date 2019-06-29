from airflow import DAG
from airflow.operators import PythonOperator
from datetime import datetime, timedelta
import os
import json
import requests
import urllib3
import time

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2001, 6, 1),
    'depends_on_past': False,
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
    'schedule_interval': '@once',
}

vRA_username = "administrator"
vRA_password = "pM0dularc!"
vRA_tenant = "ICDS"
vRA_url = "192.168.56.5"
vRA_catalogname = "Sree-Linux-copy"
vRA_subnetmask = "255.255.52.0"
vRA_gateway = "192.168.56.1"
vRA_dns = "192.168.56.2"
vRA_name = "DPortGroup"
vRA_suffix = "icds.online"
vRA_IP = ""

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
    # default_args["start_date"] = datetime.now()



def deploy_vm(**context):
    global vRA_IP
    vRA_IP = context['task_instance'].xcom_pull(task_ids='fetch_ip')
    print("*************************************************************Deploy VM*****************************************************")
    urllib3.disable_warnings()
    url = "https://192.168.60.12:31001/api/v1/namespaces/_/actions/deployvm"
    headers = {
        "Authorization": "Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=",
        "Content-Type" : "application/json",
        "Accept" : "application/json"
    }
    data = {
        "username":vRA_username,
        "password":vRA_password,
        "tenant":vRA_tenant,
        "BASE_URL":vRA_url,
        "catalog_name":vRA_catalogname,
        "subnetmask":vRA_subnetmask,
        "gateway":vRA_gateway,
        "dns":vRA_dns,
        "suffix":vRA_suffix,
        "name":vRA_name,
        "ip":vRA_IP
    }
    data = json.dumps(data)
    output = requests.post(url,headers=headers,data=data,verify=False)
    output = output.json()
    Id = output["activationId"]
    url_acti = "https://192.168.60.12:31001/api/v1/namespaces/_/activations/"+Id
    headers = {
        "Authorization": "Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A="
    }
    print("Deploying VM")
    time.sleep(3)
    output = requests.get(url_acti,headers=headers,verify=False)
    output = output.json()
    time.sleep(2)
    print(output)
    Id = output["response"]["result"]["id"]

    auth_data = {"username":vRA_username,"password":vRA_password,"tenant":vRA_tenant}
    auth_data = json.dumps(auth_data)
    auth_header= {"Content-Type":"application/json","Accept":"application/json"}
    auth_req = requests.post("https://"+vRA_url+"/identity/api/tokens/",headers=auth_header,data=auth_data,verify=False)
    time.sleep(2)
    token = auth_req.json()['id']
    req_header = {"Authorization":"Bearer "+token, "Content-Type" : "application/json", "Accept" : "application/json"}
    while(1):
        req5 = requests.get("https://"+vRA_url+"/catalog-service/api/consumer/requests/"+Id,headers=req_header,verify=False)
        if(req5.json()["state"]=="UNSUBMITTED"):
            print("UNSUBMITTED")
            return {"Unsubmitted":"Request was saved but not submitted","info":req5.json()}
        elif(req5.json()["state"]=="FAILED"):
            print("FAILED")
            return {"Failed":"Request Failed"}
        elif(req5.json()["state"]=="REJECTED"):
            print("REJECTED")
            return {"Rejected":"Request approval was rejected and will not complete","info":req5.json()}
        elif(req5.json()["state"]=="IN_PROGRESS"):
            continue
        elif(req5.json()["state"]=="SUCCESSFUL"):
            print("SUCCESSFUL")
            return {"Successful":"Request completed successfully", "info":req5.json()}
        elif(req5.json()["state"]=="CANCELLED"):
            print("CANCELLED")
            return {"Cancelled":"Request Cancelled By Administrator", "info":req5.json()}


def post_provision(**context):
    global vRA_IP
    vRA_IP = context['task_instance'].xcom_pull(task_ids='fetch_ip')
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


dag = DAG(
'test08', default_args=default_args, schedule_interval='@once')

t1 = PythonOperator(
    task_id='fetch_ip',
    provide_context=True,
    python_callable=fetch_ip,
    dag=dag
)


t2 = PythonOperator(
    task_id='deploy_vm',
    provide_context=True,
    python_callable=deploy_vm,
    dag=dag
)


t3 = PythonOperator(
    task_id='post_provision',
    provide_context=True,
    python_callable=post_provision,
    dag=dag
)

t1 >> t2
t2 >> t3