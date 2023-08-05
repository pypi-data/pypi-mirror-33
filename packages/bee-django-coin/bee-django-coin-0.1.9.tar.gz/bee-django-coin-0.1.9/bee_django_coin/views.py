#!/usr/bin/env python
# -*- coding:utf-8 -*-
from __future__ import unicode_literals

import json
from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.decorators import method_decorator
from .decorators import cls_decorator, func_decorator
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Sum, Count
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from .models import CoinType, UserCoinRecord, UserCoinCount
from .forms import CoinTypeForm, UserCoinRecordForm
from django.contrib.auth import get_user_model
from django.contrib import messages

from .utils import get_user_name, get_default_name


# Create your views here.
# =======course=======
def test(request):
    from exports import add_coin_record
    from django.contrib.auth.models import User
    to_user = User.objects.all().first()
    res = add_coin_record(to_user=to_user, coin_type_id=2, reason='test', created_by=to_user)
    print(res)
    return


@method_decorator(cls_decorator(cls_name='CoinTypeList'), name='dispatch')
class CoinTypeList(ListView):
    template_name = 'bee_django_coin/coin_type/coin_type_list.html'
    context_object_name = 'coin_type_list'
    paginate_by = 20
    queryset = CoinType.objects.all()


# @method_decorator(cls_decorator(cls_name='MessageDetail'), name='dispatch')
# class CoinTypeDetail(DetailView):
#     model = Message
#     template_name = 'bee_django_message/message/message_detail.html'
#     context_object_name = 'message'


@method_decorator(cls_decorator(cls_name='CoinTypeCreate'), name='dispatch')
class CoinTypeCreate(CreateView):
    model = CoinType
    form_class = CoinTypeForm
    template_name = 'bee_django_coin/coin_type/coin_type_form.html'


@method_decorator(cls_decorator(cls_name='CoinTypeUpdate'), name='dispatch')
class CoinTypeUpdate(UpdateView):
    model = CoinType
    form_class = CoinTypeForm
    template_name = 'bee_django_coin/coin_type/coin_type_form.html'


@method_decorator(cls_decorator(cls_name='CoinTypeDelete'), name='dispatch')
class CoinTypeDelete(DeleteView):
    model = CoinType
    success_url = reverse_lazy('bee_django_coin:coin_type_list')

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


# 发金币记录
@method_decorator(cls_decorator(cls_name='UserRecordList'), name='dispatch')
class UserRecordList(ListView):
    template_name = 'bee_django_coin/record/user_record_list.html'
    context_object_name = 'record_list'
    paginate_by = 20
    queryset = None

    def get_user(self):
        user_id = self.kwargs["user_id"]
        try:
            user_table = get_user_model()
            user = user_table.objects.get(id=user_id)
        except:
            user = None
        return user

    def get_queryset(self):
        self.queryset = UserCoinRecord.objects.filter(user=self.get_user())
        return self.queryset

    def get_context_data(self, **kwargs):
        user = self.get_user()
        context = super(UserRecordList, self).get_context_data(**kwargs)
        context['name'] = get_user_name(user)
        context['default_name'] = get_default_name
        return context


# 发M币，增加一条记录
class UserRecordCreate(CreateView):
    model = UserCoinRecord
    form_class = UserCoinRecordForm
    template_name = 'bee_django_coin/record/form.html'

    def get_user(self):
        return get_object_or_404(get_user_model(), pk=self.kwargs["user_id"])

    def get_context_data(self, **kwargs):
        context = super(UserRecordCreate, self).get_context_data(**kwargs)
        user = self.get_user()
        context['name'] = get_user_name(user)
        return context

    def form_valid(self, form):
        if not self.request.user.has_perm('bee_django_coin.add_usercoinrecord'):
            messages.error(self.request, '没有权限')
            return super(UserRecordCreate, self).form_valid(form)
        user_record = form.save(commit=False)
        user = self.get_user()
        user_record.user = user
        user_record.created_by = self.request.user
        user_record.save()
        return super(UserRecordCreate, self).form_valid(form)


class UserRankList(ListView):
    template_name = 'bee_django_coin/rank/list.html'
    context_object_name = 'user_list'
    paginate_by = 100
    queryset = UserCoinCount.objects.all()

    def get_context_data(self, **kwargs):
        context = super(UserRankList, self).get_context_data(**kwargs)
        context['title'] = "M币排行榜"
        return context
