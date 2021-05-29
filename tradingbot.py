'''
This code uses Binance API to create Buy and Sell orders based on EMA_10 and EMA_50 Indicators. Every line has comments above to explain it's use
Project Start Date: May 4th 2021
Project First Release: May 17th 2021
Project Updated: May 29th 2021
'''
#imports websocket library to connect to Binance websocket for Price data
import websocket
#imports json library for printing websocket data
import json
#imports pprint library for printing API data
import pprint
#imports config.py where API Key and Secret are stored
import config
#imports time library to create delays
import time
#imports binance API's
from binance.client import Client
from binance.enums import *
#imports datetime to make sure bot does not lag
from datetime import datetime
#imports exeptions incase bot fails to complete order
from binance.exceptions import BinanceAPIException
from binance.exceptions import BinanceOrderException

#creates list named "closes" where last close was stored (needed to calculate EMA) 
closes = []

#previous EMA should bereplaced here everytime before starting bot
Previous_EMA_10 = []
Previous_EMA_50 = []

#Connects to the asset bought and sold
TRADE_SYMBOL = 'ETHUSDT'

#socket stream. can be updated for different coins, trade types, and charts 
SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_5m"

#connects to binance account api for buying, selling and checkingaccount related info
client = Client(config.API_KEY, config.API_SECRET)

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
    
    #gives the time of receiving message
    print("received message at", Current_time)
    
    #loads received information into a json message
    json_message = json.loads(message)
    #pprint.pprint(json_message)

    #gets user's USDT balance, converts it to float, and prints it out every 2 seconds
    USDTbal = (client.get_asset_balance(asset='USDT'))
    USDTbalance= float(USDTbal['free'])
    print("your USDT balance is currently:", USDTbalance)

    #gets user's ETH balance, convers it to float and prints it every 2 seconds
    ETHbal = (client.get_asset_balance(asset='ETH'))
    ETHbalance = float(ETHbal['free'])
    print("your ETH balance is currently: ", ETHbalance)

    #gets current price of ETH and prints it out every 2 seconds
    avg_price = (client.get_avg_price(symbol='ETHUSDT'))
    symbol_price = float(avg_price['price'])
    print("The current price of 1 ETH is: ", symbol_price)
    
    #creates a quantity for the bot to buy and sell using balance
    BUY_QUANTIY = round(((USDTbalance - 0.02) / symbol_price), 5)
    SELL_QUANTITY = round((ETHbalance), 5)
    
    candle = json_message["k"]

    #checks in candle is closed
    is_candle_closed = candle["x"]
    close=candle["c"]    
    
    if is_candle_closed:
        closes.append(float(close))
        
        #prints latest closes
        print ("the latest closes are:", closes)
        
        #calculates the EMA's required for the bot to trade
        EMA_10 = round((closes[-1] * (2/(1 + 10))) + (Previous_EMA_10[-1] * (1-(2/(1+10)))), 4)
        Previous_EMA_10.append(float(EMA_10))
        EMA_50 = round((closes[-1] * (2/(1 + 50))) + (Previous_EMA_50[-1] * (1-(2/(1+50)))), 4)
        Previous_EMA_50.append(float(EMA_50))
        print("EMA_10 is: ")
        print(EMA_10)
        print("EMA_50 is: ")
        print(EMA_50)
        
        #when in uptrend (EMA 10 is bigger than EMA 50), bot buys max eth
        if EMA_10 > EMA_50:
            print ("Buy!")
            try:
                #API function to create a buy order
                print("sending order")
                buy_order = client.create_order(
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
                
        #when in a downtrend (EMA 10 smaller than EMA 50) the bot will sell max
        if EMA_10 < EMA_50:
            print("Sell!")
            try:
                #API function to sell
                print("sending order")
                buy_order = client.create_order(
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

#websocket to recieve information on prices
ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
