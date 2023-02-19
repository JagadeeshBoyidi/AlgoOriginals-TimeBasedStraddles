# -*- coding: utf-8 -*-
"""
Created on Wed Dec 23 22:33:40 2020

@author: jzsja
"""
import time
import datetime
import pickle
from nt_aft import Algo_logger,bot
logger = Algo_logger()

import json
from ks_api_client import ks_api
import pandas as pd

import requests
from hyper.contrib import HTTP20Adapter






def et_login():
    try:
        user = json.loads(open('creds.json', 'r').read().rstrip())

        client = ks_api.KSTradeApi(access_token = user["access_token"], userid = user['userid'],\
                        consumer_key = user['consumer_key'], ip = "127.0.0.1", app_id = "")
            
        client.login(password = user['password'])
        
            
        headers = {
            'accept': 'application/json',
            'oneTimeToken': client.one_time_token,
            'consumerKey': client.consumer_key,
            'ip': 'test',
            'appId': 'test',
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+client.access_token,
        }
        data = '{"userid": "'+client.userid+'"}'
        response = requests.post(client.host+'/session/1.0/session/2FA/oneTimeToken', headers=headers, data=data)
        client.session_token=response.json()['success']['sessionToken']

        
        return client

    except:
        code = "nt: Error in kotak_login" 
        bot(code) 
        print(code)
        time.sleep(30)
        et_login()
        return  code
    
    

def get_funds(client):
    
    user = json.loads(open('creds.json', 'r').read().rstrip())
    header_params = {}
    header_params['consumerKey'] = user['consumer_key']  
    header_params['sessionToken'] = client.session_token  
    body_params = None
    header_params['Authorization'] = "Bearer "+user['access_token']
    
    s = requests.session()
    s.mount('https://', HTTP20Adapter())
    res = s.get("https://tradeapi.kotaksecurities.com/apim/margin/1.0/margin",data=body_params,  headers=header_params)
       
    res = res.json()
    
    if "Success" in res:
        if "equity" in res["Success"]:
            eq = res["Success"]["equity"]
            if (len(eq) >0):
                if 'cash' in eq[0]:
                    if "marginAvailable" in eq[0]['cash']:
                        return round(float(res["Success"]["equity"][0]["cash"]["availableCashBalance"]),2)



def get_login():
    
    try:
        with open("cns"+"//"+"et_token_kotak_jb_"+str(datetime.datetime.now().date())+'.pkl', 'rb') as input:
            client = pickle.load(input)
    except:
        client = et_login()
        # with open("cns"+"//"+"et_token_kotak_jb_"+str(datetime.datetime.now().date())+'.pkl',  'wb') as output:  # Overwrites any existing file.
        #     pickle.dump(client, output, pickle.HIGHEST_PROTOCOL)
        
    return client








    
def download_dt_scripts():
    
    
    xday = datetime.datetime.now().date()
    
    
    if xday.day<10:
        s_day = str(0)+str(xday.day)
    else:
        s_day = str(xday.day)
        
    if xday.month<10:
        s_month = str(0)+str(xday.month)
    else:
        s_month = str(xday.month)   
        
    scripts_date = str(s_day)+'_'+str(s_month)+'_'+str(xday.year)
    
    
    url = "https://preferred.kotaksecurities.com/security/production/TradeApiInstruments_FNO_"+scripts_date+".txt"
    logger.info(url)
    try:
        dv_scripts = pd.read_csv("cns"+"//"+'nt_kotak_scripts_'+str(datetime.datetime.now().date())+'.csv')
    except:
    
        try:
            dv_scripts = pd.read_csv(url, sep="|")
            dv_scripts.to_csv("cns"+"//"+'nt_kotak_scripts_'+str(datetime.datetime.now().date())+'.csv')
        except:
            download_dt_scripts()
    logger.info('scripts done')

    return dv_scripts



def get_scripts(algo_sym)  :
    
    df =  download_dt_scripts()
    df = df[(df.segment == 'FO')&(df.instrumentName ==algo_sym)]
    df['exchange_token']= df['exchangeToken'].copy()
    df['expiry'] = pd.to_datetime(df['expiry'])
    exp = list(set(df['expiry']))
    exp.sort()
    exp = list(filter(lambda x: x >=pd.Timestamp(datetime.datetime.now().date()), exp))
    et_scripts = df[(df['expiry']  ==exp[0])]
    
    return et_scripts


