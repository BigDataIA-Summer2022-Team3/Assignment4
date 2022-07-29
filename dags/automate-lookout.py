from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

import os
import json
import boto3
import config

default_args = {
    "owner": "DAMG7245-summer2022-team3",
    'depends_on_past': False,
    "start_date": datetime(2022, 7, 21),
    'retry_delay': timedelta(minutes=5),
    'execution_timeout': timedelta(seconds=420),
    'provide_context': True
}

def start_model(dag_run = None):
    """
    Print the payload "message" passed to the DagRun conf attribute.

    :param dag_run: The DagRun object
    :type dag_run: DagRun
    """
    start_message = client.start_model(
        ProjectName='damg7245team3',
        ModelVersion='2',
        MinInferenceUnits=1,
    )
    print(f"Remotely start model. Model status: {start_message['Status']}")


def check_model(dag_run = None):

    response = client.describe_model(
        ProjectName='damg7245team3',
        ModelVersion='2'
    )
    print(f"Check model status.  Model status: {response['ModelDescription']['Status']}")


def detect_images(ti):
    """
    Print the payload "message" passed to the DagRun conf attribute.

    :param dag_run: The DagRun object
    :type dag_run: DagRun
    """
    parent_path = '/Users/lizhijie_1/airflow/casting-data/'
    filenamelist = os.listdir(parent_path)

    test_list, pred_list = [], []
    
    for filename in filenamelist:
        filepath = parent_path + filename
        
        if "def" in filename:
            test_list.append(0)
        else:
            test_list.append(1)

        with open(filepath, 'rb') as f:
            byte_im = f.read()
            response = client.detect_anomalies(
                    ProjectName='damg7245team3',
                    ModelVersion='2',
                    Body= byte_im, 
                    ContentType='image/jpeg'
                )

        reval = response["DetectAnomalyResult"]
        if(str(reval["IsAnomalous"]) == "True"):
            pred_list.append(0)
        else:
            pred_list.append(1)

    ti.xcom_push(key='test_list', value=test_list)
    ti.xcom_push(key='pred_list', value=pred_list)
    return test_list, pred_list;

def upload_predict_result_to_s3(ti):
    """
    :param y_test: a list has all real info
    :type y_test: list of int

    :param y_pred: a list has all predict info
    :type y_pred: list of int
    """
    test_list, pred_list = [], []
    test_list = ti.xcom_pull(task_ids='detect_images', key='test_list')
    pred_list = ti.xcom_pull(task_ids='detect_images', key='pred_list')
        
    s3 = boto3.client('s3',
                region_name = 'us-east-1',
                aws_access_key_id= config.ACKEY,
                aws_secret_access_key= config.SCKEY
    )
    dt = datetime.now().strftime('%Y-%m-%d-%H-%M')
    json_object = {"truth": test_list,
                    "predict": pred_list}

    s3.put_object(
        Body=json.dumps(json_object),
        Bucket='damg7245defect-inspection',
        Key='confusion_matrix/'+dt
    )

    print(test_list, pred_list)
    return test_list, pred_list;


def stop_model(dag_run = None):
    """
    Print the payload "message" passed to the DagRun conf attribute.

    :param dag_run: The DagRun object
    :type dag_run: DagRun
    """
    response = client.stop_model(
        ProjectName='damg7245team3',
        ModelVersion='2',

    )
    print(f"Remotely stop model. Model status: {response['Status']}")


with DAG(
    dag_id = 'test_Lookout_model_dag',
    default_args= default_args,
    schedule_interval = None
    ) as dag:

    client = boto3.client('lookoutvision',
                        region_name = 'us-east-1',
                        aws_access_key_id= config.ACKEY,
                        aws_secret_access_key= config.SCKEY)

    start_model_task = PythonOperator(
        task_id = 'start_Lookout_model',
        python_callable=start_model,
        dag = dag,
    )

    waiting_for_model_task = BashOperator(
            task_id='sleep_till_model_open',
            depends_on_past=False,
            bash_command='sleep 220',
            dag = dag,
        )

    check_model_status_task = PythonOperator(
        task_id = 'check_Lookout_model_state',
        python_callable = check_model,
    )

    detect_images_task = PythonOperator(
        task_id = 'detect_images',
        python_callable = detect_images,
        dag = dag,
    )

    gen_confusion_matrix_task = PythonOperator(
        task_id = 'upload_predict_result',
        python_callable = upload_predict_result_to_s3,
        dag = dag,
    ) 

    close_model_task = PythonOperator(
        task_id = 'stop_Lookout_model',
        python_callable = stop_model,
        dag = dag,
    )
    
    start_model_task >> waiting_for_model_task >> check_model_status_task >> detect_images_task >> gen_confusion_matrix_task >> close_model_task

