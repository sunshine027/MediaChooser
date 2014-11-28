#! /usr/bin/env python
#coding=utf-8

from django.db import models

class NielsenCategory (models.Model):

    parent = models.ForeignKey('self', related_name='parent_category', verbose_name=u'上级分类', blank=True, null=True)
    c_name = models.CharField('中文名称', max_length=40, help_text='中文名称')
    e_name = models.CharField('英文名称', max_length=40, help_text='英文名称')
    desc = models.TextField('描述', blank=True, null=True, help_text='描述')
    
    class Meta:
        verbose_name = '分类'
        verbose_name_plural = '分类'
        unique_together = (("c_name", "e_name"),)
        
    def __unicode__(self):
        if self.parent == None:
            return self.c_name
        else:
            return self.parent.c_name+'->'+self.c_name


class NielsenMedia (models.Model):

    domain = models.URLField('域名',verify_exists=False)
    c_name = models.CharField('中文名称', max_length=40, help_text='中文名称')
    e_name = models.CharField('英文名称', max_length=40, help_text='英文名称')
    main_category = models.ForeignKey(NielsenCategory, related_name='media_main_category', verbose_name='所属分类', blank=True, null=True)
    sub_category = models.ForeignKey(NielsenCategory, related_name='media_sub_category', verbose_name='所属子分类', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Nielsen媒体'
        verbose_name_plural = 'Nielsen媒体'
        
    def __unicode__(self):
        return self.c_name


class NielsenChannel (models.Model):

    media = models.ForeignKey(NielsenMedia, verbose_name='所属媒体', blank=True, null=True)
    domain = models.URLField('域名',verify_exists=False)
    c_name = models.CharField('频道中文名称', max_length=40, help_text='中文名称')
    e_name = models.CharField('英文名称', max_length=40, help_text='英文名称')
    main_category = models.ForeignKey(NielsenCategory, related_name='channel_main_category', verbose_name='所属分类', blank=True, null=True)
    sub_category = models.ForeignKey(NielsenCategory, related_name='channel_sub_category', verbose_name='所属子分类', blank=True, null=True)
    
    class Meta:
        verbose_name = 'Nielsen频道'
        verbose_name_plural = 'Nielsen频道'
        
    def __unicode__(self):
        return self.c_name

class Province (models.Model):

    c_name = models.CharField('中文名称', max_length=40, help_text='中文名称', unique=True)
    e_name = models.CharField('英文名称', max_length=40, help_text='英文名称', unique=True)
    
    class Meta:
        verbose_name = '省份'
        verbose_name_plural = '省份'
        
    def __unicode__(self):
        return self.c_name

class NielsenTrafficData(models.Model):

    media = models.ForeignKey(NielsenMedia, verbose_name='媒体', blank=True, null=True)
    channel = models.ForeignKey(NielsenChannel, verbose_name='频道', blank=True, null=True)
    province = models.ForeignKey(Province, verbose_name='省份')
    all_ub = models.FloatField(blank=True, null=True)
    all_us_change = models.FloatField(blank=True, null=True)
    all_ts = models.FloatField(blank=True, null=True)
    all_ub_freq = models.FloatField(blank=True, null=True)
    all_asd = models.FloatField(blank=True, null=True)
    sample_ub = models.FloatField(u'样本流量UB(mil.)')
    sample_ub_freq = models.FloatField(u'样本流量UB Freq')
    sample_ts = models.FloatField(u'样本流量TS(mil.)')
    sample_asd = models.FloatField(u'样本流量ASD(s)')
    week = models.DateTimeField(u'周', max_length=40)

    class Meta:
        verbose_name = 'Nielsen流量数据'
        verbose_name_plural = 'Nielsen流量数据'

    def __unicode__(self):
        if self.media:
            return self.media.c_name + '-' + self.province.c_name + '-' + str(self.week.year) + str(self.week.month) + str(self.week.day)
        elif self.channel:
            return self.channel.c_name + '-' + self.province.c_name + '-' + str(self.week.year) + str(self.week.month) + str(self.week.day)
            
class NielsenOverlap (models.Model):

    media_a = models.ForeignKey(NielsenMedia, related_name='media_a', verbose_name='基准媒体')
    media_b = models.ForeignKey(NielsenMedia, related_name='media_b', verbose_name='对比媒体')
    net_ub = models.FloatField(u'Net UB(mil.)')
    ub_dup = models.FloatField(u'UB Dup(mil.)')
    dup = models.FloatField(u'重合度Dup(%)')
    week = models.DateTimeField(u'周', max_length=40)
    
    class Meta:
        verbose_name = 'Nielsen媒体重合度'
        verbose_name_plural = 'Nielsen媒体重合度'
        
    def __unicode__(self):
        return "%s - %s: %s" % (self.media_a, self.media_b, self.dup)