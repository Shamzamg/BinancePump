"""
Created on Tuesday December 29 11:20:41 2020
@author: ZIANI Shamsdine

Buys an amount of BTCquantity of the input symbol at its average price after a Telegram signal
Auto sell
"""

#import keys
import math
import datetime
import requests
import sys
import time
from time import sleep
import webbrowser
from binance.client import Client
from telethon.sync import TelegramClient, events

url = 'https://api.binance.com/api/v1/ticker/price?symbol='

api_id = 123456
api_hash = 'yourapiHash'
phone_number = +123456789
name = 'telegramPump'
chatName = 'ShamsTest'

BinanceClient = Client("username", "password")
BTCquantity = '0.001'

securityCoef = 1.2
sellCoef = 1.2

client = TelegramClient(name, api_id, api_hash).start()


@client.on(events.NewMessage(chats=(chatName)))
async def my_event_handler(event):

    symbol = ''
    asset = ''

    if "Today We Push: #" in event.message.message:
        msg = event.message.message
        msg_parsed = msg.split("Today We Push: #", 1)
        msg_parsed2 = msg_parsed[1].split(" $", 1)
        asset = str(msg_parsed2[0])

    elif "There are many good coins on Binance" in event.message.message:

        msg = event.message.message
        msg_parsed = msg.split("The coin we picked today is :", 1)
        symbol = str(msg_parsed[1]).replace("👉", "")
        symbol = symbol.replace("(", "")
        symbol = symbol.replace(")", "")
        symbol = symbol.replace("👈", "")
        asset = symbol.replace(" ", "")

    elif "#" in event.message.message:
        msg = event.message.message
        msg_parsed = msg.split("#", 1)
        msg_parsed2 = msg_parsed[1].split("\n", 1)
        asset = msg_parsed2[0].replace(" ", "")

    elif "$" in event.message.message:
        msg = event.message.message
        msg_parsed = msg.split("$", 1)
        msg_parsed2 = msg_parsed[1].split("\n", 1)
        asset = msg_parsed2[0].replace(" ", "")

    else:
        asset = input("Enter the token: \n")

    symbol = asset + 'BTC'

    avgPriceSymbol = BinanceClient.get_avg_price(symbol=symbol)['price']
    quantity = str(math.floor(float(BTCquantity) / float(avgPriceSymbol)))

    buyPrice = format(securityCoef * float(avgPriceSymbol), '.8f')

    print('buyPrice: ' + str(buyPrice))

    try:
        BinanceClient.order_limit_buy(symbol=symbol, quantity=quantity, price=str(buyPrice))
        print("limit buy set")
    except Exception as e:
        try:
            buyPrice = format(securityCoef * float(avgPriceSymbol), '.7f')
            BinanceClient.order_limit_buy(symbol=symbol, quantity=quantity, price=str(buyPrice))
            print("limit buy set")
        except Exception as e:
            try:
                buyPrice = format(securityCoef * float(avgPriceSymbol), '.6f')
                BinanceClient.order_limit_buy(symbol=symbol, quantity=quantity, price=str(buyPrice))
                print("limit buy set")
            except Exception as e:
                    print(e)

    try:
        myOrders = BinanceClient.get_all_orders(symbol=symbol)
        print("got all orders")
    except Exception as e:
        print(e)

    try:
        priceWeBoughtAt = format(float(myOrders[len(myOrders) - 1]['cummulativeQuoteQty'])/float(myOrders[len(myOrders) - 1]['executedQty']), '.8f')
    except Exception as e:
        print(e)

    print('price we bought at : ' + str(priceWeBoughtAt))

    sellPrice = format(float(sellCoef) * float(priceWeBoughtAt), '.8f')

    print('sellPrice: ' + sellPrice)

    balanceInfo = BinanceClient.get_asset_balance(asset=asset)
    balance = str(balanceInfo['free'])[:-3]

    minQty = 0
    try:
        info = BinanceClient.get_symbol_info(symbol)
        minQty = info['filters'][2]['minQty']
    except Exception as e:
        print(e)

    print(asset + ' available: ' + str(balance))
    print('minQty : ' + minQty)

    quantityLotSize = str(float(balance) - float(balance)%float(minQty))

    try:
        BinanceClient.order_limit_sell(symbol=symbol, quantity=quantityLotSize, price=str(sellPrice))
        print("limit sell set")
    except Exception as e:
        try:
            sellPrice = format(float(sellCoef) * float(priceWeBoughtAt), '.7f')
            BinanceClient.order_limit_sell(symbol=symbol, quantity=quantityLotSize, price=str(sellPrice))
            print("limit sell set")
        except Exception as e:
            try:
                sellPrice = format(float(sellCoef) * float(priceWeBoughtAt), '.6f')
                BinanceClient.order_limit_sell(symbol=symbol, quantity=quantityLotSize, price=str(sellPrice))
                print("limit sell set")
            except Exception as e:
                print(e)

    webbrowser.open("https://www.binance.com/en/trade/" + symbol)

    try:
        infoSymbol = (requests.get(url + symbol)).json()
        currentPrice = infoSymbol['price']

        print('Current price: ' + str(currentPrice))
    except Exception as e:
        print(e)

    time.sleep(3)

    while currentPrice >= priceWeBoughtAt:
        infoSymbol = (requests.get(url + symbol)).json()
        currentPrice = infoSymbol['price']
        print('Current price: ' + str(currentPrice))

    try:
        myOrders = BinanceClient.get_all_orders(symbol=symbol)
        print("got all orders")
    except Exception as e:
        print(e)

    try:
        BinanceClient.cancel_order(symbol=symbol, orderId=myOrders[len(myOrders) - 1]['orderId'])
        print("order cancelled")
    except Exception as e:
        print(e)
    try:
        BinanceClient.order_market_sell(symbol=symbol, quantity=quantityLotSize)
        print("order sold")
    except Exception as e:
        print(e)

    sys.exit("End of the program")
client.run_until_disconnected()
