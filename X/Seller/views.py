from django.shortcuts import render,HttpResponseRedirect
from Seller.models import *
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
                    response = HttpResponseRedirect("/Seller/index/")
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
    return render(request,"seller/login.html",locals())

#  登出页
def logout(request):
    response = HttpResponseRedirect('/Seller/login/')
    keys = request.COOKIES.keys()
    for key in keys:
        response.delete_cookie(key)
    del request.session["username"]
    return response
