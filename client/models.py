#! /usr/bin/env python
#coding=utf-8

from django.db import models
from MediaChooser.media.models import Media
from MediaChooser.misc.models import Industry
from django.contrib.auth.models import User

# 客户，特指andc客户，享受andc服务的大客户，包括levono等
class ClientManager (models.Manager):
    def get_clients_industry(self):
        industries = []
        #for c in super(ClientManager, self).get_query_set().all():
        for c in super(ClientManager, self).get_query_set().select_related('industry'):
            if c.industry != None and c.industry.c_name not in industries:
                industries.append(c.industry.c_name)
        return industries
    '''
    def get_clients_dict(self):
        clients_dict = {}
        for i in self.get_clients_industry():
            try:
                clients_dict[i]
            except KeyError:
                clients = Client.objects.filter(industry__c_name=i)
                clients_dict[i] = list(clients)
        return clients_dict
    '''
    
    def get_clients_dict(self):
        clients_dict = {}
        clients = Client.objects.select_related('industry')
        for c in clients:
            industry_name = c.industry
            if industry_name in clients_dict:
                clients_dict[industry_name].append(c)
            else:
                clients_dict[industry_name] = []
                clients_dict[industry_name].append(c)
        
        return clients_dict
    
    def get_clients_by_industry(self, id):
        try:
            industry = Industry.objects.get(pk=id)
            return super(ClientManager, self).get_query_set().filter(industry=industry)
        except ObjectDoesNotExist:
            return None

class Client(models.Model):
    c_name = models.CharField('客户名', max_length=128, unique=True, help_text='客户中文名称')
    e_name = models.CharField('客户名(英文)', max_length=128, help_text='客户英文名称')
    desc = models.TextField('描述', help_text='描述', blank=True, null=True)
    favor_media = models.ManyToManyField(Media, verbose_name='偏好媒体', help_text='客户偏好的媒体', blank=True, null=True)
    industry = models.ForeignKey(Industry, blank=True, null=True)
    objects = ClientManager()
    
    class Meta:
        verbose_name = '客户'
        verbose_name_plural = '客户'
    
    def __unicode__(self):
        return self.c_name
    
class DomainName(models.Model):
    client = models.ForeignKey(Client, null=True, blank=True, verbose_name=u'客户')
    business = models.ForeignKey(User, null=True, blank=True, verbose_name=u'营业')
    ip = models.CharField(u'地址', max_length=256, blank=True)
    domain_name = models.CharField(u'域名', max_length=256)
    path = models.CharField(u'存储路径', max_length=256, blank=True)
    parse_status = models.CharField(u'解析状态', max_length=256, blank=True)
    domain_name_register_info = models.CharField(u'域名注册信息', max_length=256, blank=True)
    domain_name_register_address = models.CharField(u'域名注册地址', max_length=256, blank=True)
    remark = models.CharField(u'备注', max_length=256, blank=True)
    
    class Meta:
        verbose_name = u'域名'
        verbose_name_plural = '域名'
        
    def __unicode__(self):
        return self.domain_name
