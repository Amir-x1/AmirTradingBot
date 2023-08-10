from django.db import models


class EngineSetup(models.Model):
    UserName = models.CharField(max_length=100)
    symbol = models.CharField(max_length=100)
    engine = models.CharField(max_length=100)
    TP = models.CharField(max_length=100, default=0)
    SL = models.CharField(max_length=100, default=0)
    verticalOffset = models.CharField(max_length=100, default=0)
    timeFrame = models.CharField(max_length=100)
    leverage = models.CharField(max_length=100)
    amount = models.CharField(max_length=100)
    EngineStarted = models.BooleanField(default=False)

    objects = models.Manager()
