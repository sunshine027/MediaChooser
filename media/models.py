#! /usr/bin/env python
#coding=utf-8

from django.db import models
from MediaChooser.misc.models import Contact, Industry, GeographicInfo
from django.contrib.contenttypes import generic
from MediaChooser.NielsenMedia.models import NielsenCategory 

# 媒体类别
class MediaCategory(models.Model):
    parent = models.ForeignKey(
        'self', null=True, blank=True, help_text='父类', verbose_name='父类', related_name='related_child_category')
    c_name = models.CharField('中文名称', max_length=40, help_text='中文名称')
    e_name = models.CharField('英文名称', max_length=40, help_text='英文名称')
    e_abbr = models.CharField('英文简称', max_length=10, help_text='英文简称')
    # 分类来源, &c, Nielsen, iResearch等
    # cate_src = models.CharField()
    desc = models.TextField(blank=True, null=True, help_text='描述')

    class Meta:
        verbose_name = '媒体类别'
        verbose_name_plural = '媒体类别'

    def __unicode__(self):
        if self.parent == None:
            return self.c_name
        else:
            return self.parent.c_name+'->'+self.c_name

# 媒体
class Media(models.Model):
    ISSUE_ORGANIZATION_CHOICES = (('gov', '国家机关'),('local', '省市'),('per', '私人'),)
    logo = models.ImageField('logo', upload_to='files/', blank=True, help_text='媒体logo', null=True)
    c_name = models.CharField('中文名称', max_length=30, help_text='中文名称')
    e_name = models.CharField('英文名称', max_length=30, help_text='英文名称', null=True, blank=True)
    domain = models.CharField('域名', max_length=200, help_text='域名', unique=True)
    # second_category所在的父类必须与first_category吻合
    # 同时考虑category会来自多方

    first_category = models.ForeignKey(MediaCategory, help_text='一级类别', verbose_name='一级类别', related_name='related_first_category', blank=True, null=True)
    # first_category = models.ForeignKey(NielsenCategory, help_text='Nielsen一级类别', verbose_name='Nielsen一级类别', related_name='related_first_media', blank=True, null=True)
    second_category = models.ForeignKey(MediaCategory, help_text='二级类别', verbose_name='二级类别', related_name='related_second_category', blank=True, null=True)
    # second_category = models.ForeignKey(NielsenCategory, help_text='Nielsen二级类别', verbose_name='Nielsen二级类别', related_name='related_second_media', blank=True, null=True)

    industry = models.ForeignKey(Industry, verbose_name='所属行业', help_text='媒体所属行业', null=True, blank=True)

    issue_organization = models.CharField('发行', max_length=20, help_text='发行机关', choices=ISSUE_ORGANIZATION_CHOICES, blank=True, null=True)
    influence_area = models.ForeignKey(GeographicInfo, blank=True, verbose_name='影响地域', help_text='影响地域', null=True)
    # audience 所有的数据都记录在Audience表中，可能需要根据需求做关联
    # advantage_channel 信息记录在Channel表中
    # 上网时段？
    # supported_adtype=property(), 根据media的channel支持的adtype属性来获得本字段
    # coopreator 合作客户
    advantage = models.TextField('优势', blank=True, null=True, help_text='媒体优势')
    addr = models.CharField('地址', blank=True, null=True, max_length=50, help_text='联系人地址')
    zipcode = models.CharField('邮编', blank=True, null=True, max_length=6, help_text='邮编')
    desc = models.TextField('描述', blank=True, null=True, help_text='描述')

    contact = generic.GenericRelation(Contact, null=True, blank=True)

    class Meta:
        verbose_name = '媒体'
        verbose_name_plural = '媒体'

    def __unicode__(self):
        return self.c_name

# 媒体动态属性 -- data from third party

# 公关媒体属性
class MediaAttrForPR(models.Model):
    LEVEL_CHOICES = (('a', 'A'), ('b', 'B'), ('c', 'C'),)

    media = models.ForeignKey(Media, verbose_name='媒体', related_name='related_mediaAttrForPR')
    level = models.CharField('级别', max_length=1, choices=LEVEL_CHOICES, help_text='网站分级')
    class Meta:
        verbose_name = '媒体公关属性'
        verbose_name_plural = '媒体公关属性'

    def __unicode__(self):
        return self.media.c_name

# 媒体重合度
class MediaOverlapRatio(models.Model):
    media_a = models.ForeignKey(Media, verbose_name='媒体 a', help_text='媒体 a', related_name='related_MediaOverlapRatio_a')
    media_b = models.ForeignKey(Media, verbose_name='媒体 b', help_text='媒体 b', related_name='related_MediaOverlapRatio_b')
    overlap_ratio = models.FloatField('重合度', help_text='媒体重合度')
    net_ratio = models.FloatField('覆盖度', help_text='媒体总覆盖度')
    class Meta:
        verbose_name = '媒体重合度'
        verbose_name_plural = '媒体重合度'

    def __unicode__(self):
        return self.media_a.c_name + ' - ' + self.media_b.c_name

# 媒体线下资源
class MediaOfflineRes(models.Model):
    TYPE_CHOICES = (('a', '附赠媒体'),('b', '社区'),('c', '会展'),)

    media = models.ForeignKey(Media, verbose_name='媒体', help_text='媒体', related_name='related_MediaOfflineRes')
    res_type = models.CharField('资源类型', max_length=1, choices=TYPE_CHOICES, help_text='媒体线下资源类型')
    advantage = models.TextField('优势', blank=True, null=True, help_text='媒体优势')
    contact = generic.GenericRelation(Contact)

    class Meta:
        verbose_name = '媒体线下资源'
        verbose_name_plural = '媒体线下资源'

    def __unicode__(self):
        return self.media.c_name     


# 媒体软性指标

# 媒体配合度

# 媒体出错记录

# 媒体利润

# 媒体框架协议

# 频道
class Channel(models.Model):
    WEIGHT_CHOICES = (('a','高'),('b','较高'),('c','中'),('d','较低'),('e','低'),)

    media = models.ForeignKey(Media, verbose_name='媒体', help_text='所在媒体', related_name='related_channels')
    c_name = models.CharField('名称', help_text='频道中文名称', max_length=128)
    domain = models.URLField('域名', null=True, verify_exists=True, help_text='域名', blank=True)
    weight = models.CharField('权重', null=True, max_length=1, choices=WEIGHT_CHOICES, help_text='频道权重', blank=True)   #'中' as default

    class Meta:
        verbose_name = '频道'
        verbose_name_plural = '频道'

    def __unicode__(self):
        return '%s->%s'%(self.media.c_name, self.c_name)

# 频道动态属性

# 媒体频道广告位
class MediaAdInfo(models.Model):
    media         = models.ForeignKey(Media, verbose_name='媒体', related_name='related_adinfo')
    channel       = models.ForeignKey(Channel, verbose_name='频道', related_name='related_adinfo')
    adform        = models.CharField('广告形式', max_length=256) # store raw AD form info from Media Planning file

    adformat      = models.CharField('广告格式', max_length=48, help_text='广告规格-文件格式', blank=True, null=True)  #jpg, gif, swf ...
    adfilesize    = models.IntegerField('文件大小', help_text='广告规格-文件大小', null=True, blank=True)              #unit: k
    adsize        = models.CharField('内容格式', max_length=10, help_text='广告规格-内容格式', blank=True, null=True)  #m * n 
    #price         = models.IntegerField('价格', null=True, help_text='价格')
    #discount      = models.PositiveSmallIntegerField('折扣', null=True, help_text='折扣')
    adsize_detail = models.CharField('广告规则', max_length=256, blank=True, null=True, help_text='广告形式原始信息')

    class Meta:
        verbose_name = '媒体频道广告位'
        verbose_name_plural = '媒体频道广告位'
    
    def __unicode__(self):
        return self.adform

# 媒体成功案例
