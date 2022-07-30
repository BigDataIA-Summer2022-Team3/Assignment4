import streamlit as st
import pickle
from pathlib import Path
from PIL import Image
import streamlit_authenticator as stauth
import requests
import time
import yaml
import os
import json

if st.session_state["authentication_status"]:
    st.markdown('# Data Performance')

    modelNum = st.selectbox(
        'Choose a Model...',
        ('01g317', '04hgtk', '04rky', '09j2d'))

    checkFlipped = st.selectbox(
        'Flipped or not Flipped?',
        ('not Flipped', 'Flipped'))

    # noiseLevel = st.selectbox(
    #      'Choose noise level...',
    #      (0.3, 0.4, 0.5))

    modelName = ''
    if(checkFlipped == 'Flipped'):
        modelName = modelNum + '-flipped'
    else:
        modelName = modelNum

    st.write(modelName)

    if st.button('Run'):
        st.write(modelName)

        paths = {
            "embedding_folder": "embeddings/",
            "groundtruth_folder": "data/",
            "submission_folder": "submissions/",
            "results_folder": "results/"
        }

        tasks = {
            "data_id": modelName,
            "train_size": 300,
            "noise_level": 0.3,
            "test_size": 500,
            "val_size": 100
        }

        tasks1 = [tasks]

        baselines = [{"name": "neighbor_shapley (datascope)"}, {"name": "random"}]

        desired_caps = {
                    'paths': paths,
                    'tasks': tasks1,
                    'baselines': baselines
                    }


        st.write(desired_caps)

        curpath = os.path.dirname(os.path.realpath(__file__))
        yamlpath = os.path.join(curpath, "../../dataperf/task_setup.yml")

        # 写入到yaml文件
        with open(yamlpath, "w", encoding="utf-8") as f:
            yaml.dump(desired_caps, f)

        # 读取，输出文件
        st.write(curpath)
        st.write(os.path.join(curpath, "../../dataperf/results"))

        resultspath = os.path.join(curpath, "../../dataperf/results/")
        resultslist = os.listdir(resultspath)
        for name in resultslist:
            if modelName in name and 'png' in name:
                image = Image.open(os.path.join(resultspath, name))
                st.image(image)
        st.write(resultslist)

        from airflow.api.client.local_client import Client

        c = Client(None, None)
        c.trigger_dag(dag_id='run_dataperf_dag', run_id='test_run_id', conf={"data_id": modelName})

                # # 等待运行，最好运行后有信息返回，实在不行就sleep
        #     data={
        #     "modelname": modelName
        # }

        # url="http://0.0.0.0:8080/api/experimental/dags/run_dataperf_dag/dag_runs"
        # data_info={}
        # data_info["conf"]=data

        # headers = {'Content-type': 'Content-type',
        #         'Cache-Control': 'no-cache'}
        # r = requests.post(url, data=json.dumps(data_info), headers=headers )
        # time.sleep(20) #需要修改睡眠时间 

else:
    st.markdown('# Please login first')