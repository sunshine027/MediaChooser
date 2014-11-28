#! /usr/bin/env python
#coding=utf-8

from django import forms
from MediaChooser.NielsenMedia.models import *
from django.contrib.admin import widgets

def _get_weeks():
    from django.db import connection
    cursor = connection.cursor()
    qs = cursor.execute('SELECT DISTINCT week FROM "NielsenMedia_nielsenoverlap" ORDER BY "week" DESC')
    qs = cursor.fetchall()
    weeks = [(str(q[0]).split(' ')[0],str(q[0]).split(' ')[0]) for q in qs]
    return weeks
    
class NielsenRankForm(forms.ModelForm):
    
    #category = forms.ModelChoiceField('ss',queryset=NielsenCategory.objects.all())
    #NielsenCategory = forms.ModelChoiceField('ss', queryset=NielsenCategory.objects.all())
    #category = forms.ChoiceField(choices=(('-','-'),))
    category = forms.ModelChoiceField(label='Category', queryset=NielsenCategory.objects.filter(parent=None))
    media = forms.ModelChoiceField(label='Media', queryset=NielsenMedia.objects.all())
    week = forms.DateField(label='week', widget=widgets.AdminDateWidget)
    province = forms.ModelChoiceField(label='province', queryset=Province.objects.all())

    class Meta:
        model = NielsenTrafficData
        #exclude = ('responsible_user', 'create_time', 'last_modified', 'can_modify')
        
class NielsenOverlapForm(forms.ModelForm):
    
    category_base = forms.ModelChoiceField(label='Category', queryset=NielsenCategory.objects.filter(parent=None))
    category_comp = forms.ModelChoiceField(label='Category', queryset=NielsenCategory.objects.filter(parent=None))
    
    weeks = _get_weeks()
    week = forms.ChoiceField(label='week', choices= weeks)
    
    class Meta:
        model = NielsenOverlap
        
class NielsenTrafficForm (forms.ModelForm):

    category = forms.ModelChoiceField(label='Category', queryset=NielsenCategory.objects.filter(parent=None))
    weeks = _get_weeks()
    week_start = forms.ChoiceField(label='week', choices= weeks)
    week_end = forms.ChoiceField(label='week', choices= weeks)
    class Meta:
        model = NielsenTrafficData
        