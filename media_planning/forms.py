#! /usr/bin/env python
#coding=utf-8

from django import forms
from MediaChooser.media_planning.models import Flight
from MediaChooser.client.models import Client
from MediaChooser.misc.models import Industry
from MediaChooser.ad.models import ActivityType
from django.contrib.admin import widgets

class MP_SFlight_Form (forms.Form):

    campaign_id = forms.CharField()
    
class MP_MFlights_Form (forms.Form):
    
    campaign_name = forms.CharField(required=False)
    #industry = forms.ModelChoiceField(label='所属行业', queryset= Industry.objects.all())
    client = forms.ModelChoiceField(label='所属行业', required=False, queryset= Client.objects.all())
    activitytype = forms.ModelChoiceField(label='活动类型', required=False, queryset = ActivityType.objects.all())
    start_day = forms.DateField(label='开始日期', widget=widgets.AdminDateWidget, required=False)
    end_day = forms.DateField(label='结束日期', widget=widgets.AdminDateWidget, required=False)
    
class MP_MediaFilter_Form (forms.Form):
    
    start_day = forms.DateField(label='开始日期', widget=widgets.AdminDateWidget, required=False)
    end_day = forms.DateField(label='结束日期', widget=widgets.AdminDateWidget, required=False)
    
    