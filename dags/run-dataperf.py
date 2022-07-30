# import os
# path = os.path.abspath(os.path.join(os.path.dirname(__file__),".."))

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

# import boto3
# import json


# os.path.abspath('../')

default_args = {
    "owner": "DAMG7245-summer2022-team3",
    'depends_on_past': False,
    "start_date": datetime(2022, 7, 21),
    'retry_delay': timedelta(minutes=5),
    'provide_context': True
}

# def upload_dataperf_result_to_s3(ti):

#     test_list, pred_list = [], []
#     test_list = ti.xcom_pull(task_ids='detect_images', key='test_list')
#     pred_list = ti.xcom_pull(task_ids='detect_images', key='pred_list')
        
#     s3 = boto3.client('s3',
#                 region_name = 'us-east-1',
#                 aws_access_key_id= config.ACKEY,
#                 aws_secret_access_key= config.SCKEY
#     )
#     dt = datetime.now().strftime('%Y-%m-%d-%H-%M')
#     json_object = {"truth": test_list,
#                     "predict": pred_list}

#     s3.put_object(
#         Body=json.dumps(json_object),
#         Bucket='damg7245defect-inspection',
#         Key='confusion_matrix/'+dt
#     )


with DAG(
    dag_id = 'run_dataperf_dag',
    default_args= default_args,
    schedule_interval = None
    ) as dag:

    dataperf_command = """
        cd /home/zhijieprod/assign4/dataperf/
        echo `pwd`
        python3 create_baselines.py && python3 main.py && python3 plotter.py
        echo got the file
    """  

    print_start_task = BashOperator(
            task_id='print_start',
            depends_on_past=False,
            bash_command= 'echo start',
        )

    main_task = BashOperator(
            task_id='test_data_perf',
            depends_on_past=False,
            bash_command= dataperf_command,
        )

    print_finished_task = BashOperator(
            task_id='print_finished',
            depends_on_past=False,
            bash_command ='echo Finished',
        )

    print_start_task >> main_task >> print_finished_task


    # create_baselines_task = PythonOperator(
    #         task_id='print_start',
    #         python_callable = create_baselines,
    #     )


    # main_task = BashOperator(
    #         task_id='test_data_perf',
    #         bash_command= main,
    #     )

    # plotter_task = BashOperator(
    #         task_id='plotter',
    #         bash_command= plotter,
    #     )