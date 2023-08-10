import json
from . import functions
import numpy as np
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views import View
from .models import EngineSetup
from authentication.models import Profile
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from kucoin_futures.client import Market, TradeData, UserData
import telegram
import time
from django.conf import settings

client = Market(url='https://api-futures.kucoin.com')
tradData = TradeData(url='https://api-futures.kucoin.com')
userData = UserData(url='https://api-futures.kucoin.com')
bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)


class TraderView(View):
    try:
        @method_decorator(login_required(login_url='login'), name='dispatch')
        def get(self, request):
            username = request.user.username
            if not EngineSetup.objects.filter(UserName=username).exists():
                engineSetup = EngineSetup(UserName=username)
                engineSetup.save()
            engineSetup = EngineSetup.objects.get(UserName=username)
            engineStarted = engineSetup.EngineStarted
            if engineStarted:
                engineStarted = 'Stop'
                engineStartBtnColor = '#fa0000'
            else:
                engineStarted = 'Start'
                engineStartBtnColor = '#2f9ce0'
            return render(request, 'trader/trader.html',
                          {'engineStarted': engineStarted, 'engineStartBtnColor': engineStartBtnColor})
    except Exception as error:
        print("An exception occurred at TraderView:", error)


class EngineSetupView(View):
    try:
        @method_decorator(login_required(login_url='login'), name='dispatch')
        def post(self, request):
            data = json.loads(request.body)
            symbol = data['symbol']
            engine = data['engine']
            TP = data['TP']
            SL = data['SL']
            verticalOffset = data['verticalOffset']
            timeFrame = data['timeFrame']
            leverage = data['leverage']
            amount = data['amount']
            EngineStarted = data['EngineStarted']
            if EngineStarted == 'true':
                EngineStarted = True
            elif EngineStarted == 'false':
                EngineStarted = False
            username = request.user.username
            if not EngineSetup.objects.filter(UserName=username).exists():
                engineSetup = EngineSetup(UserName=username)
                engineSetup.save()
            engineSetup = EngineSetup.objects.get(UserName=username)
            engineSetup.symbol = symbol
            engineSetup.engine = engine
            engineSetup.TP = TP
            engineSetup.SL = SL
            engineSetup.verticalOffset = verticalOffset
            engineSetup.timeFrame = timeFrame
            engineSetup.leverage = leverage
            engineSetup.amount = amount
            engineSetup.EngineStarted = EngineStarted
            engineSetup.save()
            return JsonResponse({})
    except Exception as error:
        print("An exception occurred at EngineSetupView:", error)


class StartEngineView(View):
    try:
        @method_decorator(login_required(login_url='login'), name='dispatch')
        def post(self, request):
            username = request.user.username
            profile = Profile.objects.get(UserName=username)
            tradData.passphrase = profile.APIPassPhrase
            tradData.secret = profile.APISecret
            tradData.key = profile.APIKey
            userData.passphrase = profile.APIPassPhrase
            userData.secret = profile.APISecret
            userData.key = profile.APIKey
            TelegramID = profile.TelegramID

            engineSetup = EngineSetup.objects.get(UserName=username)
            symbol = engineSetup.symbol
            timeFrame = int(engineSetup.timeFrame)
            leverage = int(engineSetup.leverage)
            amount = int(engineSetup.amount)
            TP = float(engineSetup.TP)
            SL = float(engineSetup.SL)
            verticalOffset = float(engineSetup.verticalOffset)
            print('Engine working for: ' + username)
            while True:
                try:
                    bot.sendMessage(chat_id=TelegramID, text='Engine Started \n' +
                                                                     'Your Equity is: ' + str(
                                                            round(userData.get_account_overview('USDT')['accountEquity'], 2))
                                    + '\nSymbol: ' + symbol)
                    # functions.crossUnder(symbol=symbol, timeFrame=timeFrame, line=100)
                    break
                except Exception as error:
                    print("An exception occurred at Start engine:", error)
                    break
            while True:
                time.sleep(4)
                engineSetup = EngineSetup.objects.get(UserName=username)
                EngineStarted = engineSetup.EngineStarted
                if EngineStarted:
                    try:
                        # ###################################### Main Engine ###########################################

                        position = functions.findPosition(symbol=symbol, timeFrame=timeFrame, verticalOffset=verticalOffset)
                        # position = 'SHORT'
                        if position == 'LONG':
                            print('LONG')
                            orderID = functions.order(side='buy', symbol=symbol,
                                                    amount=amount, leverage=leverage, username=username, TP=TP, SL=SL)
                            print(orderID)
                        elif position == 'SHORT':
                            print('SHORT')
                            orderID = functions.order(side='sell', symbol=symbol,
                                                      amount=amount, leverage=leverage, username=username, TP=TP, SL=SL)
                            print(orderID)
                        else:
                            pass
                    except Exception as error:
                        # bot.sendMessage(chat_id=224147512, text="EngineStarted:  " + str(error))
                        print("An exception occurred at EngineStarted:", error)
                        continue
                else:
                    break
            print('Engine Stopped for: ' + username)
            bot.sendMessage(chat_id=TelegramID, text="Engine Stopped!")
            return HttpResponse('')
    except Exception as error:
        # bot.sendMessage(chat_id=224147512, text="StartEngineView:  " + str(error))
        print("An exception occurred at StartEngineView:", error)
