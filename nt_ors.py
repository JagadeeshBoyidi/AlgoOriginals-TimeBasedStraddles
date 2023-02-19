'''importing Logger and telegram bot'''
from nt_aft import Algo_logger,bot
logger = Algo_logger()
import time

 
def place_order(al_mgr,scrip_code,quantity,ordertype,limitPrice=0,stopPrice=0):
    client = al_mgr['client']
    logger.info(f'{scrip_code} with {quantity} being placed')
    try:
        res = client.place_order(order_type = "N", instrument_token = scrip_code, transaction_type = ordertype,\
                               quantity = quantity, price = stopPrice, disclosed_quantity = 0, trigger_price = 0, tag = "at")       						
        logger.info(res)
                    
            
    except Exception as e:
        logger.error(e)
        code = "at: Error in kotak_algo place_order" 
        print(code)
        bot(code)
        return  code
       
    
def place_sl_order(al_mgr,token,quantity,trans_type,trigger_price,price):
    client = al_mgr['client']
    logger.info(f'{token} sl order with {quantity} being placed')

    try:
        res = client.place_order(order_type = "N", instrument_token =int(token), transaction_type = trans_type,\
                               quantity = int(quantity),trigger_price = int(trigger_price),price = int(price))       						
        logger.info(res)
                                
    except Exception as e:
        logger.error(e)
        code = "at: Error in kotak_algo place_sl_order" 
        print(code)
        bot(code)
        return  code
    

def cancel_order(al_mgr,orderId):
    client = al_mgr['client']   
  
    try:
        res = client.cancel_order(order_id = orderId)
        logger.info(res)

    except Exception as e:
        logger.error(e)
        code = "at: Error in kotak cancel  order" 
        print(code)
        bot(code)

        return  code
    
