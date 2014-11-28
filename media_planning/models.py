#! /usr/bin/env python
#coding=utf-8
import datetime

from django.db import models
from MediaChooser.ad.models import Ad
from MediaChooser.media.models import MediaAdInfo, Media, Channel

# Create your models here.

class Flight(models.Model):
    ad             = models.ForeignKey(Ad, verbose_name='campaign', help_text='campaign', related_name='flights')

    media = models.ForeignKey(Media, verbose_name='Media', related_name='flights')
    channel = models.ForeignKey(Channel, verbose_name='Channel', related_name='flights')
    media_ad_info  = models.ForeignKey(MediaAdInfo, verbose_name='MediaAdInfo', help_text='MediaAdInfo', related_name='flights')

    pv				= models.IntegerField('PV', help_text='Page View', blank=True, null=True)
    spending      	= models.IntegerField('投放量', help_text='投放量') # 排期上写的投放量
    unit = models.CharField('单位', max_length=8, help_text='单位') # 投放的单位，CPM/天
    ad_days = models.SmallIntegerField('投放天数', help_text='投放天数') # 从排期中获取到的投放的总天数
    ad_days_tracked = models.SmallIntegerField('有效投放天数', help_text='有效投放天数', default=0)	# 有效的投放天数，也即监测到的点击数>10的那些投放日
    if_buy		   = models.BooleanField('购买方式', help_text='购买方式')	# True：购买；False：赠送
    discount       = models.FloatField('折扣', help_text='折扣')
    unit_price     = models.FloatField('折后单价', help_text='折后单价')
    total_price = models.FloatField('折后总价', help_text='折后总价')
    #unit_price_weighted		= models.FloatField('加权后折后单价', help_text='加权后折后单价')	# 目前暂时不用
    #total_price_weighted	= models.FloatField('加权后折后总价', help_text='加权后折后总价')	# 目前暂时不用
    total_price_tracked		= models.FloatField('有效的投放额', help_text='有效的投放额', default=0)		# 有效的投放额度，即监测到的点击数>10的那些投放日的额度累加；=unit_price_weighted*ad_days_tracked
    discount_after_discount	= models.FloatField('折上折', help_text='折上折')		# 媒体购买的广告位的总价有时候会再打一个折扣（折上折）来到媒体总价，这种情况不多

    # statistic related info
    click 	= models.IntegerField('点击数', help_text='点击数', default=0) # FIX me with a function ...
    cpc		= models.FloatField('CPC', default=0)
    cpc_weighted	= models.FloatField('加权后CPC', default=0)		# 目前暂时不用
    start_day	= models.DateField(null=True, blank=True)	# 投放开始日
    end_day		= models.DateField(null=True, blank=True)	# 投放结束日

    DE_backend_url = models.TextField('后台URL', null=True, blank=True, help_text='后台URL')
    DE_campaign_id = models.IntegerField('DE_campaign_id')
    DE_flight_id = models.IntegerField('DE_flight_id', help_text='DE_flight_id')
    # DE_flight_number = models.SmallIntegerField('DE_flight_number', help_text='广告位在排期中的序列号')
    DE_ad_id = models.IntegerField('DE_ngAdID', help_text='DE_ngAdID')
    clickurl = models.CharField('目标网址', max_length=200, help_text='目标网址')
    
    unit_price_weighted = models.IntegerField('权重单价', help_text='分配权重后的单价')
    total_price_weighted = models.IntegerField('权重总价', help_text='分配权重后的总价')
    cpc_weighted = models.FloatField('权重CPC', default=0)
    
    class Meta:
        verbose_name = '广告位信息'
        verbose_name_plural = '广告位信息'
    
    def __unicode__(self):
        return "campaign:%s - %s - %s" % (self.DE_campaign_id, self.DE_ad_id, self.DE_flight_id)
    
    def is_end(self):
        """ if the flight ends ? compare with today """
        today = datetime.date.today()
        if (self.end_day - today).days >= 0:
            return False
        return True
    

class DE_ClickData(models.Model):
    ad		= models.ForeignKey(Ad, related_name='de_clickdata')
    media 	= models.ForeignKey(Media, related_name='de_clickdata')
    channel = models.ForeignKey(Channel, related_name='de_clickdata')
    media_ad_info = models.ForeignKey(MediaAdInfo, related_name='de_clickdata')
    flight      = models.ForeignKey(Flight, verbose_name='排期', help_text='排期', related_name='de_clickdata')
    cpm			= models.IntegerField('CPM', default=0) 	# 如果投放的单位为CPM，此字段用来记录该日的CPM投放量
    eventtype   = models.IntegerField('事件类型', help_text='事件类型', default=-1) # -1 means no type
    # 对于点击数<10的情况，可以认为是无效的数据；
    # 发生这种情况可能是因为：点击代码没有加到素材中；那几个零散的点击是测试时候记录到的；
    eventcount  = models.IntegerField('时间数量', help_text='事件数量', default=0)  # 0 means no data
    date        = models.DateField('事件日期', help_text='事件日期')
    # 对于在排期中计划的投放日，值为true，反之为false
    if_planned_spending		= models.BooleanField('是否计划投放', help_text='是否计划投放')

    class Meta:
        verbose_name = 'DE监测点击数据'
        verbose_name_plural = 'DE监测点击数据'
