#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django.conf.urls import include, url
from . import views

app_name='bee_django_coin'

urlpatterns = [
    url(r'^test$', views.test, name='test'),
    url(r'^$', views.CoinTypeList.as_view(), name='index'),
    # =======发金币类型========
    url(r'^type/list$', views.CoinTypeList.as_view(), name='coin_type_list'),
    # url(r'^message/detail/(?P<pk>[0-9]+)$', views.CoinTypeDetail.as_view(), name='coin_type_detail'),
    url(r'^type/add/$', views.CoinTypeCreate.as_view(), name='coin_type_add'),
    url(r'^type/update/(?P<pk>[0-9]+)/$', views.CoinTypeUpdate.as_view(), name='coin_type_update'),
    url(r'^type/delete/(?P<pk>[0-9]+)/$', views.CoinTypeDelete.as_view(), name='coin_type_delete'),
    # =======发送记录========
    url(r'^user/record/list/(?P<user_id>[0-9]+)/$', views.UserRecordList.as_view(), name='user_record_list'),
    url(r'^user/record/add/(?P<user_id>[0-9]+)/$', views.UserRecordCreate.as_view(), name='coin_record_add'),
    # =======金币排行榜=======
    url(r'^user/rank/list/$', views.UserRankList.as_view(), name='user_rank_list'),
    # url(r'^user/record/click$', views.UserRecordClick.as_view(), name='user_record_click'),

]
