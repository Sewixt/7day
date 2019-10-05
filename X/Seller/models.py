from django.db import models

# Create your models here.

class Login_user(models.Model):
    email = models.EmailField()
    password = models.CharField(max_length=32)
    username = models.CharField(max_length=32, blank=True, null=True)
    phonenumber = models.CharField(max_length=32, blank=True, null=True)
    adress = models.TextField(max_length=254, blank=True, null=True)
    photo = models.ImageField(upload_to='images',default="seller/images/default_photo.jpg")

    QQ = models.IntegerField(blank=True, null=True)
    hoby = models.CharField(max_length=254, blank=True, null=True)

    user_type = models.IntegerField(default=0)    #  0为买家，1为店家，2为管理员