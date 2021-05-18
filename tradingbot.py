#imports websocket library to connect to Binance websocket for Price data
import websocket
#imports json library for printing websocket data
import json
#imports pprint library for printing API data
import pprint
#imports config.py where API Key and Secret are stored
import config
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
Previous_EMA_10 = [3325.2042]
Previous_EMA_50 = [3307.7125]

#socket stream. can be updated for different coins, trade types, and charts 
SOCKET = "wss://stream.binance.com:9443/ws/ethusdt@kline_5m"
#bool which updates after every trade to check whether in bought or sold condition
in_position = False

#connects to binance account api for buying, selling and checking account related info
client = Client(config.API_KEY, config.API_SECRET)
def on_open(ws):
    print("opened connection")
def on_close(ws):
    print("closed connection")

def on_message(ws, message):
    global closes
    now = datetime.now()
    Current_time = now.strftime("%H:%M.%S")
    print("received message")
    json_message = json.loads(message)
    #pprint.pprint(json_message)
    print("The time is: ", Current_time)

    candle = json_message["k"]

    is_candle_closed = candle["x"]
    close=candle["c"]    
    
    if is_candle_closed:
        closes.append(float(close))
        print ("closes")
        print (closes)
        print (Previous_EMA_10)
        print (Previous_EMA_50)
        EMA_10 = round((closes[-1] * (2/(1 + 10))) + (Previous_EMA_10[-1] * (1-(2/(1+10)))), 4)
        Previous_EMA_10.append(float(EMA_10))
        EMA_50 = round((closes[-1] * (2/(1 + 50))) + (Previous_EMA_50[-1] * (1-(2/(1+50)))), 4)
        Previous_EMA_50.append(float(EMA_50))
        
        print("EMA_10 is: ")
        print(EMA_10)
        print("EMA_50 is: ")
        print(EMA_50)
        
        if EMA_10 > EMA_50 and not in_position:
            print ("Buy!")
            try:
                print("sending order")
                buy_order = client.create_order(symbol='ETHUSDT', side='BUY', type='MARKET', quantity=0.00314)
                print (buy_order)
            except BinanceAPIException as e:
                # error handling goes here
                print(e)
            except BinanceOrderException as e:
                # error handling goes here
                print(e)
                
        if EMA_10 > EMA_50 and in_position:
            print ("Nothing to buy with")
        if EMA_10 < EMA_50 and not in_position:
            print ("Nothing to sell") 
        if EMA_10 < EMA_50 and in_position:
            print("Sell!")
            try:
                print("sending order")
                buy_order = client.create_order(symbol='ETHUSDT', side='SELL', type='MARKET', quantity=0.00314)
                print (buy_order)
            except BinanceAPIException as e:
                # error handling goes here
                print(e)
            except BinanceOrderException as e:
                # error handling goes here
                print(e)

ws = websocket.WebSocketApp(SOCKET, on_open=on_open, on_close=on_close, on_message=on_message)
ws.run_forever()
