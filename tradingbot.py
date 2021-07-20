'''
This code uses Binance API to create Buy and Sell orders based on a popular and high profit strategy.
The strategy is a combination of MACD(5,13,2) on 3hr charts
Project Updated: July 20th 2021
'''
#imports websocket library to connect to Binance websocket for Price data
import websocket
#imports json library for printing websocket data
import json
#imports pprint library for printing API data
import pprint
#imports binance API
from binance.client import Client
#for time calculation
from datetime import datetime
#imports exeptions incase bot fails to complete order
from binance.exceptions import BinanceAPIException
from binance.exceptions import BinanceOrderException

#creates list named "closes" where last close was stored (needed to calculate EMA) 
closes = []

#asks user for previous EMAs and Signal Input before starting bot
Previous_EMA_5_Input = int(float((input("Enter the Latest EMA 5: "))))
Previous_EMA_13_Input = int(float((input("Enter the Latest EMA 13: "))))
Previous_Signal_Input = int(float((input("Enter the Latest Signal Line: "))))
Previous_EMA_5 = []
Previous_EMA_13 = []
Previous_signal_line = []
Previous_EMA_5.append(Previous_EMA_5_Input)
Previous_EMA_13.append(Previous_EMA_13_Input)
Previous_signal_line.append(Previous_Signal_Input)

#Connects to the asset bought and sold
TRADE_SYMBOL = 'ETHUSDT'
TRADE_ASSET = 'ETH'


#socket stream. can be updated for different coins, trade types, and charts 
SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_1m"

#connects to binance account api for buying, selling and checkingaccount related info
API_KEY = "xxxxxxxxxxxxxxxxxx"
API_SECRET = "xxxxxxxxxxxxxxxxxx"
client = Client(API_KEY, API_SECRET)
info = client.get_symbol_info(TRADE_SYMBOL)
precision = info['baseAssetPrecision']

while __name__ == "__main__":


    #prints "opened connection" upon connection to websocket
    def on_open(ws):
        print("opened connection")

    #prints "closed connection" upon cllsing connection when ending code
    def on_close(ws):
        print("closed connection")
        
    #main code where trading occurs
    def on_message(ws, message):
        
        #converts list closes to become global
        global closes
    
        #gets the current date
        now = datetime.now()
        Current_time = now.strftime("%H:%M.%S")
        utc_now = datetime.utcnow()
        utc_time = utc_now.strftime("%H:%M.%S")
        hour = int(datetime.utcnow().hour)
        min = int(datetime.utcnow().minute)
        sec = int(datetime.utcnow().second)      
        macd_minutes = 60 - min
    
        if (hour == 0) or (hour == 3) or (hour == 6) or (hour == 9) or (hour == 12) or (hour == 15) or (hour == 18) or (hour == 21) or (hour == 24):
            macd_countdown = "2 hours " + str(macd_minutes) + " minutes"
        if (hour == 1) or (hour == 4) or (hour == 7) or (hour == 10) or (hour == 13) or (hour == 16) or (hour == 19) or (hour == 22):
            macd_countdown = "1 hour " + str(macd_minutes) + " minutes"
        if (hour == 2) or (hour == 5) or (hour == 8) or (hour == 11) or (hour == 14) or (hour == 17) or (hour == 20) or (hour == 23):
            macd_countdown = str(macd_minutes) + " minutes"

    
        #gives the time of receiving message
        print("received message at", Current_time)
    
        #loads received information into a json message
        json_message = json.loads(message)
        
        avg_price = (client.get_avg_price(symbol=TRADE_SYMBOL))
        symbol_price = float(avg_price['price'])
        
        #gets user's USDT balance
        USDTbal = (client.get_asset_balance(asset='USDT'))
        USDTbalance= float(USDTbal['free'])
        print("your USDT balance is currently:", USDTbalance)

        #gets user's Trading asset balance
        TRADE_ASSET_bal = (client.get_asset_balance(asset=TRADE_ASSET))
        TRADE_ASSET_Balanace = float(TRADE_ASSET_bal['free'])
        print("your ETH balance is currently: " + str(TRADE_ASSET_Balanace) + " (=" + str(TRADE_ASSET_Balanace*symbol_price) + "USDT)")

        #gets current price of Trading asset
        print("The current price of 1 ETH is: ", symbol_price)
        print("-----------------------")
    
        #creates a quantity for the bot to buy and sell using balance
        BUY_QUANTIY = round(((USDTbalance - 0.01) / symbol_price), 8)
        SELL_QUANTITY = round((TRADE_ASSET_Balanace), precision)
    
        candle = json_message["k"]

    
        #calculates and runs strategy every 3 hours, which is the optimal time for this strategy
        if ((hour == 0) or (hour == 3) or (hour == 6) or (hour == 9) or (hour == 12) or (hour == 15) or (hour == 18) or (hour == 21) or (hour == 24)) and (min == 0) and (sec == 0 or sec == 1 or sec == 2):
        
            close=candle["c"]    
            closes.append(float(close))
        
            #prints latest closes
            print ("the latest closes are:", closes)

            #!--Main Trading Strategy--!#
            EMA_5 = round((closes[-1] * (2/(1 + 5))) + (Previous_EMA_5[-1] * (1-(2/(1+5)))), 4)
            Previous_EMA_5.append(float(EMA_5))
            EMA_13 = round((closes[-1] * (2/(1 + 13))) + (Previous_EMA_13[-1] * (1-(2/(1+13)))), 4)
            Previous_EMA_13.append(float(EMA_13))
            macd = (EMA_5 - EMA_13)
            signal_line = round((macd * (2/(1 + 2))) + (Previous_signal_line[-1] * (1-(2/(1+2)))), 4)
            Previous_signal_line.append(signal_line)
            print("EMA_5 is: ")
            print(EMA_5)
            print("EMA_13 is: ")
            print(EMA_13)
            print("MACD line is: " + str(macd))
            print("Signal line is: " + str(signal_line))
        
            #when in uptrend bot buys max eth
            if macd > signal_line:
                print ("Buy!")
                try:
                    #API function to create a buy order
                    print("sending order")
                    buy_order = client.create_test_order(
                        symbol=TRADE_SYMBOL, 
                        side='BUY', 
                        type='MARKET', 
                        quantity=BUY_QUANTIY)
                    print (buy_order)

                except BinanceAPIException as e:
                    # error handling goes here
                    print(e)
                except BinanceOrderException as e:
                    # error handling goes here
                    print(e)
       
            #when in a downtrend the bot will sell max
            if macd < signal_line:
                print("Sell!")
                try:
                    #API function to sell
                    print("Sending order")
                    buy_order = client.create_test_order(
                        symbol=TRADE_SYMBOL, 
                        side='SELL', 
                        type='MARKET', 
                        quantity=SELL_QUANTITY)
                    print (buy_order)
                except BinanceAPIException as e:
                    # error handling goes here
                    print(e)
                except BinanceOrderException as e:
                    # error handling goes here
                    print(e)
        
        else:
            print("Time till next MACD calculation is: " + str(macd_countdown))            

    #websocket to recieve information on prices
    ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
    ws.run_forever()
