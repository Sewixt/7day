from django.db import models

# Create your models here.



class Goods_type(models.Model):
    type_label = models.CharField(max_length=254)
    type_description = models.TextField()



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

class Goods(models.Model):
    goods_num = models.CharField(max_length=32)
    goods_name = models.CharField(max_length=254)
    goods_price = models.FloatField()
    goods_count = models.IntegerField()
    goods_location = models.CharField(max_length=254)
    goods_safedate = models.IntegerField()
    goods_pro_time = models.DateField(auto_now=True)
    goods_status = models.IntegerField()  #0为下架  1为上架

    picture = models.ImageField(upload_to='seller/images',default="seller/images/default_photo.jpg")
    goods_type = models.ForeignKey(to=Goods_type,on_delete=models.CASCADE,default=1)
    goods_store = models.ForeignKey(to=Login_user,on_delete=models.CASCADE,default=1)


class Valid_Code(models.Model):
    code_content = models.CharField(max_length=32)
    code_user = models.EmailField()
    code_time = models.DateTimeField(auto_now=True)
    code_state = models.IntegerField(default=0)   #0 代表未被使用，1 代表已使用