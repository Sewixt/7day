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