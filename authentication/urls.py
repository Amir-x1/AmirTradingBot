from django.urls import path
from . import views
from .views import LoginView, LogoutView, UserSettingView, TelegramValidationView


urlpatterns = [
    path('', LoginView.as_view(), name="login"),
    path('logout', LogoutView.as_view(), name="logout"),
    path('user-setting', UserSettingView.as_view(), name="user-setting"),
    path('telegram-validation', TelegramValidationView.as_view(), name="telegram-validation"),
]
