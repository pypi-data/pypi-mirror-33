# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models
from django.core.urlresolvers import reverse
from django.conf import settings

ACTIVITY_SHOW_TYPE_CHOICES = ((1, '全部显示'), (2, "指定用户显示"))


class Activity(models.Model):
    name = models.CharField(max_length=180, verbose_name='活动名称')
    link_name = models.CharField(max_length=180, verbose_name='链接文字')
    source_id = models.IntegerField(null=True, blank=True, verbose_name='渠道id', help_text='crm中对应渠道id')
    source_name = models.CharField(max_length=180, verbose_name='渠道名称', null=True, blank=True)
    start_date = models.DateTimeField(null=True, blank=True, verbose_name='开始时间')
    end_date = models.DateTimeField(null=True, blank=True, verbose_name='结束时间')
    detail = models.TextField(verbose_name='活动说明', null=True, blank=True)
    info = models.TextField(verbose_name='分享说明', null=True, blank=True)
    show_type = models.IntegerField(verbose_name='显示类型', choices=ACTIVITY_SHOW_TYPE_CHOICES, default=1)
    explain = models.TextField(verbose_name='规则解释', null=True, blank=True)
    # ===二维码===
    qrcode_width = models.IntegerField(verbose_name='二维码宽度', null=True, blank=True, default=0)
    qrcode_height = models.IntegerField(verbose_name='二维码高度', null=True, blank=True, default=0)
    qrcode_pos_x = models.IntegerField(verbose_name='二维码x轴坐标', null=True, blank=True, default=0)
    qrcode_pos_y = models.IntegerField(verbose_name='二维码y轴坐标', null=True, blank=True, default=0)
    qrcode_color = models.CharField(max_length=8, verbose_name='二维码颜色', default='#000000', null=True)
    qrcode_bg = models.ImageField(verbose_name='二维码', upload_to='bee_django_referral/qrcode/bg', null=True, blank=True)
    qrcode_thumb = models.CharField(verbose_name='二维码预览图', max_length=180, null=True, blank=True)
    qrcode_url = models.CharField(verbose_name='二维码地址', max_length=180, null=True, blank=True)

    class Meta:
        db_table = 'bee_django_referral_activity'
        app_label = 'bee_django_referral'

    def __unicode__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('bee_django_referral:activity_detail', kwargs={"pk": self.id.__str__()})

    def get_show_type(self):
        if self.show_type==1:
            return '全部显示'
        if self.show_type==2:
            return '指定用户显示'


class UserShareImage(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.SET_NULL, null=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    qrcode = models.ImageField(verbose_name='二维码', upload_to='bee_django_referral/user_qrcode/')
    created_at = models.DateTimeField(verbose_name='生成时间', auto_now_add=True)
    status = models.IntegerField(default=0, verbose_name='状态')
    timestamp = models.BigIntegerField(default=0, verbose_name='时间戳')

    class Meta:
        db_table = 'bee_django_referral_image'
        app_label = 'bee_django_referral'

    def __unicode__(self):
        return self.user.name + ':' + self.timestamp.__str__()


class UserQrcodeRecordStatus:
    reg = 1
    pay = 2


class UserShareImageRecord(models.Model):
    user_share_image = models.ForeignKey(UserShareImage)
    preuser_id = models.IntegerField(verbose_name='crm中preuser的id')
    status = models.IntegerField(default=0, verbose_name='状态')
    created_at = models.DateTimeField(verbose_name='时间', auto_now_add=True)

    class Meta:
        db_table = 'bee_django_referral_record'
        app_label = 'bee_django_referral'

    def __unicode__(self):
        return self.user_share_image.qrcode + ',status:' + self.status.__str__()


class UserActivity(models.Model):
    activity = models.ForeignKey(Activity, verbose_name='转介活动')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)

    class Meta:
        db_table = 'bee_django_referral_user_activity'
        app_label = 'bee_django_referral'
        unique_together = ("activity", "user")

    def __unicode__(self):
        return self.user + ',activity:' + self.activity.name
