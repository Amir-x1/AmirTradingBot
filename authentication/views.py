from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.models import User
from .models import Profile
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
import telegram
from django.conf import settings


# Create your views here.
class LoginView(View):
    try:
        def get(self, request):
            return render(request, 'authentication/login.html')

        def post(self, request):
            username = request.POST['username']
            password = request.POST['password']

            if username and password:
                user = auth.authenticate(username=username, password=password)
                if user:
                    auth.login(request, user)
                    return redirect('dashboard/')
                messages.error(request, 'Username or password is wrong!')
                return redirect('login')
            messages.error(request, 'Please fill all fields')
            return redirect('login')
    except Exception as error:
        print("An exception occurred at LoginView:", error)


class LogoutView(View):
    try:
        @method_decorator(login_required(login_url='login'), name='dispatch')
        def post(self, request):
            auth.logout(request)
            # messages.set_level(request, None)
            messages.success(request, 'You are successfully logged out')
            return redirect('login')
    except Exception as error:
        print("An exception occurred at LogoutView:", error)


class UserSettingView(View):
    try:
        @method_decorator(login_required(login_url='login'), name='dispatch')
        def get(self, request):
            return render(request, 'authentication/user-setting.html')

        @method_decorator(login_required(login_url='login'), name='dispatch')
        def post(self, request):
            exchange = request.POST['exchange']
            apiName = request.POST['API-name']
            apiKey = request.POST['API-Key']
            apiSecret = request.POST['API-Secret']
            apiPassPhrase = request.POST['API-PassPhrase']
            username = request.user.username
            if not Profile.objects.filter(UserName=username).exists():
                profile = Profile(UserName=username)
                profile.save()
            profile = Profile.objects.get(UserName=username)
            if exchange:
                profile.Exchange = exchange
                profile.save()
            if apiName:
                profile.APIName = apiName
                profile.save()
            if apiKey:
                profile.APIKey = apiKey
                profile.save()
            if apiSecret:
                profile.APISecret = apiSecret
                profile.save()
            if apiPassPhrase:
                profile.APIPassPhrase = apiPassPhrase
                profile.save()

            return render(request, 'authentication/user-setting.html')
    except Exception as error:
        print("An exception occurred at UserSettingView:", error)


class TelegramValidationView(View):
    try:
        @method_decorator(login_required(login_url='login'), name='dispatch')
        def get(self, request):
            bot = telegram.Bot(token=settings.TELEGRAM_BOT_TOKEN)
            updates = bot.getUpdates()
            # print(bot.getUpdates()[-1].message.chat_id)
            telegramID = bot.getUpdates()[-1].message.chat_id
            username = request.user.username
            if telegramID:
                if not Profile.objects.filter(UserName=username).exists():
                    profile = Profile(UserName=username, TelegramID=telegramID)
                    profile.save()
                profile = Profile.objects.get(UserName=username)
                profile.TelegramID = telegramID
                profile.save()
                messages.success(request, 'Telegram ID saved successfully')
            return render(request, 'authentication/user-setting.html')
    except Exception as error:
        print("An exception occurred at TelegramValidationView:", error)