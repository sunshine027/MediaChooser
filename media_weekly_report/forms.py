#! /usr/bin/env python
#coding=utf-8

from django import forms
# from django.db.models import Q
from MediaChooser.media_weekly_report.models import ReportItem, WorkType, Project
from MediaChooser.client.models import Client
from django.contrib.admin import widgets

class ReportItemForm(forms.ModelForm):
    start_day = forms.DateField(label='开始日期', widget=widgets.AdminDateWidget)
    end_day = forms.DateField(label='结束日期', widget=widgets.AdminDateWidget)
    work_type = forms.ModelChoiceField(label='工作类型', queryset=WorkType.objects.filter(parent=None))
    client = forms.ModelChoiceField(required=False, label='客户名称', queryset=Client.objects.all().order_by('c_name'))
    project = forms.ModelChoiceField(required=False, label='项目名称', queryset=Project.objects.all().order_by('name'))
    work_subtype = forms.ModelChoiceField(label='工作类别', queryset=WorkType.objects.exclude(parent=None))
#    desc = forms.CharField(label='工作描述', widget=widgets.AdminTextareaWidget)
#    duration = forms.FloatField(label='工作时长')
    
    class Meta:
        model = ReportItem
        exclude = ('responsible_user', 'create_time', 'last_modified', 'can_modify')
