from django.shortcuts import render,HttpResponseRedirect
from Seller.models import *
from Buyer.models import *
from alipay import AliPay
# Create your views here.


# 装饰器   cookie，session清除
def loginValid(fun):
    def inner(request,*args,**kwargs):
        cookie_username = request.COOKIES.get("name")
        session_username = request.session.get("username")
        if cookie_username and session_username and cookie_username == session_username:
            return fun(request,*args,**kwargs)
        else:
            return HttpResponseRedirect("/Buyer/login/")
    return inner

import hashlib
#####设置密码加密方式
def setpassword(password):
    md5=hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result


#####注册页面
def register(request):
    error_message = ""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        if email:
            #   判断数据库中是否有email
            user = Login_user.objects.filter(email=email).first()
            if not user:
                new_user = Login_user()
                new_user.email = email
                new_user.username = email
                new_user.password = setpassword(password)
                new_user.save()
            else:
                error_message = "该邮箱已被注册"
        else:
            error_message = "请输入邮箱"
    return render(request,"buyer/register.html",locals())

#### 登录
def login(request):
    error_message = ""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        if email:
            #   判断数据库中是否有email
            user = Login_user.objects.filter(email=email).first()
            if user:
                db_password = user.password
                password = setpassword(password)
                if db_password == password:
                    response = HttpResponseRedirect("/Buyer/index/")
                    response.set_cookie("name",user.username)
                    response.set_cookie("id",user.id)
                    request.session["username"] = user.username
                    return response
                else:
                    error_message = "密码错误"
            else:
                 error_message = "用户不存在"
        else:
            error_message = "邮箱不能为空"
    return render(request,"buyer/login.html",locals())


### 登出
def logout(request):
    url = request.META.get("HTTP_REFERER", "/Buyer/index/")
    response = HttpResponseRedirect(url)
    for k in request.COOKIES:
        response.delete_cookie("name")
        response.delete_cookie("id")
    del request.session["username"]
    return response


####   index
def index(request):
    goods_type = Goods_type.objects.all()   #获取所有类型
    result = []
    for ty in goods_type:
        #按照生产日期对对应类型的商品进行排序
        goods = ty.goods_set.order_by("-goods_pro_time")
        t =ty.id
        if len(goods) >= 4 :
            goods = goods[:4]
            result.append({"type":ty,"goods_list":goods})
    return render(request,"buyer/index.html",locals())

##商品列表页
def goods_list(request):
    """
    type  代表请求的类型
        t 按照类型查找
            keywords必须是类型id
        k 按照关键字查询
            keywords可以是任何东西
    keywords 代表请求的关键字
    """
    request_type = request.GET.get("type")   #获取请求的类型  t类型查询  k关键字查询
    keyword = request.GET.get("keywords")    #查询的内容 t类型 k为类型id  k类型  k为关键字
    goods_list = [ ]  #返回的结果
    if request_type == "t":  #t类型查询
        if keyword:
            id = int(keyword)
            goods_type = Goods_type.objects.get(id = id)  #先查询类型
            goods_list = goods_type.goods_set.order_by("-goods_pro_time")   #再查询类型对应的商品
    elif request_type == "k":
        if keyword:
            goods_list = Goods.objects.filter(goods_name__contains=keyword).order_by("-goods_pro_time")
    if goods_list:   # 限定推荐的条数
        lenth = len(goods_list) / 5
        if lenth != int(lenth):
            lenth +=1
        lenth = int(lenth)
        recommend = goods_list[:lenth]
    return render(request,"buyer/goods_list.html",locals())


##商品详情页
def detail(request,id):
    goods = Goods.objects.get(id=int(id))
    return render(request,"buyer/detail.html",locals())

import time
import datetime
####支付页面
@loginValid
def pay_order(request):
    goods_id = request.GET.get("goods_id")
    count = request.GET.get("count")
    if goods_id and count :
        #保存订单表,但保存总价
        order = PayOrder()
        order.order_number = str(time.time()).replace(".","")
        order.order_date = datetime.datetime.now()
        order.order_user = Login_user.objects.get(id=int(request.COOKIES.get("id")))
        order.save()
        #保存订单详情
        #查询商品的信息
        """订单的编号,商品的id,商品的图片,商品的名称,商品购买的数量,
        商品的单价,商品小计,店铺id"""
        goods = Goods.objects.get(id = int(goods_id))
        order_info = OrderInfo()
        order_info.order_id = order
        order_info.goods_id = goods_id
        order_info.goods_picture = goods.picture
        order_info.goods_name = goods.goods_name
        order_info.goods_count = int(count)
        order_info.goods_price = goods.goods_price
        order_info.goods_total_price = goods.goods_price*int(count)
        order_info.store_id = goods.goods_store  #商品卖家，goods,goods_store本身就是一条卖家数据
        order_info.save()
        order.order_total = order_info.goods_total_price
        order.save()
    return render(request,"buyer/pay_order.html",locals())


from X.settings import alipay_public_key_string,alipay_private_key_string
def AlipayViews(request):
    order_number = request.GET.get("order_number")
    order_total = request.GET.get("total")
    #实例化支付
    alipay = AliPay(
        appid="2016101200667858",
        app_notify_url=None,
        app_private_key_string=alipay_private_key_string,
        alipay_public_key_string=alipay_public_key_string,
        sign_type="RSA2"
    )
    #订单实例化
    order_string = alipay.api_alipay_trade_page_pay(
        out_trade_no= order_number,
        total_amount=str(order_total),
        subject="中公教育",
        return_url="http://127.0.0.1:8000/Buyer/payresult/",   #结果返回的地址
        notify_url="http://127.0.0.1:8000/Buyer/payresult/" #订单状态发生改变后返回的地址
    ) #网页支付订单
    #拼接收款地址 = 支付宝网关 + 订单返回参数
    result = "https://openapi.alipaydev.com/gateway.do?" + order_string
    return HttpResponseRedirect(result)


def payresult(request):
    out_trade_on = request.GET.get("out_trade_no")
    if out_trade_on:
        order = PayOrder.objects.get(order_number=out_trade_on)
        order.orderinfo_set.all().update(order_status=1)
    return render(request,"buyer/payresult.html",locals())