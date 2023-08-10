from django.urls import path
from . import views
from .views import TraderView, StartEngineView, EngineSetupView
from django.views.decorators.csrf import csrf_exempt

urlpatterns = [
    path('', TraderView.as_view(), name="trader"),
    path('start-engine', csrf_exempt(StartEngineView.as_view()), name="start-engine"),
    path('engine-setup', csrf_exempt(EngineSetupView.as_view()), name="engine-setup"),
]
