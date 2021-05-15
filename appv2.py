import datetime
import json
import numpy as np
import requests
import pandas as pd
from copy import deepcopy
from fake_useragent import UserAgent
from pushbullet.pushbullet import PushBullet
from configparser import ConfigParser

numdays = 7
DIST_ID = '170'

config_object = ConfigParser()
config_object.read("config.ini")
auth = config_object["AUTH"]["api_key"]
print(auth)
p = PushBullet(auth)

def load_mapping(): 
    df = pd.read_csv("district_mapping.csv")
    return df

def filter_column(df, col, value):
    df_temp = deepcopy(df.loc[df[col] == value, :]) 
    return df_temp

def filter_capacity(df, col, value):
    df_temp = deepcopy(df.loc[df[col] > value, :])
    return df_temp

mapping_df = load_mapping() 

valid_states = list(np.unique(mapping_df["state_name"].values))


base = datetime.datetime.today()
date_list = [base + datetime.timedelta(days=x) for x in range(numdays)]
date_str = [x.strftime("%d-%m-%Y") for x in date_list]

temp_user_agent = UserAgent()
browser_header = {'User-Agent': temp_user_agent.random}

final_df = None
for INP_DATE in date_str:
    URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={}&date={}".format(DIST_ID, INP_DATE)
    response = requests.get(URL, headers=browser_header)
    if (response.ok) and ('centers' in json.loads(response.text)):
        resp_json = json.loads(response.text)['centers']
        if (resp_json is not None):
            for mydistrictcenters in resp_json:
                if(((mydistrictcenters['pincode']==370205) or (mydistrictcenters['pincode']==370201))):
                    for availablesessions in mydistrictcenters['sessions']:
                        if((availablesessions['min_age_limit']==18) and (availablesessions['available_capacity']==0)):
                            text = 'Vaccine Unavailable'
                            body = 'Go back to sleep'
                        else:
                            text = 'Vaccine Available'
                            body = 'GO GO GO!!!'
        else:
            st.error("No rows in the data Extracted from the API")

p.pushNote(p.getDevices()[0]["iden"], text, body)
