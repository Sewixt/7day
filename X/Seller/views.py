from django.shortcuts import render,HttpResponseRedirect
from Seller.models import *
from django.http import JsonResponse
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
