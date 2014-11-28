#! /usr/bin/env python
#coding=utf-8

import datetime

from django.db import models
from django.contrib.auth.models import Group
from django.contrib.auth.models import User

from MediaChooser.media.models import Media, Channel
from MediaChooser.client.models import Client

EFFECTIVE_COUNT = 10
DC_CLICK_EVENTTYPE = 4

# 广告形式表
class AdType(models.Model):
    AD_CATEGORY_CHOICES = ((1, '硬广'),(2, '软广'),(3, '专题'),(4, '活动'),)

    category = models.PositiveSmallIntegerField('分类', choices=AD_CATEGORY_CHOICES, help_text='分类')
    c_name = models.CharField('中文名称', max_length=40, help_text='中文名称')
    e_name = models.CharField('英文名称', max_length=40, help_text='英文名称', blank=True, null=True)
    desc = models.TextField('描述', blank=True, null=True, help_text='描述')
    demo = models.FileField('演示', upload_to='files/', blank=True, null=True, help_text='演示')
    advantage = models.TextField('优势', blank=True, null=True, help_text='优势')
    disadvantage = models.TextField('劣势', blank=True, null=True, help_text='劣势')
    class Meta:
        verbose_name = '广告形式'
        verbose_name_plural = '广告形式'
    def __unicode__(self):
        return self.c_name

# 投放类型
class ActivityType(models.Model):
    name = models.CharField('名称', max_length=20, help_text='活动名称')
    desc = models.TextField('描述', null=True, blank=True, help_text='描述')

    class Meta:
        verbose_name = '活动类型'
        verbose_name_plural = '活动类型'
    
    def __unicode__(self):
        return self.name

class Ad(models.Model):
    client   = models.ForeignKey(Client, verbose_name='广告主')
    #adtype = models.ForeignKey(AdType, verbose_name='类型', related_name='related_adinfo')
    activity_type = models.ForeignKey(ActivityType)
    #product  = models.ForeignKey(Product)
    #minisite = models.ForeignKey(MiniSite)
    DE_campaign_id = models.IntegerField('campaign_id', unique=True, help_text='campaign_id')
    name  = models.CharField('name', help_text='name', max_length=256)

    # statistic related info
    spending	= models.IntegerField('投放费用', default=0)
    click		= models.IntegerField('DE记录到的点击数', default=0)
    cpc			= models.FloatField('CPC', default=0)

    #title = models.CharField('title', help_text='title', max_length=96)
    desc = models.TextField('desc', blank=True, null=True, help_text='desc')

    #targeting = models.DateField()
    uploader  = models.ForeignKey(User, verbose_name='上传者')
    start_day = models.DateField('开始日期', help_text='开始日期')
    end_day = models.DateField('结束日期', help_text='结束日期')
    create_time = models.DateTimeField('创建日期', auto_now_add=True, null=True, help_text='创建日期')
    last_modified = models.DateTimeField('最后修改', auto_now=True, null=True, help_text='最后修改')

    related_staff = models.ManyToManyField(User, related_name='ads', verbose_name='相关人员', through='AdRelatedStaff')
    ga_pid = models.CharField('GA profile id', blank=True, max_length=20)
    
    group_id = models.IntegerField('用户组', default=-1)
    
    date_range = []
    media = []
    date_price = {}
    date_click = {}
    
    has_init = False
    
    class Meta:
        verbose_name = 'Campaign'
        verbose_name_plural = 'Campaign'
                    
    def __unicode__ (self):
        return self.name
    
    def _init(self):
        self.date_range = []
        for n in range((self.end_day - self.start_day).days+1):
            date_str = str(self.start_day + datetime.timedelta(days=n))
            self.date_range.append(date_str)
            self.date_price[date_str] = 0
            self.date_click[date_str] = 0
        
        self.media = self._campaign_media()
        
    
    def _campaign_media(self):
        media = set()
        for f in self.flights.all():
            media.add(f.media.c_name)
        media_list = list(media)
        media_list.sort()
        return media_list
    
    def media_click(self):
        """ return sorted media click list during this campaign """
        media_click = {}
        flights = self.flights.all()
        for f in flights:
            if f.media.c_name in media_click:
                media_click[f.media.c_name] += f.click
            else:
                media_click[f.media.c_name] = f.click
        #return [ x[1] for x in sorted(media_click.iteritems(), key=lambda d:d[0])]
        return media_click
    
    def media_price(self):
        """ return sorted media price and tracked price list during this campaign """
        media_price = {}
        media_price_tracked = {}
        flights = self.flights.all()
        for f in flights:
            media_name = f.media.c_name
            if f.if_buy:
                if media_name in media_price:
                    media_price[media_name] += f.total_price * f.discount_after_discount
                else:
                    media_price[media_name] = f.total_price * f.discount_after_discount
                if media_name in media_price_tracked:
                    media_price_tracked[media_name] += f.total_price_tracked * f.discount_after_discount
                else:
                    media_price_tracked[media_name] = f.total_price_tracked * f.discount_after_discount
            else:
                if media_name not in media_price:
                    media_price[media_name] = 0
                if media_name not in media_price_tracked:
                    media_price_tracked[media_name] = 0
        #return [x[1] for x in sorted(media_price.iteritems(), key=lambda d:d[0])], [x[1] for x in sorted(media_price_tracked.iteritems(), key=lambda d:d[0])]
        return media_price, media_price_tracked
    
    def media_cpc(self):
        """ return sorted media cpc list during this campaign """
        media = self.media
        media_cpc = {}
        media_click = self.media_click()
        media_price = self.media_price()[1]
        #for i, m in enumerate(media):
        #    if media_click[i] != 0:
        #        media_cpc[i] = media_price[i] * 1.0 / media_click[i]
        #    else:
        #        media_cpc[i] = 0 
        
        for m in media_price:
            if media_click[m] != 0:
                media_cpc[m] = media_price[m] * 1.0 / media_click[m]
            else:
                media_cpc[m] = 0
        
        return media_cpc
        
    def daily_click(self):
        flights = self.flights.all()
        fids = [ f.id for f in flights]
        from django.db import connection
        cursor = connection.cursor()
        sql = "SELECT date,sum(eventcount) FROM media_planning_de_clickdata \
            WHERE flight_id in %s and eventtype=%s and eventcount > %s\
            GROUP BY date ORDER BY date" % (str(tuple(fids)), DC_CLICK_EVENTTYPE, EFFECTIVE_COUNT)
        cursor.execute(sql)
        rows = cursor.fetchall()
        for r in rows:
            d = str(r[0])
            if d >= str(self.start_day) and d <= str(self.end_day):
                self.date_click[str(r[0])] = r[1]
        
        #return [x[1] for x in sorted(self.date_click.iteritems(), key=lambda d:d[0])]
        return self.date_click
        
    def daily_price(self):
        flights = self.flights.all()
        fids = [ f.id for f in flights]
        from django.db import connection
        cursor = connection.cursor()        
        sql = "SELECT a.date,sum(b.unit_price * b.discount_after_discount) \
            FROM media_planning_de_clickdata a, media_planning_flight b \
            WHERE a.flight_id in %s AND a.if_planned_spending = true AND a.eventtype=%s AND a.eventcount > %s AND a.flight_id = b.id \
            AND b.if_buy = true GROUP BY a.date ORDER BY a.date" % (str(tuple(fids)), DC_CLICK_EVENTTYPE, EFFECTIVE_COUNT)
        cursor.execute(sql)
        rows = cursor.fetchall()
        for r in rows:
            self.date_price[str(r[0])] = r[1]
        
        #return [x[1] for x in sorted(self.date_price.iteritems(), key=lambda d:d[0])]
        return self.date_price
    
    def daily_cpc(self):
        daily_price = self.daily_price()
        daily_click = self.daily_click()
        #daily_cpc = [0] * len(self.date_range)
        daily_cpc = {}
        #for i in range(len(daily_cpc)):
        #    if daily_click[i] != 0:
        #        daily_cpc[i] = daily_price[i] / daily_click[i]
        #    else:
        #        daily_cpc[i] = 0
        for d in daily_click:
            if daily_click[d] != 0:
                daily_cpc[d] = daily_price[d] / daily_click[d]
            else:
                daily_cpc[d] = None
        return daily_cpc
    
    def media_daily_click(self):
        media_daily_click = {}
        flights = self.flights.all()
        fids = [ f.id for f in flights]
        from django.db import connection
        cursor = connection.cursor()
        sql = "SELECT b.c_name, a.date, sum(eventcount) FROM media_planning_de_clickdata a, media_media b \
            WHERE flight_id in %s and eventtype=%s and eventcount > %s and a.media_id = b.id \
            GROUP BY b.c_name, date ORDER BY b.c_name, date" % (str(tuple(fids)), DC_CLICK_EVENTTYPE, EFFECTIVE_COUNT)
        cursor.execute(sql)
        rows = cursor.fetchall()
        for r in rows:
            media_name = r[0]
            date = r[1]
            click = r[2]
            
            if media_name in media_daily_click:
                media_daily_click[media_name][str(date)] = r[2]
            else:
                media_daily_click[media_name] = [0] * len(self.date_range)
        
        return media_daily_click
        #
    
    def campaign_detail(self):
        from django.db import connection
        cursor = connection.cursor()
        sql = "select b.c_name, d.c_name, c.adform, a.total_price * a.discount_after_discount, \
                a.click, a.if_buy, a.start_day, a.end_day, a.\"DE_ad_id\" \
                from media_planning_flight a, media_media b, media_mediaadinfo c, media_channel d \
                where a.media_id = b.id and a.ad_id =%s and c.id = a.media_ad_info_id and \
                a.channel_id = d.id order by b.c_name, d.c_name" % self.id
        cursor.execute(sql)
        rows = cursor.fetchall()
        result = []
        for r in rows:
            media = r[0]
            channel = r[1]
            adform = r[2]
            price = int(r[3])
            click = r[4]
            if_buy = r[5]
            start_day = r[6]
            end_day = r[7]
            de_ad_id = r[8]

            result.append({'media':media, 'channel':channel, 'adform':adform, 'price':price, 'click':click, 'if_buy':if_buy, 'start_day':start_day, 'end_day':end_day,'de_ad_id':de_ad_id})

        return result
        

class AdRelatedStaff(models.Model):
    ad = models.ForeignKey(Ad, verbose_name='广告')
    staff = models.ForeignKey(User, verbose_name='相关人员')

#
#class DE_Cmpaign_Processed(models.Model):
#    #all follow fields are for DE
#    campaignid  = models.IntegerField('CampaignID', help_text='CampaignID')
#    flightid    = models.IntegerField('FlightID', help_text='FlightID')
#    flightname  = models.CharField('FlightName', max_length=64, help_text='FlightName')
#    flightnum   = models.IntegerField('FlightNum', help_text='FlightNum')
#    class Meta:
#        verbose_name = '已导入的排期'
#        verbose_name_plural = '已导入的排期'        

class AdCreative(models.Model):
    ad = models.ForeignKey(Ad, verbose_name='广告')
    creative = models.FileField(upload_to='creatives')