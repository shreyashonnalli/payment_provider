from django.db import models

# Create your models here.
class Currency(models.Model):
    code = models.CharField(max_length=3, primary_key=True)
    name = models.CharField(max_length=30)
    
class Merchant(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=100)
    API_KEY = models.CharField(max_length=20)