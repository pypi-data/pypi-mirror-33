# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings
from django.contrib.auth.models import User
from django.db.models import Sum, Count
from django.dispatch import receiver
from django.db.models.signals import post_save


# Create your models here.
def get_user_table():
    return settings.AUTH_USER_MODEL


# 获取自定义user的自定义name
def get_user_name(user):
    try:
        return getattr(user, settings.COIN_USER_NAME_FIELD)
    except:
        return None


class CoinType(models.Model):
    name = models.CharField(max_length=180, verbose_name='名称类型')
    coin = models.IntegerField(verbose_name="数量")
    info = models.CharField(max_length=180, null=True, blank=True, verbose_name='说明')
    identity = models.CharField(max_length=180, null=True, verbose_name='标识符', unique=True, help_text='此字段唯一')

    class Meta:
        app_label = 'bee_django_coin'
        db_table = 'bee_django_coin_type'
        ordering = ["id"]
        permissions = (
            ('can_manage_coin', '可以进入M币管理页'),
        )

    def __unicode__(self):
        return (self.name)

    def get_absolute_url(self):
        return reverse('bee_django_coin:coin_type_list')


# 缦币
class UserCoinRecord(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='coin_user')
    coin = models.IntegerField(verbose_name='数量', help_text='扣除填入负数')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="created_by_user", null=True)
    reason = models.CharField(max_length=180, verbose_name='原因', null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    coin_type = models.ForeignKey('bee_django_coin.CoinType', null=True, on_delete=models.SET_NULL, verbose_name='类型')

    class Meta:
        app_label = 'bee_django_coin'
        db_table = 'bee_django_coin_record'
        ordering = ["-created_at"]

    def __unicode__(self):
        return ("UserCoinRecord->reason:" + self.reason)

    def get_absolute_url(self):
        return reverse('bee_django_coin:user_record_list', kwargs={"user_id": self.user.id})

    def get_created_by_user_name(self):
        if self.created_by:
            return get_user_name(self.created_by)
        else:
            return settings.COIN_DEFAULT_NAME


class UserCoinCount(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    coin_count = models.IntegerField(default=0)

    class Meta:
        app_label = 'bee_django_coin'
        db_table = 'bee_django_coin_rank_list'
        ordering = ["-coin_count"]

    def __unicode__(self):
        return ("UserCoinCount->user:" + self.coin_count.__str__())

    @classmethod
    def update(cls, user):
        user_record = UserCoinRecord.objects.filter(user=user).aggregate(sum_coin=Sum("coin"))
        try:
            user_count = cls.objects.get(user=user)
        except:
            user_count = cls()
            user_count.user = user
        user_count.coin_count = user_record["sum_coin"]
        user_count.save()

        return


# 增加记录后，自动更新用户总M币数量
@receiver(post_save, sender=UserCoinRecord)
def create_user(sender, **kwargs):
    user_record = kwargs['instance']
    if kwargs['created']:
        UserCoinCount.update(user_record.user)
    return
