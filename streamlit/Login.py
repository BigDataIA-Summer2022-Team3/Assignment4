import streamlit as st
import pickle
from pathlib import Path
import streamlit_authenticator as stauth
import pymysql
import requests
import logging
# from dbconfig import funct

#need "pip install streamlit-authenticator==0.1.5"


logging.basicConfig(filename='logs.txt')
logging.debug('Start the Streamlit log')


st.markdown('# Login Page')

usernames = ["zhijie", "yijun", "team4", "parth", "srikanth"]

#load passwords
file_path = Path(__file__).parent / "streamlitUserPW.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)
    
authenticator = stauth.Authenticate(usernames, usernames, hashed_passwords, "Login", "abcdef", cookie_expiry_days=0)

name, authentication_status, username = authenticator.login("Login" , "main")


def load_token(username): #password if has
    url = "https://damg-team3-lookout.herokuapp.com/token"

    header = {
        "accept": "application/json",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
            "grant_type":"",  "scope": "", "client_id": "", "client_secret": "",
            "username": username, "password": username + "pw"  # To do: Fetch the password from DB
            }
    
    authentication = requests.post(url, data, header)
    token = authentication.json()["access_token"]
    if(st.session_state["token"] == "" ): 
        st.session_state["token"] = token


# Initialization
if "token" not in st.session_state:
    st.session_state["token"] = ""

if st.session_state["authentication_status"]:
    # authenticator.logout('Logout', 'sidebar')
    st.markdown(f'# Welcome *{st.session_state["name"]}*')

    Host, User, Password = st.secrets["Host"] , st.secrets["User"] , st.secrets["Password"]
    # Host, User, Password = funct()
    con = pymysql.connect(host = Host, user = User, password = Password, database = 'lemon', charset = "utf8")
    c = con.cursor()
    c.execute('select * from user_table where username = "%s"' % st.session_state.username)
    datainfo = c.fetchall()
    username = datainfo[0][1]

    load_token(username) #dbpassword if has
    logging.debug(f'User {username} log in')

    
    
elif st.session_state["authentication_status"] == False:
    st.error('Username/password is incorrect')    

elif st.session_state["authentication_status"] == None:
    st.warning('Please enter your username and password')
    st.session_state["token"] = ""