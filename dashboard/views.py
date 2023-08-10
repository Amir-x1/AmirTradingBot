from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from kucoin_futures.client import Market
import time


# Create your views here.
try:
    @login_required(login_url='login')
    def dashboard(request):
        username = None
        if request.user.is_authenticated:
            username = request.user.username
        return render(request, 'dashboard/index.html', {'username': username})
except Exception as error:
    print("An exception occurred at dashboard:", error)
