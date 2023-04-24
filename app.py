import json
from flask import Flask, render_template, request, jsonify
from pybit import HTTP
import time
import ccxt
from binanceFutures import Bot

def validate_bybit_api_key(session):
    try:
        result = session.get_api_key_info()
        return True
    except Exception as e:
        print("Bybit API key validation failed:", str(e))
        return False

def validate_binance_api_key(exchange):
    try:
        result = exchange.fetch_balance()
        return True
    except Exception as e:
        print("Binance API key validation failed:", str(e))
        return False

app = Flask(__name__)

# load config.json
with open('config.json') as config_file:
    config = json.load(config_file)

###############################################################################
#
#             This Section is for Exchange Validation
#
###############################################################################

use_bybit = False
if 'BYBIT' in config['EXCHANGES']:
    if config['EXCHANGES']['BYBIT']['ENABLED']:
        print("Bybit is enabled!")
        use_bybit = True

    session = HTTP(
        endpoint='https://api.bybit.com',
        api_key=config['EXCHANGES']['BYBIT']['API_KEY'],
        api_secret=config['EXCHANGES']['BYBIT']['API_SECRET']
    )

use_binance_futures = False
if 'BINANCE-FUTURES' in config['EXCHANGES']:
    if config['EXCHANGES']['BINANCE-FUTURES']['ENABLED']:
        print("Binance is enabled!")
        use_binance_futures = True

        exchange = ccxt.binance({
        'apiKey': config['EXCHANGES']['BINANCE-FUTURES']['API_KEY'],
        'secret': config['EXCHANGES']['BINANCE-FUTURES']['API_SECRET'],
        'options': {
            'defaultType': 'future',
            },
        'urls': {
            'api': {
                'public': 'https://testnet.binancefuture.com/fapi/v1',
                'private': 'https://testnet.binancefuture.com/fapi/v1',
            }, }
        })
        exchange.set_sandbox_mode(True)

# Validate Bybit API key
if use_bybit:
    if not validate_bybit_api_key(session):
        print("Invalid Bybit API key.")
        use_bybit = False

# Validate Binance Futures API key
if use_binance_futures:
    if not validate_binance_api_key(exchange):
        print("Invalid Binance Futures API key.")
        use_binance_futures = False

@app.route('/')
def index():
    return {'message': 'Server is running!'}

@app.route('/webhook', methods=['POST'])
def webhook():
    print("Hook Received!")
    data = json.loads(request.data)
    print(data)

    if int(data['key']) != config['KEY']:
        print("Invalid Key, Please Try Again!")
        return {
            "status": "error",
            "message": "Invalid Key, Please Try Again!"
        }

    ##############################################################################
    #             Bybit
    ##############################################################################
    if data['exchange'] == 'bybit':

        if use_bybit:
            if data['close_position'] == 'True':
                print("Closing Position")
                session.close_position(symbol=data['symbol'])
            else:
                if 'cancel_orders' in data:
                    print("Cancelling Order")
                    session.cancel_all_active_orders(symbol=data['symbol'])
                if 'type' in data:
                    print("Placing Order")
                    if 'price' in data:
                        price = data['price']
                    else:
                        price = 0


                    if data['order_mode'] == 'Both':
                        take_profit_percent = float(data['take_profit_percent'])/100
                        stop_loss_percent = float(data['stop_loss_percent'])/100
                        current_price = session.latest_information_for_symbol(symbol=data['symbol'])['result'][0]['last_price']
                        if data['side'] == 'Buy':
                            take_profit_price = round(float(current_price) + (float(current_price) * take_profit_percent), 2)
                            stop_loss_price = round(float(current_price) - (float(current_price) * stop_loss_percent), 2)
                        elif data['side'] == 'Sell':
                            take_profit_price = round(float(current_price) - (float(current_price) * take_profit_percent), 2)
                            stop_loss_price = round(float(current_price) + (float(current_price) * stop_loss_percent), 2)

                        print("Take Profit Price: " + str(take_profit_price))
                        print("Stop Loss Price: " + str(stop_loss_price))

                        session.place_active_order(symbol=data['symbol'], order_type=data['type'], side=data['side'],
                                                   qty=data['qty'], time_in_force="GoodTillCancel", reduce_only=False,
                                                   close_on_trigger=False, price=price, take_profit=take_profit_price, stop_loss=stop_loss_price)

                    elif data['order_mode'] == 'Profit':
                        take_profit_percent = float(data['take_profit_percent'])/100
                        current_price = session.latest_information_for_symbol(symbol=data['symbol'])['result'][0]['last_price']
                        if data['side'] == 'Buy':
                            take_profit_price = round(float(current_price) + (float(current_price) * take_profit_percent), 2)
                        elif data['side'] == 'Sell':
                            take_profit_price = round(float(current_price) - (float(current_price) * take_profit_percent), 2)

                        print("Take Profit Price: " + str(take_profit_price))
                        session.place_active_order(symbol=data['symbol'], order_type=data['type'], side=data['side'],
                                                   qty=data['qty'], time_in_force="GoodTillCancel", reduce_only=False,
                                                   close_on_trigger=False, price=price, take_profit=take_profit_price)
                    elif data['order_mode'] == 'Stop':
                        stop_loss_percent = float(data['stop_loss_percent'])/100
                        current_price = session.latest_information_for_symbol(symbol=data['symbol'])['result'][0]['last_price']
                        if data['side'] == 'Buy':
                            stop_loss_price = round(float(current_price) - (float(current_price) * stop_loss_percent), 2)
                        elif data['side'] == 'Sell':
                            stop_loss_price = round(float(current_price) + (float(current_price) * stop_loss_percent), 2)

                        print("Stop Loss Price: " + str(stop_loss_price))
                        session.place_active_order(symbol=data['symbol'], order_type=data['type'], side=data['side'],
                                                   qty=data['qty'], time_in_force="GoodTillCancel", reduce_only=False,
                                                   close_on_trigger=False, price=price, stop_loss=stop_loss_price)

                    else:
                        session.place_active_order(symbol=data['symbol'], order_type=data['type'], side=data['side'],
                                                   qty=data['qty'], time_in_force="GoodTillCancel", reduce_only=False,
                                                   close_on_trigger=False, price=price)

        return {
            "status": "success",
            "message": "Bybit Webhook Received!"
        }
    ##############################################################################
    #             Binance Futures
    ##############################################################################
        if data['exchange'] == 'binance-futures':
            if use_binance_futures:
                bot = Bot()
                bot.run(data)
                return {
                    "status": "success",
                    "message": "Binance Futures Webhook Received!"
                }

        else:
            print("Invalid Exchange, Please Try Again!")
            return {
                "status": "error",
                "message": "Invalid Exchange, Please Try Again!"
            }

if __name__ == '__main__':
    app.run(debug=False)


