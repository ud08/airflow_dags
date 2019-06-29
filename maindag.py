# main_dag.py
from datetime import datetime, timedelta
from airflow.models import DAG
from airflow.operators.subdag_operator import SubDagOperator
import subdag1,subdag2,subdag3
import urllib3

PARENT_DAG_NAME = 'main'
CHILD_DAG_NAME = 'fetch_ip'
CHILD2_DAG_NAME = 'deploy_vm'
CHILD3_DAG_NAME = 'install_pkg'
vRA_IP = ""
main_dag = DAG(
  dag_id=PARENT_DAG_NAME,
  schedule_interval='@once',
  start_date=datetime(2016, 1, 1)
)
urllib3.disable_warnings()
sub_dag = SubDagOperator(
  subdag=subdag1.sub_dag(PARENT_DAG_NAME, CHILD_DAG_NAME, main_dag.start_date,
                 main_dag.schedule_interval),
  task_id=CHILD_DAG_NAME,
  dag=main_dag,
)
# vRA_IP = sub_dag.xcom_pull(task_ids='fetch_ip')
# print(vRA_IP)
sub_dag2 = SubDagOperator(
  subdag =subdag2.sub_dag(PARENT_DAG_NAME, CHILD_DAG_NAME, CHILD2_DAG_NAME, main_dag.start_date,
                 main_dag.schedule_interval),
  task_id=CHILD2_DAG_NAME,
  dag=main_dag,
)

sub_dag3 = SubDagOperator(
  subdag =subdag3.sub_dag(PARENT_DAG_NAME, CHILD_DAG_NAME, CHILD3_DAG_NAME, main_dag.start_date,
                 main_dag.schedule_interval),
  task_id=CHILD3_DAG_NAME,
  dag=main_dag,
)

sub_dag >> sub_dag2
sub_dag2 >> sub_dag3