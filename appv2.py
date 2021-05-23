import datetime
import json
import numpy as np
import requests
import logging
from fake_useragent import UserAgent
from pushbullet.pushbullet import PushBullet
from configparser import ConfigParser
import shelve
import os

logging.basicConfig(filename="/home/roark/AutoAccessCowin/cowin-vaccination-slot-availabilityv2/newfile.log", format='%(asctime)s %(message)s', filemode='a')
logger=logging.getLogger()
logger.setLevel(logging.INFO)

if(os.path.exists("/home/roark/AutoAccessCowin/cowin-vaccination-slot-availabilityv2/PreviousAvailabilityShelf")):
    shelf = shelve.open("/home/roark/AutoAccessCowin/cowin-vaccination-slot-availabilityv2/PreviousAvailabilityShelf", writeback = True)
else:
    shelf = shelve.open("/home/roark/AutoAccessCowin/cowin-vaccination-slot-availabilityv2/PreviousAvailabilityShelf", writeback = True)
    shelf['previousavailability'] = False

numdays = 7
DIST_ID = '170'

config_object = ConfigParser()
config_object.read("config.ini")
auth = config_object["AUTH"]["api_key"]
print(auth)
p = PushBullet(auth)

base = datetime.datetime.today()
date_list = [base + datetime.timedelta(days=x) for x in range(numdays)]
date_str = [x.strftime("%d-%m-%Y") for x in date_list]

temp_user_agent = UserAgent()
browser_header = {'User-Agent': temp_user_agent.random}

for INP_DATE in date_str:
    URL = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id={}&date={}".format(DIST_ID, INP_DATE)
    response = requests.get(URL, headers=browser_header)
    if (response.ok) and ('centers' in json.loads(response.text)):
        resp_json = json.loads(response.text)['centers']
        if (resp_json is not None):
            for mydistrictcenters in resp_json:
                if(((mydistrictcenters['pincode']==370205) or (mydistrictcenters['pincode']==370201))):
                    for availablesessions in mydistrictcenters['sessions']:
                        logger.info(" : Records Fetched")
                        if((availablesessions['min_age_limit']==18) and (availablesessions['available_capacity']==0)):
                            currentavailability = False
                        else:
                            currentavailability = True
        else:
            logger.info(" : No rows in the data Extracted from the API")


if(shelf['previousavailability'] != currentavailability):
    shelf['previousavailability'] = currentavailability
    if(currentavailability == True):
        text = 'Vaccine Available'
        body = 'GO GO GO!!!'
    else:
        text = 'Vaccine Unavailable'
        body = 'Go back to sleep'  
    p.pushNote(p.getDevices()[0]["iden"], text, body)
shelf.close()