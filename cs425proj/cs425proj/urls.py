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
    path('account/checkout_confirm_account/', views.checkout_confirm_account, name='account'),
    path('logout/', views.logout, name='account'),
    path('admin/', admin.site.urls),
]
