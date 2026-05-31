from django.db import models
from datetime import date

# Create your models here.
class product(models.Model):
    CATEGORY_CHOICES = [
        ('smart', 'Smart Watch'),
        ('luxury', 'Luxury Watch'),
        ('sport', 'Sport Watch'),
        ('casual', 'Casual Watch'),
    ]
    GENDER_CHOICES = [
        ('men', 'Men'),
        ('women', 'Women'),
        ('unisex', 'Unisex'),
    ]
    STRAP_CHOICES = [
        ('leather', 'Leather'),
        ('metal', 'Metal'),
        ('silicone', 'Silicone'),
    ]
    tpcode = models.CharField(max_length=50)
    tpname = models.CharField(max_length=100)
    brand = models.CharField(max_length=100, default="Generic")
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default="smart")
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, default="unisex")
    strap_material = models.CharField(max_length=20, choices=STRAP_CHOICES, default="leather")
    tfile = models.ImageField(upload_to='images/')
    tprice = models.IntegerField()
    tstock = models.IntegerField()
    def __str__(self):
        return self.tpname

class usreg(models.Model):
    fn=models.CharField(max_length=40)
    email=models.CharField(max_length=40)
    phoneno=models.IntegerField()
    un=models.CharField(max_length=40, default='v')
    psw=models.CharField(max_length=20)
    cpws=models.CharField(max_length=20)
    rights=models.CharField(max_length=50,default='user')


class adreg(models.Model):
      un=models.CharField(max_length=40)
      psw=models.IntegerField()


class cart(models.Model):
    slno = models.IntegerField()
    pname = models.CharField(max_length=40)
    rate = models.IntegerField()
    qty = models.IntegerField()
    total = models.IntegerField()
    userid = models.IntegerField()

class onlinemaster(models.Model):
    salesno = models.IntegerField()
    salesdate = models.DateField(default=date.today)
    userid = models.IntegerField()
    uname = models.CharField(max_length=30)
    shipment= models.CharField(max_length=300)
    phone = models.CharField(max_length=10)
    cardno = models.CharField(max_length=40)
    total = models.IntegerField()
    status = models.CharField(max_length=30, default='New Order')

class onlinesub(models.Model):
    salesno = models.IntegerField()
    slno =models.IntegerField()
    pname = models.CharField(max_length=40)
    rate = models.IntegerField()
    qty = models.IntegerField()
    total = models.IntegerField()




