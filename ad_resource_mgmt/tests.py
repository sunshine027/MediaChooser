# coding: utf-8

import datetime

from django.test.client import Client as Clt
from django.contrib.auth.models import User
from django.test import TestCase

from MediaChooser.ad.models import ActivityType, Ad
from MediaChooser.media_planning.models import Flight, DE_ClickData
from MediaChooser.client.models import Client
from MediaChooser.ad_resource_mgmt.views import get_mediareco
from MediaChooser.media.models import Media,Channel,MediaAdInfo

class AdMgmtTest(TestCase):
        
    def setUp(self):
        #self.client = Clt()
        
        # User
        self.user1 = User.objects.create_user('user1111', 'user1@and-c.com', 'user1pass')
        self.user2 = User.objects.create_user('user2222', 'user2@and-c.com', 'user2pass')
        
        # activitytype
        self.at = ActivityType.objects.create(name='ss')
        
        # client
        self.clt_lenovo = Client.objects.create(c_name="lenovo",e_name='lenovo')
        self.clt_hy = Client.objects.create(c_name="hy",e_name='hy')
        
        # ad
        self.ad_lenovo1 = Ad.objects.create(client=self.clt_lenovo, DE_campaign_id=1800, cpc=5, click=5000, \
            activity_type=self.at, start_day=datetime.date(2009,6,1), end_day=datetime.date(2009,6,5), uploader_id=1)
        self.ad_lenovo2 = Ad.objects.create(client=self.clt_lenovo, DE_campaign_id=1900, cpc=7, click=7000, \
            activity_type=self.at, start_day=datetime.date(2009,6,1), end_day=datetime.date(2009,6,5), uploader_id=2)
        
        # media
        self.sina = Media.objects.create(c_name='sina',domain="sina.com.cn")
        self.sohu = Media.objects.create(c_name='sohu',domain="sohu.com")
        
        # channel
        self.sina_ch1 = Channel.objects.create(c_name="sina_ch1", media=self.sina)
        self.sina_ch2 = Channel.objects.create(c_name="sina_ch2", media=self.sina)
        self.sohu_ch1 = Channel.objects.create(c_name="sohu_ch1", media=self.sohu)
        self.sohu_ch2 = Channel.objects.create(c_name="sohu_ch2", media=self.sohu)
        
        # mediaadinfo
        self.sina_mai1 = MediaAdInfo.objects.create(media=self.sina, channel=self.sina_ch1, adform='tonglan')
        self.sina_mai2 = MediaAdInfo.objects.create(media=self.sina, channel=self.sina_ch2, adform='tonglan')
        self.sohu_mai1 = MediaAdInfo.objects.create(media=self.sohu, channel=self.sohu_ch1, adform='tonglan')
        
        self.sina_flight1 = Flight.objects.create(media=self.sina, channel=self.sina_ch1, ad=self.ad_lenovo1, \
                                media_ad_info=self.sina_mai1, spending=10, ad_days=60, discount=0.6, unit_price=8000, \
                                total_price=8000, DE_campaign_id=1800, DE_flight_id=100, DE_flight_number=1, \
                                start_day=datetime.date(2009,6,1), end_day=datetime.date(2009,6,3), unit_price_weighted=0, \
                                total_price_weighted=0, cpc=3.5, click=3000, discount_after_discount=0.9,DE_ad_id=22222, \
                                if_buy=True, total_price_tracked=5000) # 7200
        
        self.sina_flight2 = Flight.objects.create(media=self.sina, channel=self.sina_ch2, ad=self.ad_lenovo1, \
                                media_ad_info=self.sina_mai2, spending=10, ad_days=60, discount=0.6, unit_price=7000, \
                                total_price=7000, DE_campaign_id=1800, DE_flight_id=101, DE_flight_number=2, \
                                start_day=datetime.date(2009,6,3), end_day=datetime.date(2009,6,5), unit_price_weighted=0, \
                                total_price_weighted=0, cpc=4.5, click=4000, discount_after_discount=0.8, DE_ad_id=11111, \
                                if_buy=True,total_price_tracked=6000) # 5600
        
        self.sohu_flight1 = Flight.objects.create(media=self.sohu, channel=self.sohu_ch1, ad=self.ad_lenovo1, \
                                media_ad_info=self.sohu_mai1, spending=10, ad_days=60, discount=0.6, unit_price=9000, \
                                total_price=8000, DE_campaign_id=1800, DE_flight_id=100, DE_flight_number=1, \
                                start_day=datetime.date(2009,6,1), end_day=datetime.date(2009,6,3), unit_price_weighted=0, \
                                total_price_weighted=0, cpc=3.5, click=5000, discount_after_discount=0.9,DE_ad_id=33333, \
                                if_buy=True,total_price_tracked=7000) # 8100
        
        
        # DE_CLICK_DATA
        de_click_sina1_61 = DE_ClickData.objects.create(ad=self.ad_lenovo1,media=self.sina,channel=self.sina_ch1, \
                                media_ad_info=self.sina_mai1,flight=self.sina_flight1, cpm=0,eventtype=4, eventcount=100, \
                                date=datetime.date(2009,6,1), if_planned_spending=True)
        de_click_sina1_62 = DE_ClickData.objects.create(ad=self.ad_lenovo1,media=self.sina,channel=self.sina_ch1, \
                                media_ad_info=self.sina_mai1,flight=self.sina_flight1, cpm=0,eventtype=4, eventcount=200, \
                                date=datetime.date(2009,6,2), if_planned_spending=True)

        de_click_sina1_63 = DE_ClickData.objects.create(ad=self.ad_lenovo1,media=self.sina,channel=self.sina_ch1, \
                                media_ad_info=self.sina_mai1,flight=self.sina_flight1, cpm=0,eventtype=4, eventcount=300, \
                                date=datetime.date(2009,6,3), if_planned_spending=True)
        
        de_click_sina2_63 = DE_ClickData.objects.create(ad=self.ad_lenovo1,media=self.sina,channel=self.sina_ch1, \
                                media_ad_info=self.sina_mai1,flight=self.sina_flight2, cpm=0,eventtype=4, eventcount=400, \
                                date=datetime.date(2009,6,3), if_planned_spending=True)
        
        
        de_click_sina2_64 = DE_ClickData.objects.create(ad=self.ad_lenovo1,media=self.sina,channel=self.sina_ch1, \
                                media_ad_info=self.sina_mai1,flight=self.sina_flight2, cpm=0,eventtype=4, eventcount=500, \
                                date=datetime.date(2009,6,4), if_planned_spending=True)

        de_click_sina2_65 = DE_ClickData.objects.create(ad=self.ad_lenovo1,media=self.sina,channel=self.sina_ch1, \
                                media_ad_info=self.sina_mai1,flight=self.sina_flight2, cpm=0,eventtype=4, eventcount=600, \
                                date=datetime.date(2009,6,5), if_planned_spending=True)
                                
        de_click_sohu1_61 = DE_ClickData.objects.create(ad=self.ad_lenovo1,media=self.sina,channel=self.sina_ch1, \
                                media_ad_info=self.sina_mai1,flight=self.sohu_flight1, cpm=0,eventtype=4, eventcount=100, \
                                date=datetime.date(2009,6,1), if_planned_spending=True)
        de_click_sohu1_62 = DE_ClickData.objects.create(ad=self.ad_lenovo1,media=self.sina,channel=self.sina_ch1, \
                                media_ad_info=self.sina_mai1,flight=self.sohu_flight1, cpm=0,eventtype=4, eventcount=200, \
                                date=datetime.date(2009,6,2), if_planned_spending=True)

        de_click_sohu1_63 = DE_ClickData.objects.create(ad=self.ad_lenovo1,media=self.sina,channel=self.sina_ch1, \
                                media_ad_info=self.sina_mai1,flight=self.sohu_flight1, cpm=0,eventtype=4, eventcount=300, \
                                date=datetime.date(2009,6,3), if_planned_spending=True)

        #self.ad_lenovo1._init()
    """   
    def test_get_mediareco(self):
        response = self.client.get('/ad-res-mgmt/media_reco/',  {'start_day': '', 'end_day': '', 'target':'cpc', \
                            'level':'media', 'num':5, 'cat_id':'a-21', 'clients_list':[u'佳能',] })
                            
        #self.assertEqual(response.status_code,'200')
        self.assertEqual(self.sina.c_name,'sina')
    """
    
    def test_ad_media(self):
        self.assertEqual(self.ad_lenovo1._campaign_media(), [u'sina', u'sohu'])
    
    def test_media_click(self):
        self.assertEqual(self.ad_lenovo1.media_click(), [7000, 5000])
    
    def test_media_price(self):
        self.assertEqual(self.ad_lenovo1.media_price(), ([8000*0.9+7000*0.8, 8000*0.9], [5000*0.9+6000*0.8, 7000*0.9]))
    
    def test_media_cpc(self):
        self.ad_lenovo1._init()
        self.assertEqual(["%.2f" % mc for mc in self.ad_lenovo1.media_cpc()], ["%.2f" % 1.33, '1.26'])
    
    def test_daily_click(self):
        self.assertEqual(self.ad_lenovo1.daily_click(), [200,400,1000,500,600])
    
    def test_daily_price(self):
        self.assertEqual(self.ad_lenovo1.daily_price(), [15300, 15300, 20900, 5600, 5600])
        
    def test_daily_cpc(self):
        self.ad_lenovo1._init()
        self.assertEqual(self.ad_lenovo1.daily_cpc(), [15300*1.0/200, 15300*1.0/400, 20900*1.0/1000,5600*1.0/500, 5600*1.0/600])
        
    def test_media_daily_click(self):
        self.ad_lenovo1._init()
        self.assertEqual(self.ad_lenovo1.media_daily_click(), [15300*1.0/200, 15300*1.0/400, 20900*1.0/1000,5600*1.0/500, 5600*1.0/600])
        