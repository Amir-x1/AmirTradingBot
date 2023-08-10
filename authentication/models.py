from django.db import models


# Create your models here.
class Profile(models.Model):
    UserName = models.CharField(max_length=100)
    Exchange = models.CharField(max_length=100)
    APIName = models.CharField(max_length=100)
    APIKey = models.CharField(max_length=100)
    APISecret = models.CharField(max_length=100)
    APIPassPhrase = models.CharField(max_length=100)
    TelegramID = models.CharField(max_length=100)

    objects = models.Manager()
