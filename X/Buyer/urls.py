from django.contrib import admin
from django.urls import path,re_path
from Buyer.views import *
from django.views.decorators.cache import cache_page


urlpatterns = [
    path('index/', index),
    path('register/', register),
    path('login/', login),
    path('logout/', logout),
    path('goods_list/', goods_list),
    re_path('detail/(?P<id>\d+)', detail),
]