#! /usr/bin/env python
#coding=utf-8

from django.db import models
from MediaChooser.media_planning.models import Flight
from MediaChooser.ad.models import Ad

class UserBehaviourManager(models.Manager):
    def om_report(self, campaign_id):
        ubs = []
        tracking_codes = ['%s' % f.DE_ad_id for f in Ad.objects.get(DE_campaign_id=campaign_id).flights.all()]
        
        from django.db import connection
        cursor = connection.cursor()
        sql = "SELECT tracking_code, sum(pv) as pv, sum(visits) as visits, sum(uv) as uv, \
                sum(products_view) as product_view,sum(cart_addition) as cart,  sum(checkouts) as checkouts, \
                sum(orders) as orders,sum(revenue) as revenue FROM user_behaviour_userbehaviour \
                WHERE level = \'om\' AND tracking_code in %s \
                GROUP BY tracking_code, level order by tracking_code" % str(tuple(tracking_codes))
        cursor.execute(sql)
        rows = cursor.fetchall()

        for r in rows:
            ub = {}
            f = Flight.objects.get(DE_ad_id=r[0])

            ub['media'] = f.media.c_name
            ub['channel'] = f.channel.c_name
            ub['adform'] = f.media_ad_info.adform
            ub['click'] = f.click
            ub['tracking_code'] = r[0]
            ub['pv'] = r[1]
            ub['visits'] = r[2]
            ub['uv'] = r[3]
            ub['products_view'] = r[4]
            ub['cart_addition'] = r[5]
            ub['checkouts'] = r[6]
            ub['orders'] = r[7]
            ub['revenue'] = r[8]
            if f.click == 0:
                ub['loss'] = 0
            else:
                ub['loss'] = "%.2f" % ((f.click - r[2]) * 1.0 * 100 / f.click)

            ubs.append(ub)
        ubs.sort(lambda x,y: cmp(x['media'], y['media']))
        
        return ubs
        
    
    def ga_report(self, campaign_id):
        ubs = []
        tracking_codes = ['%s' % f.DE_ad_id for f in Ad.objects.get(DE_campaign_id=campaign_id).flights.all()]
        
        from django.db import connection
        cursor = connection.cursor()
        sql = "SELECT tracking_code, sum(pv), sum(visits), sum(entrances), sum(bounces), sum(time_onsite) \
                FROM user_behaviour_userbehaviour GROUP BY tracking_code, level having level = \'ga\' and \
                tracking_code in %s order by tracking_code; " % str(tuple(tracking_codes))
        cursor.execute(sql)
        rows = cursor.fetchall()
        
        for r in rows:
            ub = {}
            tracking_code = r[0]
            pv = r[1]
            visits = r[2]
            entrances = r[3]
            bounces = r[4]
            time_onsite = r[5]
            
            avg_time = 'N/A'
            if visits != 0:
                avg_time = int(round(time_onsite *1.0 /visits))
            
            bounce_rate = 'N/A'
            if entrances !=0:
                bounce_rate = "%.2f" % (bounces * 1.0 * 100 /entrances)

            f = Flight.objects.get(DE_ad_id=tracking_code)      
            ub['media'] = f.media.c_name
            ub['channel'] = f.channel.c_name
            ub['adform'] = f.media_ad_info.adform
            ub['click'] = f.click
            ub['pv'] = pv
            ub['visits'] = visits
            ub['avg_time'] = avg_time
            ub['bounce_rate'] = bounce_rate
            ub['tracking_code'] = tracking_code
            if f.click == 0:
                ub['loss'] = 0
            else:
                ub['loss'] = "%.2f" % ((f.click - visits) * 1.0 * 100 / f.click)
            ubs.append(ub)
        ubs.sort(lambda x,y: cmp(x['media'], y['media']))
    
        return ubs
        
    def get_ub_by_campaign(self, campaign_id):
        tracking_codes = ['%s' % f.DE_ad_id for f in Ad.objects.get(DE_campaign_id=campaign_id).flights.all()]
        rsts = self.filter(tracking_code__in=tracking_codes).aggregate(models.Sum('visits'), models.Sum('products_view'), \
            models.Sum('cart_addition'),models.Sum('checkouts'), models.Sum('orders'))
        return rsts
        
            
    
class UserBehaviour (models.Model):
    
    TIME_ONSITE_CHOICES = (('A','<1 minute'),('B','1-5 minutes'), ('C','5-10 minutes'), ('D','10-30 minutes'), \
                           ('E','30-60 minutes'), ('F','1-2 hours'), ('G','2-5 hours'), ('H','5-10 hours'), ('I','10-15 hours'))
    
    LEVEL_CHOICES = (('om','Omniture'), ('ga','Google Ananytics'))
    startdate = models.DateField('日期')
    #flight = models.ForeignKey(Flight)
    tracking_code = models.CharField(max_length=10)  # ngAdID
    #DE_flight_id = models.IntegerField('DE_flight_id', help_text='DE_flight_id')
    #minisite = models.CharField('',max_length=255)
    #average_pages = models.FloatField('浏览页面', default=0.0)
    #time_onsite_mark = models.CharField(max_length=2, choices=TIME_ONSITE_CHOICES)
    #bounce_rate = models.FloatField('跳出率', default=0.0)
    
    pv = models.IntegerField('PageView', default=0)
    uv = models.IntegerField('独立访问人数', default=0)
    visits = models.IntegerField(default=0)
    
    #ga only
    entrances = models.IntegerField(default=0)
    bounces = models.IntegerField(default=0)
    time_onsite = models.FloatField(default=0)
    
    # omniture only
    products_view = models.IntegerField(default=0)
    cart_addition = models.IntegerField(default=0)
    checkouts = models.IntegerField(default=0)
    orders = models.IntegerField(default=0)
    revenue = models.FloatField(default=0.0)
    
    level = models.CharField(max_length=2, choices=LEVEL_CHOICES)
    add_time = models.DateTimeField(auto_now_add=True)
    
    objects = UserBehaviourManager()
    
    def __unicode__(self):
        return self.tracking_code        
