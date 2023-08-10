from django.contrib import admin
from trader.models import EngineSetup
from .models import Profile

admin.site.register(EngineSetup)
admin.site.register(Profile)
# Register your models here.
