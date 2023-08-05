#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django import forms
from .models import CoinType,UserCoinRecord


# ===== course contract======
class CoinTypeForm(forms.ModelForm):
    class Meta:
        model = CoinType
        fields = ['name',"identity", "coin", "info"]


class UserCoinRecordForm(forms.ModelForm):
    class Meta:
        model =UserCoinRecord
        fields = ["coin","reason",'coin_type']