from django.db import models

# Create your models here.
from Seller.models import *
class PayOrder(models.Model):
    """订单编号/订单日期/订单状态(未支付,已支付,待发货,待收货,完成,拒收)/订单总价/订单用户"""
    order_number = models.CharField(max_length=32)
    order_date = models.DateTimeField(auto_now=True)
    order_total = models.FloatField(blank=True,null=True)
    order_user = models.ForeignKey(to=Login_user,on_delete=models.CASCADE)

class OrderInfo(models.Model):
    """订单的编号,商品的id,商品的图片,商品的名称,商品购买的数量,商品的单价,商品小计,店铺id"""
    """
        订单详情表
        订单状态
        0 未支付
        1 已支付
        2 待收货
        3/4 完成/拒收
        """
    order_id = models.ForeignKey(to=PayOrder,on_delete=models.CASCADE)
    goods_id = models.IntegerField()
    goods_picture = models.CharField(max_length=32)
    goods_name = models.CharField(max_length=32)
    goods_count = models.IntegerField()
    goods_price = models.FloatField()
    goods_total_price = models.FloatField()
    order_status = models.IntegerField(default=0)
    store_id = models.ForeignKey(to=Login_user,on_delete=models.CASCADE)
