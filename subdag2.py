from airflow.models import DAG
from airflow.operators import PythonOperator
from datetime import datetime, timedelta
import os
import json
import requests
import urllib3
import time

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

def deploy_vm(parent_name,child_name,**context):
    global vRA_IP
    vRA_IP = context['task_instance'].xcom_pull(dag_id='main.fetch_ip',task_ids='fetch_ip')
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

def sub_dag(parent_dag_name, child1_dag_name,child2_dag_name, start_date, schedule_interval):
    dag2 = DAG(
    '%s.%s' % (parent_dag_name, child2_dag_name),
    schedule_interval=schedule_interval,
    start_date=start_date,)

    t1 = PythonOperator(
        task_id='deploy_vm',
        provide_context=True,
        python_callable=deploy_vm,
        op_args={parent_dag_name,child1_dag_name},
        dag=dag2
    )
    return dag2
