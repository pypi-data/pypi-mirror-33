# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json, qrcode, os, shutil, urllib
from django.shortcuts import get_object_or_404, reverse, redirect, render
from django.views.generic import ListView, DetailView, TemplateView
from django.db.models import Q, Sum, Count
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from django.utils.datastructures import MultiValueDict
from django.contrib import messages
from django.http import HttpResponse
from django.conf import settings
from django.utils.six import BytesIO
from django.apps import apps
from django.contrib.auth import get_user_model
from django.utils.decorators import method_decorator
from django import forms

from .decorators import cls_decorator, func_decorator
from .models import Activity, UserActivity
from .utils import save_user_qrcode_img, get_now_timestamp, get_now
from .forms import ActivityForm, ActivityUpdateForm, ActivityQrCodeImgUpdateForm, ActivityQrCodeUpdateForm, \
    UserActivityForm
from .qr import create_qrcode, merge_img, toRgb
from .exports import get_user_qrcode

User = get_user_model()


# Create your views here.

def test(request):
    return


# ========Activity===========
@method_decorator(cls_decorator(cls_name='ActivityList'), name='dispatch')
class ActivityList(ListView):
    model = Activity
    template_name = 'bee_django_referral/activity/activity_list.html'
    context_object_name = 'activity_list'
    paginate_by = 20
    ordering = ["-start_date"]


@method_decorator(cls_decorator(cls_name='ActivityDetail'), name='dispatch')
class ActivityDetail(DeleteView):
    model = Activity
    template_name = 'bee_django_referral/activity/activity_detail.html'
    context_object_name = 'activity'


@method_decorator(cls_decorator(cls_name='SourceCreate'), name='dispatch')
class ActivityCreate(CreateView):
    model = Activity
    form_class = ActivityForm
    template_name = 'bee_django_referral/activity/activity_form.html'


@method_decorator(cls_decorator(cls_name='ActivityUpdate'), name='dispatch')
class ActivityUpdate(UpdateView):
    model = Activity
    form_class = ActivityUpdateForm
    template_name = 'bee_django_referral/activity/activity_form.html'

    # def get_context_data(self, **kwargs):
    #     context = super(ActivityUpdate, self).get_context_data(**kwargs)
    #     context["activity"] = Activity.objects.get(id=self.kwargs["pk"])
    #     return context


@method_decorator(cls_decorator(cls_name='ActivityQrcodeUpload'), name='dispatch')
class ActivityQrcodeUpload(UpdateView):
    model = Activity
    form_class = ActivityQrCodeImgUpdateForm
    template_name = 'bee_django_referral/activity/activity_qrcode_upload_form.html'

    def get_success_url(self):
        return reverse_lazy('bee_django_referral:activity_qrcode_update', kwargs=self.kwargs)


@method_decorator(cls_decorator(cls_name='ActivityQrcodeUpdate'), name='dispatch')
class ActivityQrcodeUpdate(UpdateView):
    model = Activity
    form_class = ActivityQrCodeUpdateForm
    template_name = 'bee_django_referral/activity/activity_qrcode_form.html'

    def get_success_url(self):
        return reverse_lazy('bee_django_referral:activity_qrcode_update', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super(ActivityQrcodeUpdate, self).get_context_data(**kwargs)
        # context["img_form"] = ActivityQrCodeImgUpdateForm
        context["timestamp"] = get_now_timestamp().__str__()
        return context

    def form_valid(self, form):
        #     # This method is called when valid form data has been POSTed.
        #     # It should return an HttpResponse.
        activity = form.save(commit=True)
        ret = save_user_qrcode_img(activity_id=activity.id, user_id='', timestamp=0, url=activity.qrcode_url)
        if ret:
            activity.qrcode_thumb = ret
            activity.save()
        return super(ActivityQrcodeUpdate, self).form_valid(form)


# =======User Activity =======

class UserActivityCreate(CreateView):
    model = UserActivity
    form_class = UserActivityForm
    template_name = 'bee_django_referral/user/activity/form.html'

    def get_success_url(self):
        return reverse_lazy('bee_django_referral:user_activity_list', kwargs=self.kwargs)

    def get_context_data(self, **kwargs):
        context = super(UserActivityCreate, self).get_context_data(**kwargs)
        user = User.objects.get(id=self.kwargs["user_id"])
        context["user"] = user
        return context

    def form_valid(self, form):
        #     # This method is called when valid form data has been POSTed.
        #     # It should return an HttpResponse.
        user_activity = form.save(commit=False)
        user = User.objects.get(id=self.kwargs["user_id"])
        user_activity.user = user
        user_activity.save()
        return super(UserActivityCreate, self).form_valid(form)


class UserActivityList(TemplateView):
    template_name = 'bee_django_referral/user/activity/list.html'

    def get_context_data(self, **kwargs):
        context = super(UserActivityList, self).get_context_data(**kwargs)
        user = User.objects.get(id=self.kwargs["user_id"])
        context["user"] = user
        activity_list = Activity.objects.filter(show_type=1)
        user_activity_list = UserActivity.objects.filter(user=user).exclude(activity__in=activity_list)
        context["activity_list"] = activity_list
        context["user_activity_list"] = user_activity_list
        return context


class UserActivityDelete(DeleteView):
    model = UserActivity
    success_url = reverse_lazy('bee_django_referral:poster_list')
    # success_url = reverse_lazy('bee_django_crm:poster_list',kwargs={'pk': question_id})

    def get_success_url(self):
        user_activity = UserActivity.objects.get(pk=self.kwargs["pk"])
        user = user_activity.user
        return reverse_lazy('bee_django_referral:user_activity_list', kwargs={'user_id': user.id})

    def get(self, request, *args, **kwargs):
        return self.http_method_not_allowed(request, *args, **kwargs)


@method_decorator(cls_decorator(cls_name='UserActivityDetail'), name='dispatch')
class UserActivityDetail(DetailView):
    model = Activity
    template_name = 'bee_django_referral/user/activity/detail.html'
    context_object_name = 'activity'

    # def get_context_data(self, **kwargs):
    #     context = super(UserActivityDetail, self).get_context_data(**kwargs)
    #     user = None
    #     activity_id=self.kwargs["activity_id"]
    #     user_qrcode_list = get_user_qrcode(user,activity_id=activity_id)
    #     return context


# =======User Activity =======
@method_decorator(cls_decorator(cls_name='PreuserReg'), name='dispatch')
class PreuserReg(TemplateView):
    template_name = 'bee_django_referral/reg/preuser_from.html'

    def get_context_data(self, **kwargs):
        context = super(PreuserReg, self).get_context_data(**kwargs)
        activity_id = self.kwargs["activity_id"]
        now = get_now()
        error_message = None
        try:
            activity = Activity.objects.get(id=activity_id)
            if now < activity.start_date:
                error_message = '活动未开始'
            elif activity.end_date < now:
                error_message = '活动已结束'
        except:
            error_message = "发生错误"
        context["error_message"] = error_message
        context["activity_id"] = activity_id
        return context
