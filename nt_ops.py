'''importing Logger and telegram bot'''
# import time
from nt_aft import Algo_logger,myround,bot,get_options_strike
from nt_ors import place_order,place_sl_order,cancel_order
import pandas as pd
logger = Algo_logger()


def get_strikes(al_mgr,al_df_mgr):
    
    try:
        client = al_mgr['client']
        quote = client.quote(instrument_token=11717)
        ltp = myround(float(quote['success'][0]['ltp']))
        depth = al_mgr['alpha']['depth'].iloc[al_mgr['i']]
        
        call = get_options_strike(al_df_mgr,ltp+depth,'CE')
        put = get_options_strike(al_df_mgr,ltp-depth,'PE')
                
        
        al_mgr['call']=call
        al_mgr['put']=put

    except Exception as e:
        logger.error(e)
        code = 'at: error during get_strikes'
        bot(code)         
    
    return al_mgr



def execute_orders(al_mgr):
    
    
    et = al_mgr['et']
    i = al_mgr['i']    
    alpha = al_mgr['alpha']
    alpha[['hour', 'min']] = alpha['entry_time'].str.split(',', 1, expand=True)
    alpha['hour']=alpha['hour'].apply(lambda x:int(x))
    alpha['min']=alpha['min'].apply(lambda x:int(x))
 
    beta = alpha[(alpha['hour']==et[i][0])&(alpha['min']==et[i][1])]
    print(beta)
    
    for i in range(len(beta)):
        quantity = beta['quantity'].iloc[i]
        slp = beta['sl'].iloc[i]
        print(i,quantity,slp)
        # print(quantity,slp)
    
        try:
            place_order(al_mgr,int(al_mgr['call']),int(quantity),'SELL',0,0 )
            place_order(al_mgr,int(al_mgr['put']),int(quantity),'SELL',0,0 ) 
        except Exception as e:
            logger.error(e)
            code = 'at: error during execute_orders'
            bot(code) 
            
        try:
            sl_orders(al_mgr,slp)
        except Exception as e:
            logger.error(e)
            code = 'at: error during sl_orders'
            bot(code)  
            
    return al_mgr

  
        
def close_all(al_mgr):
    client = al_mgr['client']
    try:
        
        df_open_positions = pd.DataFrame(client.positions(position_type = "TODAYS")['Success'])
        dops = df_open_positions[df_open_positions['netTrdQtyLot']<0]      


        for i in range(len(dops)):
            token               = dops['instrumentToken'].iloc[i]
            quantity            = dops['netTrdQtyLot'].iloc[i]        
            res = place_order(al_mgr,int(token),int(abs(quantity)),'BUY',limitPrice=0,stopPrice=0)
            logger.info(res)

        clearing_positions = 'at : Squaring off done for the existing kotak short positions, please check manually'
        print(clearing_positions)
        bot(clearing_positions)
            
    except:
        msg = "at: Error in kotak fun_close_short_positions" 
        logger.error(msg)
        bot(msg)
        return None
    




def sl_orders(al_mgr,slp):
    
    client = al_mgr['client']
        
    try:
        df = pd.DataFrame(client.order_report()['success'])
        df = df[df.status =='SLO']
        dop = pd.DataFrame(client.positions(position_type = "TODAYS")['Success'])
        dop = dop[dop.netTrdQtyLot<0]
        
        if ((len(df)==0)&(len(dop)==0)):
            code='at: No open positions to place sl orders'
            bot(code)
            
        elif(len(df)==0):
            for token in [al_mgr['call'],al_mgr['put']]:
                 dop_t = dop[dop.instrumentToken == token]
                 
                 if len(dop_t)>0:
                     pos_qty = abs(dop_t['netTrdQtyLot'].sum())
                     price = dop_t['averageStockPrice'].iloc[-1]
                     price = price + price*slp
                     trigger_price = price-price*0.03
                     place_sl_order(al_mgr,int(token),int(pos_qty),'BUY',round(trigger_price,1),round(price,1))
                     
        else:
            for token in (al_mgr['call'],al_mgr['put']):
                 opn_qty = abs(df[df.instrumentToken==token]['pendingQuantity'].sum())
                 pos_qty = abs(dop[dop.instrumentToken == token]['netTrdQtyLot'].sum())
                 net_qty = abs(pos_qty-opn_qty)
                 
                 if net_qty !=0:
                     price = dop[dop.instrumentToken == token]['averageStockPrice'].iloc[-1]
                     price = price + price*slp
                     trigger_price = price-price*0.03
                     place_sl_order(al_mgr,int(token),int(net_qty),'BUY',round(trigger_price,1),round(price,1))
                    
    except:
        msg = "at: Error in  kotak while placing sl order" 
        logger.error(msg)
        bot(msg)
        return None



def cancel_sl_orders(al_mgr):
    client = al_mgr['client']
    
    try:
        df = pd.DataFrame(client.order_report()['success'])
        df = df[df.status =='SLO']
        
        for i in range(len(df)):
            orderId= df['orderId'].iloc[i]
            cancel_order(al_mgr,int(orderId))

    except Exception as e:
        logger.error(e)
        msg = "at: Error in kotak cancel_sl_orders" 
        logger.error(msg)
        bot(msg)

    

# def close_long_all(al_mgr):
    
#     try:
#         kite  = al_mgr['kite']
#         res = kite.positions() 
#         df_pos = pd.DataFrame(res['net'])
#         df_open = df_pos[df_pos.quantity > 0]   
#         for i in range(len(df_open)):
#             tradingsymbol = df_open['tradingsymbol'].iloc[i]
#             quantity = abs(df_open['quantity'].iloc[i])
#             exit_order(al_mgr,tradingsymbol,quantity,'SELL',0,0 )
            
            
#     except Exception as e:
#         logger.error(e)
#         code = 'ts: error during close_long_all'
#         bot(code)
        

#     return al_mgr

     



# def get_long_strikes(al_mgr,al_df_mgr):
    
#     try:
#         kite        = al_mgr['kite']
#         sym         = "NSE:"+"NIFTY BANK"
#         x           = kite.ltp(sym)
#         ltp         = myround(x[sym]['last_price'])
#         idepth      = al_mgr['idepth']
        
#         lng_put = get_single_options_strike(al_df_mgr,prime_strike(ltp-idepth),'PE')
#         lng_call = get_single_options_strike(al_df_mgr,prime_strike(ltp+idepth),'CE')
    
        
#         al_mgr['lng_put']=lng_put
#         al_mgr['lng_call']=lng_call
#         print(lng_put,lng_call)
        
#     except Exception as e:
#         logger.error(e)
#         code = 'ts: error during get_long_strikes'
#         bot(code) 
    
#     return al_mgr


# def execute_long_orders(al_mgr):
    
#     try:
#         place_order(al_mgr,al_mgr['lng_call'],int(al_mgr['quantity'])*3,'BUY',0,0 )
#         place_order(al_mgr,al_mgr['lng_put'],int(al_mgr['quantity'])*3,'BUY',0,0 )

#     except Exception as e:
#         logger.error(e)
#         code = 'ts: error during execute_long_orders'
#         bot(code) 
#     return al_mgr

