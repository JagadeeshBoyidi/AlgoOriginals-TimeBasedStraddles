'''importing Logger and telegram bot'''
from nt_aft import Algo_logger,bot,holiday_finder,get_rules,get_etimes,get_pnl
logger = Algo_logger()


'''importing pre-built modules'''
import datetime
import time

if holiday_finder() == 'halt':
    bot('Trading holiday, halting the algo')
    exit()
else:
    bot('Bot is active and running')
    
          
'''trading_symbol'''
algo_sym        ='BANKNIFTY' #underlying trading index


'''importing  scripts and tokens'''
from nt_auth import  get_scripts,get_login
scripts = get_scripts(algo_sym)
client = get_login()

'''importing custom libraries'''
from nt_ops import get_strikes,execute_orders,close_all,cancel_sl_orders

'''trading_hyper_parameters'''
base_value      = 100    #index strike difference
alpha           =  get_rules()
et = get_etimes(alpha)


quantity        = 25
idepth          = -100
ldepth           = 2000

xt=[15,6]



'''Assign the dictionary parameters'''

al_mgr      = {'algo_sym':algo_sym,'alpha':alpha, 'client':client,'idepth':idepth,'ldepth':ldepth,'base_value':base_value, 'et':et}
al_df_mgr   = {'scripts':scripts}



while True:
    if (datetime.datetime.now().time()>datetime.time(9,17)):
        break
    else:
        time.sleep(1)
        
count = 0

while True:
    
    while True:
        if (datetime.datetime.now().second == 0):
            break
        else:
            time.sleep(1)
    
    
    dtime = datetime.datetime.now().time()    
    dhour =  datetime.datetime.now().time().hour
    dmin =  datetime.datetime.now().time().minute
    

    for i in range( len(alpha)):
        hour = et[i][0]
        minute = et[i][1]
       
        if (hour == dhour)&(minute == dmin):
            al_mgr['i'] = i
            al_mgr = get_strikes(al_mgr,al_df_mgr)
            execute_orders(al_mgr)
            bot("orders has been placed")
            time.sleep(60)
            break


            
    if((dhour >=et[len(et)-1][0])&(dmin>et[len(et)-1][1]))|(dhour >et[len(et)-1][0]):
        break
    time.sleep(1)
    
    if count%3==0:
        pnl = get_pnl(al_mgr)
        bot(f'pnl : {pnl}')
        logger.info(f'pnl : {pnl}')
        print("waiting to place orders")
    count = count+1

            
count=0  
            
while True:
    dtime = datetime.datetime.now().time()    
    dhour =  datetime.datetime.now().time().hour
    dmin =  datetime.datetime.now().time().minute
    if ((dhour == xt[0])&(dmin >= xt[1]))|(dhour > xt[0]):
        cancel_sl_orders(al_mgr)
        time.sleep(1)
        close_all(al_mgr)
        break
    time.sleep(1)
        
    if count%180==5:
        pnl = get_pnl(al_mgr)
        bot(f'pnl : {pnl}')
        logger.info(f'pnl : {pnl}')
        print("waiting to exit orders")
    count = count+1

        

    
