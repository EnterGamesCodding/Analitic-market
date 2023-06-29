import requests
import pandas as pd
import pandas_datareader as pdr
import datetime
from difflib import SequenceMatcher as seqm

import telebot

def toFixed(numObj, digits=0):
    return f"{numObj:.{digits}f}"

def moexTIKER(name):
    url = 'https://iss.moex.com/iss/engines/stock/markets/shares/boards/TQBR/securities.json'
    response = pd.read_json(url)
    tickers = response['securities']['data']
    a = []
    for i in tickers:
        if(seqm(a=name.lower(), b=i[2].lower()).ratio() > 0.6): a.append([i[0], i[2]])

    return a


def ROC(prices, n):
    roc = ((prices[-1] - prices[-n]) / prices[-n]) * 100
    return roc


def SMA(data, window):
    if len(data) < window:
        return 0
    return sum(data[-window:]) / float(window)

    sma_pr = ((prices[-n+1])/sum(prices[-n+1:]/n))*100
    return [sma_val, sma_pr]


def main(txt):
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days=90)


    tickers = moexTIKER(txt)
    c = []
    for i in tickers:
        df = pdr.DataReader(i[0], 'moex', start_date, end_date)

        price = list(df.loc[:, 'CLOSE'])

        print(len(price))

        #try:
        sm_short = 100*(SMA(price, 7)/float(price[-1]))
        sm_long = 100*(SMA(price, 30)/float(price[-1]))
        sma = sm_short >= sm_long 

        print(sm_short, sm_long)
        sm = (sm_short-sm_long)

        if(sma): c.append(f"{i[1]}: Есть шанс, что тренд пойдет вверх:{toFixed(sm, 3)}%")
        else: c.append(f"{i[1]}: Высок шанс понижения:{toFixed(sm, 3)}%")
        #except:
        #    continue

    return c



API_TOKEN = '706951002:AAE_KZnst5UhfifnB-AfGRVoD8_BbntRZ8M'

bot = telebot.TeleBot(API_TOKEN)


# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, "Hi")

@bot.message_handler(commands=['stop']) 
def stop(message):
    bot.stop_bot()

# Handle all other messages with content_type 'text' (content_types defaults to ['text'])
@bot.message_handler(func=lambda message: True)
def echo_message(message):
    txt = moexTIKER(message.text)
    if(len(txt) == 0):
        bot.reply_to(message, "Простите, но данную компанию я не нашел")

    else:
        c = main(message.text)
        print(c)
        m = ""
        for i in c:
            bot.send_message(message.chat.id, i)



bot.infinity_polling()