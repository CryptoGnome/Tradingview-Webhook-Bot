## About
This is a tradingview webhook  designed to be free & open source.  This bot is written using Python & Flask and is designed to run a free heroku server. It will allow you to create custom alerts in tradingview and send them to your own private webhook server that can place trades on your account via the api.

#### Current Exchanges 
- [Bybit](https://partner.bybit.com/b/webhookbot)
- BinanceFutures(Soon)
- Binance US(Soon)
- FTX(Soon)
- FTX US(Soon)
- More will be done on request or can be added by submitting a pull request.

***Help keep this tool free by creating a new account using our referral below:***
[Create Bybit Account](https://partner.bybit.com/b/webhookbot)


# Setup Guide

Clone Project to Desktop

#Create Free Heroku Account

https://www.heroku.com/

Edit config.json to add your own api keys & add a custom key to protect the server.

Create a new project on heroku

1.) Open a terminal in the cloned directory and type:

git init

2.) Type:

heroku login

3.) After following the prompts, type:

heroku create --region eu tv-trader-(your-name)

4.) type following to push to heroku:

git add .

git commit -m "Initial Commit"

git push heroku master

5.) Any time you need to make a change to the code or the API keys, you can push a new build heroku:

git add .

git commit -m "Update"

git push heroku master

# TradingView Alerts Format

```

{

"key": "678777",

"exchange": "bybit",

"symbol": "ETHUSD",

"type": "Market",

"side": "Buy",

"qty": "1",

"price": "1120",

"close_position": "False",

"cancel_orders": "True",

"order_mode": "Both",

"take_profit_percent": "1",

"stop_loss_percent": "0.5"

}

```

//key is the unique id of the alert to protect your server, use a unique key and match it in you config.json file

//exhanges: bybit, more coming soon.

//Symbol = "SYMBOLUSD" for Inverse Pairs && "SYMBOLUSDT" for USDT Perpetual Pairs

//Side = "Buy" or "Sell"

//Type = "Market" or "Limit"

//order mode: Both, Profit, Stop

//qty is in the ticker base currency

//price is in the ticker quote currency

//close position: True or False

//cancel orders: True or False

//take profit percent: 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10

//stop loss percent: 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10
