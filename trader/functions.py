
import numpy as np
import telegram
from authentication.models import Profile
from kucoin_futures.client import Market, TradeData, UserData
import time
from django.conf import settings

client = Market(url='https://api-futures.kucoin.com')
tradData = TradeData(url='https://api-futures.kucoin.com')
userData = UserData(url='https://api-futures.kucoin.com')
bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)


def getCandles(symbol, timeFrame, N):
    try:
        candles = []
        FSTime = client.get_server_timestamp()
        j = 0
        while True:
            N = N - j * 200
            STime = FSTime - (60000 * N * timeFrame)
            if N <= 0:
                break
            j = + 1
            candles = candles + client.get_kline_data(symbol, timeFrame, STime)
        return candles
    except Exception as error:
        # bot.sendMessage(chat_id=224147512, text="getCandles:  " + str(error))
        print("An exception occurred at getCurrentPrice:", error)


def getCurrentPrice(symbol):
    try:
        return float(client.get_ticker(symbol)['price'])
    except Exception as error:
        # bot.sendMessage(chat_id=224147512, text="getCurrentPrice:  " + str(error))
        print("An exception occurred at getCurrentPrice:", error)


def ma(symbol, timeFrame, L):
    candles = np.array(getCandles(symbol=symbol, timeFrame=timeFrame, N=L))
    maxPrice = candles[:, 2]
    minPrice = candles[:, 3]
    MA = np.mean(maxPrice + minPrice) / 2
    return MA


def crossOver(symbol, timeFrame, line):
    candles = np.array(getCandles(symbol=symbol, timeFrame=timeFrame, N=5))
    lastCandle = candles[len(candles) - 1]
    secondLastCandle = candles[len(candles) - 2]
    if lastCandle[4] > line > secondLastCandle[4]:
        return True


def crossUnder(symbol, timeFrame, line):
    candles = np.array(getCandles(symbol=symbol, timeFrame=timeFrame, N=5))
    lastCandle = candles[len(candles) - 1]
    secondLastCandle = candles[len(candles) - 2]
    if lastCandle[4] < line < secondLastCandle[4]:
        return True


def findPosition(symbol, timeFrame, verticalOffset):
    # ma240 = ma(symbol=symbol, timeFrame=timeFrame, L=240)
    # ma80 = ma(symbol=symbol, timeFrame=timeFrame, L=80)
    # if ma240 < ma80 and crossUnder(symbol=symbol, timeFrame=timeFrame, line=ma80):  # take short position
    #
    #     return 'SHORT'
    #
    # elif ma80 < ma240 and crossOver(symbol=symbol, timeFrame=timeFrame, line=ma80):  # take long position
    #
    #     return 'LONG'
    #
    # else:
    #
    #     return None
    downVerticalOffset = 1-verticalOffset/100
    upVerticalOffset = 1+verticalOffset/100
    ma80 = ma(symbol=symbol, timeFrame=timeFrame, L=80)
    if crossOver(symbol=symbol, timeFrame=timeFrame, line=ma80*upVerticalOffset):  # take short position

        return 'LONG'

    elif crossUnder(symbol=symbol, timeFrame=timeFrame, line=ma80*downVerticalOffset):  # take long position

        return 'SHORT'

    else:

        return None


def order(side, symbol, amount, leverage, username, TP, SL):
    # initial data ------------------------------------------------#
    profile = Profile.objects.get(UserName=username)
    tradData.passphrase = profile.APIPassPhrase
    tradData.secret = profile.APISecret
    tradData.key = profile.APIKey
    userData.passphrase = profile.APIPassPhrase
    userData.secret = profile.APISecret
    userData.key = profile.APIKey
    TelegramID = profile.TelegramID
    TP = float(TP)
    SL = float(SL)
    # contract detail --------------------------------------------- #
    symbolInfo = client.get_contract_detail(symbol=symbol)
    lotSize = float(symbolInfo['lotSize'])
    tickSize = float(symbolInfo['tickSize'])
    indexPriceTickSize = float(symbolInfo['indexPriceTickSize'])
    multiplier = float(symbolInfo['multiplier'])
    roundSize = lotSize*multiplier
    decimals = indexPriceTickSize/tickSize
    userTotalEquity = userData.get_account_overview('USDT')['accountEquity']
    rawSize = ((userTotalEquity * amount / 100) * leverage) / (getCurrentPrice(symbol) * roundSize)
    size = round(rawSize / decimals) * decimals
    print(size)
    # send market order -------------------------------------------- #
    while True:
        try:
            Order = tradData.create_market_order(symbol=symbol, side=side, lever=leverage, size=size)
            orderId = Order['orderId']
            orderDetails = tradData.get_order_details(orderId=orderId)
            orderPrice = float(orderDetails['value'])/(size*multiplier)
            orderPrice = getCurrentPrice(symbol)
            LongSL = orderPrice*(1-(SL/100)/leverage)
            ShortSL = orderPrice*(1+(SL/100)/leverage)
            print('ssssss', ShortSL)
            t = time.asctime()
            bot.sendMessage(chat_id=TelegramID, text=telegram.Emoji.LARGE_BLUE_CIRCLE.decode() + " Got a " + side + " position: \n" +
                                                     "Symbol: " + symbol + "\n" +
                                                     "Price: " + str(orderPrice) + "\n" +
                                                     "Leverage: " + str(leverage) + "\n" +
                                                     "Time: " + t)
            break
        except Exception as error:
            print("An exception occurred at sending order:", error)
            continue
    # SL and TP start ---------------------------------------------- #

    while True:
        try:
            time.sleep(4)
            currentPrice = getCurrentPrice(symbol)
            if side == "buy":
                newLongSL = currentPrice*(1-(TP/100)/leverage)
                if newLongSL > orderPrice:
                    LongSL = max(LongSL, newLongSL)
                if currentPrice < LongSL:
                    closeThePosition = tradData.create_market_order(symbol=symbol, closeOrder=True)
                    closeOrderId = closeThePosition['orderId']
                    closeOrderDetails = tradData.get_order_details(orderId=closeOrderId)
                    closeOrderPrice = float(closeOrderDetails['value']) / (size * multiplier)
                    t = time.asctime()
                    bot.sendMessage(chat_id=TelegramID, text=telegram.Emoji.LARGE_RED_CIRCLE.decode()+" Position Closed: \n" +
                                                             "Price: " + str(closeOrderPrice) + "\n" +
                                                             "Profit: " + str(
                        leverage*100*(closeOrderPrice - orderPrice) / orderPrice) + "\n" +
                                                             "New Equity: " + str(
                        round(userData.get_account_overview('USDT')['accountEquity'], 2)) + "\n" +
                                                             "Time: " + t)
                    break
            else:
                newShortSL = currentPrice*(1+(TP/100)/leverage)
                if newShortSL < orderPrice:
                    ShortSL = min(ShortSL, newShortSL)
                if currentPrice > ShortSL:
                    closeThePosition = tradData.create_market_order(symbol=symbol, closeOrder=True)
                    closeOrderId = closeThePosition['orderId']
                    closeOrderDetails = tradData.get_order_details(orderId=closeOrderId)
                    closeOrderPrice = float(closeOrderDetails['value']) / (size * multiplier)
                    t = time.asctime()
                    bot.sendMessage(chat_id=TelegramID, text=telegram.Emoji.LARGE_RED_CIRCLE.decode()+" Position Closed: \n" +
                                                             "Price: " + str(closeOrderPrice) + "\n" +
                                                             "Profit: " + str(
                        leverage*100*(orderPrice-closeOrderPrice) / orderPrice) + "\n" +
                                                             "New Equity: " + str(
                        round(userData.get_account_overview('USDT')['accountEquity'], 2)) + "\n" +
                                                             "Time: " + t)
                    break
        except Exception as error:
            print("An exception occurred at closeThePosition:", error)
            continue

    print(orderDetails)
    return 'Position opened and closed'


