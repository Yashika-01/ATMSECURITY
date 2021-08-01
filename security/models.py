from django.db import models

# Create your models here.

class ATM(models.Model):
    name = models.CharField(max_length=100)
    cardno = models.CharField(max_length=16)
    pin = models.CharField(max_length=4)