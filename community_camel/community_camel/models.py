from django.db import models

class Accounts(models.Model):
    emailId = models.EmailField(primary_key=True)
    password = models.SlugField()
    phoneNum = models.SlugField()
    firstName = models.SlugField()
    lastName = models.SlugField()
    dob = models.DateField()
    address = models.SlugField()
    suit = models.SlugField()
    city = models.SlugField()
    province = models.SlugField()
    country = models.SlugField()
    cardNum = models.SlugField()
    ccv = models.IntegerField()
    cardExpMonth = models.IntegerField()
    cardExpYear = models.IntegerField()

class OrderList(models.Model):
    orderNo = models.IntegerField(primary_key=True)
    numItems = models.IntegerField()
    status = models.SlugField()
    date = models.DateField()
    type = models.SlugField()
    donation = models.BooleanField()
    orderAdd = models.SlugField()
    city = models.SlugField()
    emailId = models.EmailField()

class OrderItem(models.Model):
    id = models.AutoField(primary_key=True)
    orderNumber = models.IntegerField()
    itemName = models.SlugField()
    quantity = models.IntegerField()
    itemStatus = models.SlugField()
    driverEmail = models.EmailField()
    cost = models.FloatField()
    orderFileName = models.FileField()
    orderOpen = models.BooleanField()
    orderPending = models.BooleanField()
    orderClosed = models.BooleanField()