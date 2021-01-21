from django.db import models
from django.contrib.auth.models import User

import datetime

# Create your models here.



class Watchlist(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product_url=models.URLField(max_length = 400,null=False)
    domain = models.CharField(max_length = 30,null=False)
    product_name = models.CharField(max_length = 150,null=False)
    price = models.PositiveIntegerField(null=False)
    price_th = models.CharField(max_length = 10,null=False)
    product_pic_url = models.URLField(max_length = 250,null=False)
    availability = models.CharField(max_length=20)
    date_added = models.DateTimeField(auto_now_add=True)
    pid = models.CharField(max_length=20,null=False)


class MailingList(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    product = models.ForeignKey(Watchlist,on_delete=models.CASCADE)
    price = models.PositiveIntegerField()
    price_th = models.CharField(max_length=10)
    is_price_drop_and_avail = models.BooleanField(default=0)
    is_price_drop = models.BooleanField(default=0)
    is_avail = models.BooleanField(default=0)
    status = models.CharField(max_length=20,default="pending")
    date_added = models.DateTimeField(auto_now_add=True)