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

release_ip = Variable.get("release_ip",deserialize_json = True)
ips = release_ip["ips"]
result = "' - '".replace('-', ",".join('"{}"'.format(i) for i in ips))
result = result[2:-2]

dag = DAG('release_ip', schedule_interval='@once',default_args=default_args)

t1 = BashOperator(
    task_id='release_ip',
    bash_command = '''curl --header "Authorization: Basic MjNiYzQ2YjEtNzFmNi00ZWQ1LThjNTQtODE2YWE0ZjhjNTAyOjEyM3pPM3haQ0xyTU42djJCS0sxZFhZRnBYbFBrY2NPRnFtMTJDZEFzTWdSVTRWck5aOWx5R1ZDR3VNREdJd1A=" -d '{"ip": [ '''+result+''' ]}' -H "Content-Type: application/json" -X POST https://192.168.60.12:31001/api/v1/namespaces/_/actions/releaseip --insecure'''
    ,dag=dag)