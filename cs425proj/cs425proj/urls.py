"""cs425proj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, re_path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    re_path(r'^shop/(?P<siteid>[0-9]{5})/$', views.shop, name='shop'),
    re_path(r'^shop/(?P<siteid>[0-9]{5})/(?:page-(?P<page>\d+)/)$', views.shop, name='shop'),
    re_path(r'^shop/(?P<siteid>[0-9]{5})/addToCart/$', views.cart, name='cart'),
    re_path(r'^shop/(?P<siteid>[0-9]{5})/cart/$', views.cart, name='cart'),
    re_path(r'^shop/(?P<siteid>[0-9]{5})/checkout/$', views.checkout, name='checkout'),
    re_path(r'^shop/(?P<siteid>[0-9]{5})/doCheckout/$', views.doCheckout, name='checkout'),
    re_path(r'^shop/(?P<siteid>[0-9]{5})/ptype/(?P<ptype>[0-9]{5})/$', views.shop, name='shop'),
    re_path(r'^shop/(?P<siteid>[0-9]{5})/ptype/(?P<ptype>[0-9]{5})/(?:page-(?P<page>\d+)/)$', views.shop, name='shop'),
    re_path(r'^shop/(?P<siteid>[0-9]{5})/manu/(?P<manu>[0-9]{5})/$', views.shop, name='shop'),
    re_path(r'^shop/(?P<siteid>[0-9]{5})/manu/(?P<manu>[0-9]{5})/(?:page-(?P<page>\d+)/)$', views.shop, name='shop'),
    re_path(r'^shop/(?P<siteid>[0-9]{5})/package/(?P<pack>[0-9]{5})/$', views.shop, name='shop'),
    re_path(r'^shop/(?P<siteid>[0-9]{5})/package/(?P<pack>[0-9]{5})/(?:page-(?P<page>\d+)/)$', views.shop, name='shop'),
    re_path(r'^order/(?P<orderid>[0-9]{7})/(?P<paycard>[0-9]{16})/$', views.orderdetail, name='order'),
    re_path(r'^order/(?P<orderid>[0-9]{7})/$', views.orderdetail, name='order'),
    path('account/orders/', views.orderlist, name='account'),
    path('account/bills/', views.bills, name='account'),
    re_path(r'^account/orders/(?:page-(?P<page>\d+)/)$', views.orderlist, name='account'),
    path('account/checkout_confirm_account/', views.checkout_confirm_account, name='account'),
    path('logout/', views.logout, name='account'),
    path('account/', views.account, name='account'),
    path('admin/', admin.site.urls),
    path('report/', views.report, name='report'),
    path('report/report1/', views.report1, name='report'),
    path('report/report2/', views.report2, name='report'),
    path('report/lowstock/', views.report_low_stock, name='report'),
    path('report/restock_100/', views.restock_100, name='report'),
    re_path(r'shop/(?P<siteid>[0-9]{5})/login/$', views.login, name='account'),
    re_path(r'shop/(?P<siteid>[0-9]{5})/doLoginOrSignup/$', views.doLoginOrSignup, name='account'),
]
