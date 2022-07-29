import streamlit as st
import logging
import pickle
from pathlib import Path
from PIL import Image
import streamlit_authenticator as stauth
import requests
import time
import yaml
import os

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
    yamlpath = os.path.join(curpath, "../../task_setup.yaml")

    # 写入到yaml文件
    with open(yamlpath, "w", encoding="utf-8") as f:
        yaml.dump(desired_caps, f)

    # 等待运行，最好运行后有信息返回，实在不行就sleep


    # 读取，输出文件
    st.write(curpath)
    st.write(os.path.join(curpath, "../../results"))

    resultspath = os.path.join(curpath, "../../results/")
    resultslist = os.listdir(resultspath)
    for name in resultslist:
        if modelName in name and 'png' in name:
            image = Image.open(os.path.join(resultspath, name))
            st.image(image)
    st.write(resultslist)