# -*- coding: utf-8 -*-
"""
Created on Fri Dec 25 20:34:08 2020

@author: jzsja
"""
import pandas as pd
import datetime
import logging
import time
from telegram import Bot
import json

pd.options.mode.chained_assignment = None


global user

user = json.loads(open('creds.json', 'r').read().rstrip())



def myround(x, base=100):
    return int(base * round(float(x)/base))

def Algo_logger():
    logging.basicConfig(filename="logs"+"//"+'st_'+str(datetime.datetime.now().date())+'.txt', filemode='a',format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',datefmt='%H:%M:%S',level=logging.INFO)  
    logger=logging.getLogger()
    return logger

def bot(msg):
    bot = Bot(token=user['bot_token'])
    bot.send_message(user['chat_id'],msg)

    return bot



def holiday_finder():
    xday = str(datetime.datetime.now().date())
    zday = datetime.datetime.now().strftime("%A")
    yday = xday[-2:]+xday[4:-2]+xday[:4]# 0 = Monday, 1=Tuesday, 2=Wednesday...
    trading_holidays={'26-01-2021','11-03-2021','29-03-2021','02-04-2021','14-04-2021','21-04-2021','13-05-2021','21-07-2021','19-08-2021','10-09-2021','15-10-2021','05-11-2021','19-11-2021'}
    if ((yday in trading_holidays)|(zday in ['Saturday','Sunday'])):
        return 'halt'
    return 'trade'


def get_options_strikes(al_df_mgr,ltp):
    et_scripts = al_df_mgr['scripts']
    t_scripts = et_scripts[et_scripts.strike == ltp]
    ce_strike = t_scripts[t_scripts['optionType'].str.endswith('CE')]
    pe_strike = t_scripts[t_scripts['optionType'].str.endswith('PE')]
    print(ce_strike['strike'].iloc[0],ce_strike['optionType'].iloc[0])
    print(pe_strike['strike'].iloc[0],pe_strike['optionType'].iloc[0])
    return ce_strike['instrumentToken'].iloc[0],pe_strike['instrumentToken'].iloc[0]


def get_options_strike(al_df_mgr,ltp,op_type):
    et_scripts = al_df_mgr['scripts']
    t_scripts = et_scripts[et_scripts.strike == ltp]
    cp_strike = t_scripts[t_scripts['optionType'].str.endswith(op_type)]
    print(cp_strike['strike'].iloc[0])
    return cp_strike['instrumentToken'].iloc[0]


def get_rules():
    
    tday = datetime.datetime.now().date().strftime("%A")
    
    df = pd.read_excel("tbs_rules.xlsx")
    df = df[df.Day==tday]

    
    return df


def get_etimes(alpha):
    et = list(alpha.entry_time)
    
    temp = []
    
    for i in range(len(et)):
        x=et[i]
        y = x.split(',')
        temp.append([int(y[0]),int(y[1])])
        
        
    return temp
    
    
def get_pnl(al_mgr):
    client = al_mgr['client']
    
    try:
        response_json = client.positions(position_type = "TODAYS")
        df_kotak_position = pd.DataFrame.from_dict(response_json['Success'])
        
        pnl = 0
        for i in df_kotak_position.index:
            if int(df_kotak_position['netTrdQtyLot'].loc[i]) != 0 :
                
                
                quote = client.quote(instrument_token=int(df_kotak_position['instrumentToken'].loc[i]))
                ltp= float(quote['success'][0]['ltp'])
                
                if df_kotak_position['netTrdQtyLot'].loc[i] > 0 :
                    mtm = ( float(ltp ) - float(df_kotak_position['averageStockPrice'].loc[i]) ) * abs(df_kotak_position['netTrdQtyLot'].loc[i])
                if df_kotak_position['netTrdQtyLot'].loc[i] < 0 :
                    mtm = (float(df_kotak_position['averageStockPrice'].loc[i]) - float(ltp) ) * abs(df_kotak_position['netTrdQtyLot'].loc[i])
                    pnl = round(pnl + ( mtm ),2)
                df_kotak_position.at[i,"ltp"] = ltp
                df_kotak_position.at[i,"mtm"] = mtm
                
                
        try:
            pnl = df_kotak_position['mtm'].sum()
        except:
            pnl = 0
            
        pnl = round(pnl + df_kotak_position['realizedPL'].sum(),2)
        return pnl
        
    except:
        return 0
    
    
    
    
    
    
    
    
    
    
    
    
    

