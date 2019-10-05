from django.shortcuts import render,HttpResponseRedirect
from Seller.models import *
from Buyer.models import *
from django.http import JsonResponse
from django.core.paginator import Paginator
# Create your views here.



# 装饰器   cookie，session清除
def loginValid(fun):
    def inner(request,*args,**kwargs):
        cookie_username = request.COOKIES.get("name")
        session_username = request.session.get("username")
        if cookie_username and session_username and cookie_username == session_username:
            return fun(request,*args,**kwargs)
        else:
            return HttpResponseRedirect("/Seller/login/")
    return inner

import hashlib
def setpassword(password):
    md5 = hashlib.md5()
    md5.update(password.encode())
    result = md5.hexdigest()
    return result

#######index
@loginValid
def index(request):
    return render(request,"seller/index.html",locals())


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
    return render(request,"seller/register.html",locals())




import time,datetime
#### 登录
def login(request):
    error_message = ""
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        code = request.POST.get("valid_code")
        if email:
            #   判断数据库中是否有email
            user = Login_user.objects.filter(email=email).first()
            if user:
                db_password = user.password
                password = setpassword(password)
                if db_password == password:
                    #检测验证码
                    #获取验证码
                    codes = Valid_Code.objects.filter(code_user=email).order_by("-code_time").first()
                    #效验验证码是否存在，是否过期，是否被使用
                    now = time.mktime(datetime.datetime.now().timetuple())
                    db_time = time.mktime(codes.code_time.timetuple())
                    t = (now - db_time)/60
                    if codes and codes.code_state == 0 and t <=5 and codes.code_content.upper() == code.upper():
                        response = HttpResponseRedirect("/Seller/index/")
                        response.set_cookie("name",user.username)
                        response.set_cookie("id",user.id)
                        request.session["username"] = user.username
                        return response
                    else:
                        error_message = "验证码错误"
                else:
                    error_message = "密码错误"
            else:
                 error_message = "用户不存在"
        else:
            error_message = "邮箱不能为空"
    return render(request,"seller/login.html",locals())
#  登出页
def logout(request):
    response = HttpResponseRedirect('/Seller/login/')
    keys = request.COOKIES.keys()
    for key in keys:
        response.delete_cookie(key)
    del request.session["username"]
    return response



import random
def random_code(len=6):
    """生成6位验证码"""
    string = "1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    valid_code = "".join([random.choice(string) for i in range(len)])
    return valid_code


import smtplib
from email.mime.text import MIMEText
def Send_Email(send_email):
    # 构建邮件格式
    subject = "老子的邮件"
    content = send_email
    sender = "icfyou@163.com"
    recver = """icfyou@163.com,
    1801687395@qq.com"""
    password = "123456a"
    message = MIMEText(content, "plain", "utf-8")
    # 内容
    # 内容类型
    # 编码格式
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = recver
    # 发送邮件
    smtp = smtplib.SMTP_SSL("smtp.163.com", 994)
    smtp.login(sender, password)
    smtp.sendmail(sender, recver.split(",\n"), message.as_string())
    # 发送人
    # 接收人  需要是个列表【】
    # 发送邮件  as_string 是一种类似json的封装方式，目的是为了在协议上传输邮件内容
    smtp.close()


#保存验证码
from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def send_login_code(request):
    result = {
        "code":200,
        "data":""
    }
    if request.method == "POST":
        email = request.POST.get("email")
        code = random_code()
        c = Valid_Code()
        c.code_user = email
        c.code_content = code
        c.save()
        send_email = "%s的验证码是%s，打死都不要告诉别人zyb屌毛"%(email,code)
        Send_Email(send_email)
        result["data"] = "发送成功"
    else:
        result["code"] = 400
        result["data"] = "请求错误"
    return JsonResponse(result)


def goods_add(request):
    goods_type_list = Goods_type.objects.all()
    if request.method == "POST":
        data = request.POST
        tupi = request.FILES
        print(data)

        goods = Goods()
        goods.goods_num = data.get('goods_num')
        goods.goods_name = data.get('goods_name')
        goods.goods_price = data.get('goods_price')
        goods.goods_count = data.get('goods_count')
        goods.goods_location = data.get('goods_location')
        goods.goods_safedate = data.get('goods_safedate')
        goods.goods_pro_time = data.get('goods_pro_time')   #时间格式为    yyyy-mm-dd
        goods.goods_status = 1

        #保存外键类型
        goods_type_id = int(data.get('goods_type'))
        goods.goods_type = Goods_type.objects.get(id = goods_type_id)

        #保存图片
        picture = tupi.get("picture")
        goods.picture = picture

        #  保存对应的卖家
        user_id = request.COOKIES.get("id")
        goods.good_store = Login_user.objects.get(id = int(user_id))

        goods.save()
    return render(request,"seller/goods_add.html",locals())

######商品分页操作
def goods_list(request,status,page=1):  #传入操作（0or1）    页码page默认值为1
    page = int(page)
    if status == "1":
        goodses = Goods.objects.filter(goods_status=1)  #显示status为1 的商品
    elif status == "0":
        goodses = Goods.objects.filter(goods_status=0)    #显示status为0 的商品
    else :
        goodses = Goods.objects.all()     #显示所有的商品
    allgoods = Paginator(goodses,10)        #分页显示商品  10行个一页
    goods_list = allgoods.page(page)
    return render(request,"seller/goods_list.html",locals())

####商品上下架
def goods_status(request,state,id):
    id = int(id)    #
    goods = Goods.objects.get(id=id)
    if state == "up":     #上架
        goods.goods_status = 1
    elif state =="down":    #下架
        goods.goods_status = 0
    goods.save()    #保存
    url =request.META.get("HTTP_REFERER","/Seller/goods_list/1/1")   #获取当前请求页面的url  否则返回（，）逗号后面的路由
    return HttpResponseRedirect(url)


def change_order(request):
    #通过订单详情id来锁定订单详情
    order_id = request.GET.get("order_id")
    #获取需要修改的状态
    order_status = request.GET.get("order_status")
    order = OrderInfo.objects.get(id = order_id)
    order.order_status = int(order_status)
    order.save()
    return JsonResponse({"data":"修改成功"})


def order_list(request,status):
    status = int(status)
    user_id = request.COOKIES.get("id")  #获取店铺id
    store = Login_user.objects.get(id=user_id)  #获取店铺信息
    store_order = store.orderinfo_set.filter(order_status = status).order_by("-id")     #获取店铺对应的订单
    return render(request, "seller/order_list.html", locals())