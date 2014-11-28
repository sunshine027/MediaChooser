#! /usr/bin/env python
#coding=utf-8

from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from MediaChooser.client.models import Client

class WorkType(models.Model):
    parent = models.ForeignKey('self', verbose_name='父类', related_name='related_childs', null=True, blank=True)
    name = models.CharField('名称', max_length=20)
    desc = models.TextField('描述', blank=True, null=True, help_text='描述')
    
    class Meta:
        verbose_name = '工作类型/类别'
        verbose_name_plural = '工作类型/类别'
        
    def __unicode__(self):
        if self.parent == None:
            return self.name
        else:
            return self.parent.name + '->' + self.name
        
class Project(models.Model):
    client = models.ForeignKey(Client, verbose_name='客户', related_name='related_projects')
    name = models.CharField('项目名称', max_length='100', help_text='“比稿项目”格式——品牌+部门+时间+比稿项目名（如：安踏09年全年比稿）;“推广项目”格式——品牌+部门+时间+推广项目名（如：联想消费5月IDEAPADS10推广）;“规划工作”格式——品牌+部门+时间+规划工作名称（如：联想服务器08年全年竞品分析报告）')
    revenue = models.IntegerField('营业额', blank=True, null=True)
    profit = models.IntegerField('利润', blank=True, null=True)
    
    class Meta:
        verbose_name = '相关项目'
        verbose_name_plural = '相关项目'
        
    def __unicode__(self):
        return self.name
        
class ReportItem(models.Model):
    start_day = models.DateField('开始日期')
    end_day = models.DateField('结束日期')
    work_type = models.ForeignKey(WorkType, verbose_name='工作类型', related_name='related_reportitems')
    client = models.ForeignKey(Client, verbose_name='客户名称', related_name='related_reportitems', blank=True, null=True)
    project = models.ForeignKey(Project, verbose_name='项目名称', related_name='related_reportitems', blank=True, null=True)
    work_subtype = models.ForeignKey(WorkType, verbose_name='工作类别', related_name='related_sub_reportitems')
    desc = models.TextField('工作描述', blank=True, null=True)
    responsible_user = models.ForeignKey(User, verbose_name='负责人', related_name='related_reportitems')
    duration = models.FloatField('工作时长')
    create_time = models.DateTimeField('创建时间', auto_now_add=True, blank=True, null=True)
    last_modified = models.DateTimeField('最后修改时间', auto_now=True, blank=True, null=True)
    can_modify = models.BooleanField('可否修改', default=True)
    
    class Meta:
        verbose_name = '周报条目'
        verbose_name_plural = '周报条目'
        
    def __unicode__(self):
        return str(self.id)

class GroupLeader(models.Model):
    leader = models.ForeignKey(User, verbose_name='组长', related_name='related_group_leader')
    group = models.ForeignKey(Group, verbose_name='组', related_name='related_group')
    
    class Meta:
        verbose_name = '组长'
        verbose_name_plural = '组长'

    def __unicode__(self):
        return str(self.id)
