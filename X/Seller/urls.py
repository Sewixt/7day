"""Login URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,re_path
from Seller.views import *

urlpatterns = [
    path('register/', register),
    path('login/', login),
    path('index/', index),
    path('logout/', logout),
    path('slc/', send_login_code),
    path('goods_add/', goods_add),
    path('goods_list/', goods_list),
    re_path(r'goods_list/(?P<page>\d+)/(?P<status>[0,1])/', goods_list),
    re_path(r'goods_status/(?P<state>\w+)/(?P<id>\d+)/', goods_status),
    path('change_order/',change_order),
    re_path(r'order_list/(?P<status>\d{1})',order_list)
]
