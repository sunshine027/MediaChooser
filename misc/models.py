#! /usr/bin/env python
#coding=utf-8

from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic

# 所属行业
class Industry(models.Model):
    c_name = models.CharField('行业名称', max_length=30, help_text='行业中文名称')
    e_name = models.CharField('Industry Name', max_length=50, help_text='行业英文名称')
    desc = models.TextField('Description', blank=True, null=True, help_text='行业描述')
    class Meta:
        verbose_name = '所属行业'
        verbose_name_plural = '所属行业'
    
    def __unicode__(self):
        return self.c_name

# 影响地域 
class GeographicInfo(models.Model):
    c_name = models.CharField('地名', max_length=30, help_text='中文地名')
    desc = models.TextField('Description', blank=True, null=True, help_text='地域描述')
    class Meta:
        verbose_name = '影响地域'
        verbose_name_plural = '影响地域'

    def __unicode__(self):
        return self.c_name
    

# 联系人
class Contact(models.Model):
    c_name = models.CharField('名字', max_length=20, help_text='联系人中文名')
    e_name = models.CharField('英文名', max_length=20, help_text='联系人英文名', blank=True, null=True)
    department = models.CharField('所属部门/频道', max_length=50, help_text='所属部门/频道')
    position = models.CharField('职务', max_length=50, help_text='联系人职务', blank=True, null=True)
    SEX_CHOICES = (('male', '男'),('female', '女'),)
    sex = models.CharField('性别', max_length=6, choices=SEX_CHOICES, help_text='联系人性别')
    tel = models.CharField('Tel', max_length=25, help_text='电话', blank=True, null=True)
    fax = models.CharField('Fax', max_length=25, help_text='传真', blank=True, null=True)
    mobile = models.CharField('Mobile', max_length=11, help_text='手机', blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    msn = models.CharField(max_length=50, help_text='MSN', blank=True, null=True)
    qq = models.CharField(max_length=15, help_text='QQ', blank=True, null=True)

    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = '联系人'
        verbose_name_plural = '联系人'
    
    def __unicode__(self):
        return self.c_name

# 公司
class Company(models.Model):
    c_name = models.CharField('公司名称', max_length=30, help_text='公司中文名称')
    e_name = models.CharField('公司名称', max_length=30, help_text='公司英文名称', null=True)
    #industry = models.ForeignKey(Industry)
    if_client = models.BooleanField('是否电众客户', help_text='是否电众客户')   #True as default.
    desc = models.TextField('公司描述', blank=True, help_text='公司描述', null=True)

    class Meta:
        verbose_name = 'Company'
        verbose_name_plural = 'Company'

    def __unicode__(self):
        return self.c_name

# 品牌

# 产品

# 竞品
