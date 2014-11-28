#! /usr/bin/env python
#coding=utf-8
from __future__ import division

import re,datetime,os
from os import remove
import Image, ImageColor
from StringIO import StringIO
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.utils import simplejson as json
from django.template import RequestContext
from django.contrib.auth.models import Group
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse
from django.utils.encoding import smart_str, smart_unicode
from django.conf import settings

from MediaChooser.ad.models import ActivityType, Ad, AdCreative
from MediaChooser.client.models import Client
from MediaChooser.media_planning.forms import *
from MediaChooser.media_planning.models import Flight, DE_ClickData
from MediaChooser.utility import get_object_or_error
from MediaChooser.utility.OpenFlashChart import Chart, Bar, Bar_Glass, Line, Line_Dot, Line_Hollow,Bar_3d
from MediaChooser.media.models import MediaAdInfo
from MediaChooser.ad_resource_mgmt.chart import write_amdata_xml, write_dict_xml, write_ampie_xml, write_bar_xml, _sort_dict_by_value
from MediaChooser.user_behaviour.models import UserBehaviour 
#from MediaChooser.ad_resource_mgmt.utils import group_permission
import logging
from pyExcelerator import *
import pyodbc
#from datetime import datetime   
 
effictive_count = 10
dc_click_eventtype = 4
max_label_length = 38
date_no_year = lambda x: ('-').join(str(x).split('-')[1:])
cpc_color, click_color, media_price_color, weekend_color, campaign_cpc_color = '#0f70d3', '#92D050', "#0f70d3", '#9A0000', '#BF3EFF'

# 自定义decorator:判断操作创意者是不是长传排期的人
def isUploader(func):
    def new_func(*kwds, **dic):
        request = kwds[0]
        user = request.user
        campaign = Ad.objects.get(DE_campaign_id=request.POST['campaign_id'])
        if user == campaign.uploader:
            return func(*kwds, **dic)
        else:
            return HttpResponse('fail')
    return new_func

@login_required
def search(request):
    return render_to_response('ad_resource_mgmt/search.html', locals(), context_instance=RequestContext(request))

@login_required
def update_background_code(request):
    campaign_id = request.GET['campaign_id']
    try:
        de_db = pyodbc.connect('DRIVER={Oracle};SERVER=211.94.190.64;DATABASE=dart;UID=mediachooser_read;PWD=read_mediachooser;')
        sql = 'select a.flightid, a.clickurl from admanager65.ng_ads a, admanager65.ng_flights b where a.flightid=b.id and b.orderid=%s' % int(campaign_id)
        de_cursor = de_db.cursor()
        try:
            de_cursor.execute(sql)
        except Exception, e:
            print e
        for row in de_cursor:
            try:
                flight = Flight.objects.get(DE_flight_id = row[0])
                flight.clickurl = row[1]
                flight.save()
            except Flight.DoesNotExist:
                print 'flight not found'
    except Exception, e:
        print e
        return HttpResponse(json.dumps({'result': 'fail'}), mimetype="json")
    finally:
        de_cursor.close()
    return HttpResponse(json.dumps({'result': 'success'}), mimetype="json")

@login_required
def query(request, form_class=MP_SFlight_Form, mform_class=MP_MFlights_Form):
    # Edited by hudie @ 20100513. Added log.
    logging.info('id:' + str(request.user.id) + ' username: ' + request.user.username)
    if request.GET.has_key('cid'):
        cid = request.GET['cid']
        try:
            campaign = Ad.objects.get(DE_campaign_id= cid)
        except Ad.DoesNotExist:
            return HttpResponse(json.dumps({'url':False}), mimetype="json")
        
        user_group_ids = [ g.id for g in request.user.groups.all() ]
        if campaign.group_id not in user_group_ids and campaign.group_id != -1:
            return HttpResponse(json.dumps({'url':'noperm'}), mimetype="json")
        return HttpResponse(json.dumps({'url':"campaign/%s/" % cid}), mimetype="json")
    else:
        form = form_class()
        form_m = mform_class()
        return render_to_response('ad_resource_mgmt/mp_query.html', locals(), context_instance=RequestContext(request))

@login_required
def get_campaign(request, campaign_id):
    cpc_date_data = {}
    cpc_date = []
    media = set()
    
    campaign_id = int(campaign_id)
    try:
        campaign = Ad.objects.get(DE_campaign_id= campaign_id)
    except Ad.DoesNotExist:
        return HttpResponse(json.dumps({'success':False}), mimetype="json")
        
    #campaign._init()
    
    user_group_ids = [ g.id for g in request.user.groups.all() ]
    if campaign.group_id not in user_group_ids and campaign.group_id != -1:
        return render_to_response('ad_resource_mgmt/error.html', {'message':u'您没有权限查看此页面'}, context_instance=RequestContext(request))
    
    flights = Flight.objects.select_related('media').filter(DE_campaign_id= int(campaign_id))
    related_staff = campaign.related_staff.all()
    
    de_data = DE_ClickData.objects.select_related('flight__media').filter(flight__in= flights).order_by('date')
    for d in de_data:
        if str(d.date) not in cpc_date_data:
            cpc_date_data[str(d.date)] = {}
    
    campaign_cpc = ['%.2f' % campaign.cpc] * len(campaign.date_range)
    real_price = int(campaign.cpc * campaign.click)
    
    for f in flights:
        media.add(f.media.c_name)
        for d in cpc_date_data:
            cpc_date_data[d][f.media.c_name] = {}
            cpc_date_data[d][f.media.c_name]['price'] = 0
            cpc_date_data[d][f.media.c_name]['click'] = 0

    for d in de_data:
        f = d.flight
        if f.unit == 'CPM':
            if d.eventcount > effictive_count and d.eventtype == dc_click_eventtype:
                cpc_date_data[str(d.date)][f.media.c_name]['click'] += d.eventcount
            if f.if_buy and d.if_planned_spending:
                cpc_date_data[str(d.date)][f.media.c_name]['price'] = f.unit_price * d.cpm *f.discount_after_discount
        else:
            if d.eventcount > effictive_count and d.eventtype == dc_click_eventtype:
                cpc_date_data[str(d.date)][f.media.c_name]['click'] += d.eventcount
            if f.if_buy and d.if_planned_spending:
                cpc_date_data[str(d.date)][f.media.c_name]['price'] += f.unit_price * f.discount_after_discount 

    keys = cpc_date_data.keys()
    keys.sort()
    click_data = []
    for d in keys:
        tmp_total_price = 0
        tmp_total_click = 0
        for m in cpc_date_data[d]:
            tmp_total_price += cpc_date_data[d][m]['price']
            tmp_total_click += cpc_date_data[d][m]['click']
        
        if tmp_total_click == 0:
            click_data.append(None)
        else:
            click_data.append(tmp_total_click)
                    
        if tmp_total_click != 0:
            if tmp_total_price*1.0/tmp_total_click == 0:
                cpc_date.append(None)
            else:
                cpc_date.append(tmp_total_price*1.0/tmp_total_click)
        else:
            cpc_date.append(None)
    #cpc_date_chart = _get_cpc_date_chart(cpc_date, click_data, keys, campaign_cpc, campaign.end_day ,campaign.start_day)

    #cpc_media_chart = _get_cpc_media_chart(campaign.media_cpc(), campaign.media_click(), campaign.media)
    #cpc_media_linechart = _get_cpc_media_linechart(campaign.media_cpc(), campaign.media_click(), campaign.media)
    #price_media_chart = _get_price_media_chart(campaign.media_price()[0], campaign.media)
    
    #write_amdata_xml(campaign.date_range, campaign.daily_cpc(), campaign.daily_click(), campaign_cpc, 'cpc_date.xml', True)
    #print keys, campaign.date_range
    write_amdata_xml(keys, cpc_date, click_data, campaign_cpc, 'cpc_date.xml', True)
    
    
    #write_amdata_xml(cpc_media_data.keys(), cpc_media, None, None, 'cpc_media.xml')
    #write_ampie_xml(cpc_media_data.keys(), media_price, 'price_media.xml')
    #write_ampie_xml(campaign.media, campaign.media_price()[0], 'price_media.xml')
    
    # cpc_media_comp_chart
    tmp_media_cpc = {}
    tmp_media_click = {}
    for m in media:
        tmp_list = []
        tmp_click_list = []
        for d in keys:
#            print d
#            now = datetime.today().date()
            click = cpc_date_data[d][m]['click']
            price = cpc_date_data[d][m]['price']
            if click != 0:
                if price*1.0/click == 0:
                    tmp_list.append(None)
                else:
                    tmp_list.append(price*1.0/click)
                tmp_click_list.append(click)
            else:
                tmp_list.append(None)
                tmp_click_list.append(None)
        tmp_media_cpc[m] = tmp_list
        tmp_media_click[m] = tmp_click_list
    #cpc_media_comp = _get_cpc_media_comp_chart(tmp_media_cpc, keys, campaign.end_day ,campaign.start_day)
    write_dict_xml(keys, tmp_media_cpc, 'cpc_media_comp.xml', True)
    write_dict_xml(keys, tmp_media_click, 'click_media_comp.xml', True)
    ##########  user behaviour data  ##########
    tracking = ''
    ubs = None
    if campaign.client.c_name == u'联想':
        tracking = 'om'
        ubs = UserBehaviour.objects.om_report(campaign_id)
    else:
        tracking = 'ga'
        ubs = UserBehaviour.objects.ga_report(campaign_id)
        
#    显示广告创意
    ad_creatives = AdCreative.objects.filter(ad=campaign)
    for creative in ad_creatives:
        postfix = creative.creative.name.split('.')[1]
        if postfix in ['swf', 'fla']:
            creative.is_flash = True
        else:
            creative.is_flash = False
    return render_to_response('ad_resource_mgmt/mp_sflight.html', locals(), context_instance=RequestContext(request))

def get_campaign_status(request, ad_id):
    import pyodbc
    today = datetime.date.today()
    de_db = pyodbc.connect('DRIVER={Oracle};SERVER=211.94.190.64;DATABASE=dart;UID=mediachooser_read;PWD=read_mediachooser;')
    sql = 'select flightid, sum(eventcount) from admanager65.ng_sum_fixed_c where startdate=to_date(\'%s\', \'YYYY-MM-DD\') and eventtype=4 group by flightid' % today
    de_cursor = de_db.cursor()
    de_cursor.execute(sql)
    flights_clicks = {}
    for row in de_cursor:
        eventcount = int(row[1]*settings.CLICK_COMPENSATION_COEFFICIENT)
        flights_clicks[int(row[0])] = eventcount

    #current_flights = Flight.objects.filter(start_day__lt=today, end_day__gt=today)

    """
    from django.db import connection
    cursor = connection.cursor()
    print tuple([c.id for c in current_flights])

    sql = "SELECT id, ad_id, media_id, channel_id, media_ad_info_id, flight_id,  cpm, eventtype, eventcount, \
        date, if_planned_spending  FROM media_planning_de_clickdata where flight_id \
        in %s and date in %s and eventtype=4" % (tuple([c.id for c in current_flights]), (str(today),str(today-datetime.timedelta(days=1)),str(today-datetime.timedelta(days=2)),str(today-datetime.timedelta(days=3))));

    print sql

    cursor.execute(sql)
    rows = cursor.fetchall()
    print len(rows)
    """
    ad_id = int(ad_id)
    if ad_id == 0:
        today_de = DE_ClickData.objects.filter(date=today, if_planned_spending=True)
    else:
        today_de = DE_ClickData.objects.filter(date=today, if_planned_spending=True, flight__DE_campaign_id=ad_id)

    today_flights = [de.flight.id for de in today_de]
    de_click_data = DE_ClickData.objects.select_related('flight','media__c_name','channel__c_name','media_ad_info__adform').filter(flight__id__in=today_flights, date__range=(today-datetime.timedelta(days=7),today)).order_by('flight')

    click_data = {}
    data = []
    for c in de_click_data:
        key = '%s' % c.flight.DE_campaign_id + '^-^' +c.media.c_name + '^-^' + c.channel.c_name + '^-^' + c.media_ad_info.adform
        if key not in click_data:
            click_data[key] = {}

        if c.date == today-datetime.timedelta(days=1):
            click_data[key]['day1'] = {}
            click_data[key]['day1']['click'] = c.eventcount
            click_data[key]['day1']['if_planned'] = c.if_planned_spending
        if c.date == today-datetime.timedelta(days=2):
            click_data[key]['day2'] = {}
            click_data[key]['day2']['click'] = c.eventcount
            click_data[key]['day2']['if_planned'] = c.if_planned_spending
        if c.date == today-datetime.timedelta(days=3):
            click_data[key]['day3'] = {}
            click_data[key]['day3']['click'] = c.eventcount
            click_data[key]['day3']['if_planned'] = c.if_planned_spending
        if c.date == today-datetime.timedelta(days=4):
            click_data[key]['day4'] = {}
            click_data[key]['day4']['click'] = c.eventcount
            click_data[key]['day4']['if_planned'] = c.if_planned_spending
        if c.date == today-datetime.timedelta(days=5):
            click_data[key]['day5'] = {}
            click_data[key]['day5']['click'] = c.eventcount
            click_data[key]['day5']['if_planned'] = c.if_planned_spending
        if c.date == today-datetime.timedelta(days=6):
            click_data[key]['day6'] = {}
            click_data[key]['day6']['click'] = c.eventcount
            click_data[key]['day6']['if_planned'] = c.if_planned_spending
        if c.date == today-datetime.timedelta(days=7):
            click_data[key]['day7'] = {}
            click_data[key]['day7']['click'] = c.eventcount
            click_data[key]['day7']['if_planned'] = c.if_planned_spending

        click_data[key]['media'] = c.media
        click_data[key]['media_ad_info'] = c.media_ad_info
        click_data[key]['channel'] = c.channel
        click_data[key]['campaign'] = c.flight.DE_campaign_id
        click_data[key]['price'] = c.flight.unit_price
        try:
            click_data[key]['today'] = flights_clicks[c.flight.DE_flight_id]
        except KeyError:
            click_data[key]['today'] = 0

    keys = click_data.keys()
    keys.sort(KeySort)
    for k in keys:
        data.append(click_data[k])

    return render_to_response('ad_resource_mgmt/mp_flights_status.html', locals(), context_instance=RequestContext(request))
@isUploader
@login_required
def upload_creative(request):
    campaign_id =  request.POST['campaign_id']
    ad = Ad.objects.get(DE_campaign_id=int(campaign_id))
    upload_creative_file = request.FILES['creative_file']

    ad_creative = AdCreative.objects.create(ad=ad, creative=upload_creative_file)
    return HttpResponse('success')

@isUploader
@login_required
def delete_upload_creative(request):
    campaign_id =  request.POST['campaign_id']
    creative_file_name = request.POST['creative_file_name']
    ad = Ad.objects.get(DE_campaign_id=int(campaign_id))
    creatives = AdCreative.objects.filter(ad=ad)
    for creative in creatives:
        if creative.creative.name == creative_file_name:
            creative.delete()
            break
    return HttpResponse('success')

@login_required
def get_campaign_detail(request, campaign_id):
    campaign_id = int(campaign_id)
    result = Ad.objects.get(DE_campaign_id= campaign_id).campaign_detail()
    return render_to_response('ad_resource_mgmt/mp_sflight_detail.html',locals(), context_instance=RequestContext(request))

@login_required
def get_campaign_detail_date_cpc(request, campaign_id):
    campaign_id = int(campaign_id)
    result = Ad.objects.get(DE_campaign_id= campaign_id).campaign_detail()
    return render_to_response('ad_resource_mgmt/datecpc_click_detail.html',locals(), context_instance=RequestContext(request))
    
@login_required   
def get_campaign_detail_media_cpc(request, campaign_id):
    campaign_id = int(campaign_id)
    campaign = Ad.objects.get(DE_campaign_id= campaign_id)
    campaign._init()
    media_cpc = campaign.media_cpc()
    media_click = campaign.media_click()
    result = {}
    for media in media_cpc:
        result[media] = []
        result[media].append('%0.2f'%media_cpc[media])
        result[media].append(media_click[media])
    return render_to_response('ad_resource_mgmt/mediacpc_detail.html',locals(), context_instance=RequestContext(request))

@login_required 
def get_campaign_detail_price_media(request, campaign_id):
    campaign_id = int(campaign_id)
    campaign = Ad.objects.get(DE_campaign_id= campaign_id)
    campaign._init()
    media_price = campaign.media_price()[0]
    count = 0
    for media in media_price:
       count = count + media_price[media]
    result = {}
    for media in media_price:
       result[media] = []
       result[media].append(media_price[media])
       result[media].append('%0.2f' %(media_price[media]/count*100) + '%')
    return render_to_response('ad_resource_mgmt/pricemedia_detail.html',locals(), context_instance=RequestContext(request))

@login_required
def get_campaign_detail_funnel(request, campaign_id):
    campaign_id = int(campaign_id)
    campaign = Ad.objects.get(DE_campaign_id= campaign_id)
    ubs = None
    if campaign.client.c_name == u'联想':
        tracking = 'om'
        ubs = UserBehaviour.objects.om_report(campaign_id)
    else:
        tracking = 'ga'
        ubs = UserBehaviour.objects.ga_report(campaign_id)
    return render_to_response('ad_resource_mgmt/funnel_detail.html',locals(), context_instance=RequestContext(request))  
 
@login_required
def get_campaign_xls(request, campaign_id):
    campaign_id = int(campaign_id)
    campaign = Ad.objects.get(DE_campaign_id=campaign_id)
    campaign_name = campaign.name
    result = campaign.campaign_detail()

    workbook = Workbook()
    worksheet = workbook.add_sheet(u'MediaChooser排期详细报告')
   
    col_name = [u'媒体',u'频道',u'广告位',u'投放金额',u'点击数',u'是否购买',u'开始时间',u'结束时间']
    #xls_dir = '/tmp/xls_dir4mc/'
    tmp_fn = '%s.xls' % campaign_id

    for i, j in enumerate(col_name):
        worksheet.write(0,i,j)
    
    row_num = 1
    for r in result:
        #for adform in adform_data[media]:
        worksheet.write(row_num, 0, r['media'])
        worksheet.write(row_num, 1, r['channel'])
        worksheet.write(row_num, 2, r['adform'])
        worksheet.write(row_num, 3, r['price'])
        worksheet.write(row_num, 4, r['click'])
        
        if r['if_buy'] == True:
            worksheet.write(row_num, 5, u'是')
        else:
            worksheet.write(row_num, 5, u'否')
            
        worksheet.write(row_num, 6, str(r['start_day']))
        worksheet.write(row_num, 7, str(r['end_day']))
            
        row_num += 1
                    
    workbook.save(tmp_fn)
    data = open(tmp_fn).read()
    remove(tmp_fn)

    response = HttpResponse(data, mimetype='application/msexcel')
    response['Content-Disposition'] = 'attachment; filename=mediachooser%s.xls' %  str(campaign_id) 
    return response

@login_required
def get_campaign_media_price_xls(request, campaign_id):
    campaign_id = int(campaign_id)
    campaign = Ad.objects.get(DE_campaign_id= campaign_id)
    campaign._init()
    media_price = campaign.media_price()[0]
    count = 0
    for media in media_price:
       count = count + media_price[media]
    book = Workbook()
    worksheet = book.add_sheet(u'排期%s的媒体投放量'% str(campaign_id))
    col_name = [u'媒体',u'投放量',u'百分比']
    tmp_fn = '%s.xls' % campaign_id

    for i, j in enumerate(col_name):
        worksheet.write(0,i,j)
    row_num = 1
    for media in media_price:
        worksheet.write(row_num, 0, media)
        worksheet.write(row_num, 1, media_price[media])
        worksheet.write(row_num, 2, '%0.2f' %(media_price[media]/count*100) + '%')
        row_num = row_num + 1
    book.save(tmp_fn)
    data = open(tmp_fn).read()
    remove(tmp_fn)
    
    response = HttpResponse(data, mimetype='application/msexcel')
    response['Content-Disposition'] = 'attachment; filename=mediachooser%s的媒体投放量.xls' %  str(campaign_id) 
    return response

@login_required
def get_campaign_media_cpc_xls(request, campaign_id):
    campaign_id = int(campaign_id)
    campaign = Ad.objects.get(DE_campaign_id= campaign_id)
    campaign._init()
    media_cpc = campaign.media_cpc()
    media_click = campaign.media_click()
    tmp_fn = '%s.xls' % campaign_id
    book = Workbook()
    sheet = book.add_sheet(u'排期%s的媒体效果'% str(campaign_id))
    col_name = [u'媒体', 'cpc', 'click']
    for pos, val in enumerate(col_name):
        sheet.write(0, pos, val)
    row_number = 1
    for media in media_cpc:
        sheet.write(row_number, 0, media)
        sheet.write(row_number, 1, '%0.2f'%media_cpc[media])
        sheet.write(row_number, 2, media_click[media])
        row_number = row_number + 1
    book.save(tmp_fn)
    data = open(tmp_fn).read()
    remove(tmp_fn)
    response = HttpResponse(data, mimetype='application/msexcel')
    response['Content-Disposition'] = 'attachment; filename=mediachooser%s的媒体效果.xls' %  str(campaign_id) 
    return response

    
@login_required
def get_campaign_funel_xls(request, campaign_id):
    campaign_id = int(campaign_id)
    campaign = Ad.objects.get(DE_campaign_id= campaign_id)
    ubs = None
    if campaign.client.c_name == u'联想':
        tracking = 'om'
        ubs = UserBehaviour.objects.om_report(campaign_id)
    else:
        tracking = 'ga'
        ubs = UserBehaviour.objects.ga_report(campaign_id)
    book = Workbook()
    sheet = book.add_sheet(u'排期%s的漏斗图'% str(campaign_id))
    col_name_1 = [u'媒体', u'点击数据', u'用户行为数据']
    col_name_2= [u'媒体', u'频道', u'广告位', u'前点击', 'visits', u'流失率', 'PageViews', u'平均停留时长(秒)', u'跳出率', 'tracking_code']
    col_name_3= [u'媒体', u'频道', u'广告位', u'前点击', 'visits', u'流失率', 'PageViews', 'ub', u'产品详情页', u'购物车', 'checkout', 'order', 'revenue', 'tracking code']
    sheet.write_merge(0,0,0,2, col_name_1[0])
    sheet.write_merge(0,0,3,5, col_name_1[1])
    if tracking == 'ga':
        sheet.write_merge(0,0,6,9, col_name_1[2])
        for pos, val in enumerate(col_name_2):
            sheet.write(1, pos, val)
    if tracking == 'om':
        sheet.write_merge(0,0,6,13, col_name_1[2])
        for pos, val in enumerate(col_name_3):
            sheet.write(1, pos, val)
    row_number = 2
    for res in ubs:
        sheet.write(row_number, 0, res['media'])
        sheet.write(row_number, 1, res['channel'])
        sheet.write(row_number, 2, res['adform'])
        sheet.write(row_number, 3, res['click'])
        sheet.write(row_number, 4, str(res['visits']))
        sheet.write(row_number, 5, str(res['loss']) + '%')
        sheet.write(row_number, 6, str(res['pv']))
        if tracking == 'ga':
            sheet.write(row_number, 7, res['avg_time'])
            sheet.write(row_number, 8, str(res['bounce_rate'])+'%')
            sheet.write(row_number, 9, res['tracking_code'])
        if tracking == 'om':
            sheet.write(row_number, 7, str(res['uv']))
            sheet.write(row_number, 8, str(res['products_view']))
            sheet.write(row_number, 9, str(res['cart_addition']))
            sheet.write(row_number, 10, str(res['checkouts']))
            sheet.write(row_number, 11, str(res['orders']))
            sheet.write(row_number, 12, str(res['revenue']))
            sheet.write(row_number, 13, res['tracking_code'])
        row_number = row_number + 1
    tmp_fn = '%s.xls' % campaign_id
    book.save(tmp_fn)
    data = open(tmp_fn).read()
    remove(tmp_fn)
    response = HttpResponse(data, mimetype='application/msexcel')
    response['Content-Disposition'] = 'attachment; filename=mediachooser%s的漏斗图.xls' %  str(campaign_id) 
    return response

@login_required
def query_mflights(request, form_class=MP_MFlights_Form):
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            campaigns = Ad.objects.all().order_by('-start_day')
            
            client = form.cleaned_data['client']
            if client: campaigns = campaigns.filter(client=client)
            
            at = form.cleaned_data['activitytype']
            if at: campaigns = campaigns.filter(activity_type=at)
            
            from django.db.models import Q
            start = form.cleaned_data['start_day']
            end = form.cleaned_data['end_day']
            if start and end:
                 campaigns = campaigns.filter(Q(start_day__gt=start, start_day__lt=end)| Q(end_day__gt=start, end_day__lt=end)| Q(start_day__lt=start, end_day__gt=end))
            elif start:
                campaigns = campaigns.filter(end_day__lte=start_day)
            elif end:
                campaigns = campaigns.filter(start_day__gte=end_day)
            
            campaign_name = form.cleaned_data['campaign_name']
            if campaign_name: campaigns = campaigns.filter(name__contains= campaign_name)
            
        else:
            print "no"
        return render_to_response('ad_resource_mgmt/mp_query_result.html', locals(), context_instance=RequestContext(request))

@login_required
def mflights(request):
    if request.method == 'POST':
        source = request.GET['source']
        campaign_id = [int(c) for c in request.GET['data'].split(',')]
        if source == 'mflights':
            media = []
            cpc_data = {}
            id_dict = {}
            
            ##### generate cpc_data dict ###########
            flights = Flight.objects.select_related('media').filter(DE_campaign_id__in= campaign_id)
            
            for f in flights:
                #c_id = '%s' % f.DE_campaign_id
                c_id = f.ad.name
                m = f.media.domain
                if c_id not in cpc_data:
                    cpc_data[c_id] = {}
                    cpc_data[c_id][m] = {}
                    cpc_data[c_id][m]['click'] = 0
                    cpc_data[c_id][m]['price'] = 0
                elif m not in cpc_data[c_id]:
                    cpc_data[c_id][m] = {}
                    cpc_data[c_id][m]['click'] = 0
                    cpc_data[c_id][m]['price'] = 0
                
                id_dict[c_id] = f.DE_campaign_id
            
            ids = [f.id for f in flights]
            de_data = DE_ClickData.objects.select_related('flight','media').filter(flight__id__in= ids)
            
            for d in de_data:
                f = d.flight
                #c_id = '%s' % f.DE_campaign_id
                c_id = f.ad.name
            
                if f.unit == 'CPM':
                    if d.eventcount > 10 and d.eventtype == 4:
                        cpc_data[c_id][d.media.domain]['click'] += d.eventcount
                        if f.if_buy:
                            cpc_data[c_id][d.media.domain]['price'] += f.unit_price * d.cpm * f.discount_after_discount
                else:
                    if d.eventcount > 10 and d.eventtype == 4:
                        cpc_data[c_id][d.media.domain]['click'] += d.eventcount
                        if f.if_buy:
                            cpc_data[c_id][d.media.domain]['price'] += f.unit_price * f.discount_after_discount
            
            keys = cpc_data.keys()
            #keys.sort()
            cpc_mflights = []
            click_mflights = []
            for k in keys:
                tmp_total_price = 0
                tmp_total_click = 0
                for m in cpc_data[k]:
                    tmp_total_price += cpc_data[k][m]['price']
                    tmp_total_click += cpc_data[k][m]['click']

                if tmp_total_click == 0:
                    cpc_mflights.append(0)
                else:
                    cpc_mflights.append(tmp_total_price*1.0/tmp_total_click)
                click_mflights.append(tmp_total_click)
            cpc_mflights_chart = _get_mflights_chart(cpc_mflights, click_mflights, id_dict)    
            #cpc_mflights_chart = _get_mutil_media_chart(cpc_mflights, click_mflights, keys)
            return render_to_response('ad_resource_mgmt/mp_mflights.html', locals(), context_instance=RequestContext(request))

        elif source == 'media':
            media_tree = {}
            for c_id in campaign_id:
                flights = Flight.objects.select_related('media').filter(DE_campaign_id= int(c_id))
                for f in flights:
                    if f.media.c_name in media_tree:
                        if f.channel.c_name in media_tree[f.media.c_name]:
                            media_tree[f.media.c_name][f.channel.c_name].append(f.media_ad_info.adform)
                        else:
                            media_tree[f.media.c_name][f.channel.c_name] = []
                            media_tree[f.media.c_name][f.channel.c_name].append(f.media_ad_info.adform)
                    else:
                        media_tree[f.media.c_name] = {}
                        media_tree[f.media.c_name][f.channel.c_name] = []
                        media_tree[f.media.c_name][f.channel.c_name].append(f.media_ad_info.adform)

            init_data = empty_chart()
            
            return render_to_response('ad_resource_mgmt/mp_mediaeffect.html', locals(), context_instance=RequestContext(request))

        elif source == 'date':
            cpc_date_data = {}
            start = datetime.date(3000,1,1)
            end = datetime.date(1,1,1)
            '''
            campaigns = Ad.objects.filter(DE_campaign_id__in= campaign_id)
            for c in campaigns:
                start_day, end_day = c.start_day, c.end_day
                if start_day < start:
                    start = start_day
                if end_day > end:
                    end = end_day
            
            for d in range((end - start).days + 1):
                day = start + datetime.timedelta(days=d)
                cpc_date_data[str(day)] = {}
                cpc_date_data[str(day)]['click'] = 0
                cpc_date_data[str(day)]['price'] = 0
            '''
            flights = Flight.objects.filter(DE_campaign_id__in= campaign_id)
            for f in flights:
                if f.unit == 'CPM':
                    de_data = DE_ClickData.objects.filter(flight= f)
                    for d in de_data:
                        if d.eventcount > 10 and d.eventtype == 4:
                            if str(d.date) in cpc_date_data:
                                cpc_date_data[str(d.date)]['click'] += d.eventcount
                                if f.if_buy:
                                    cpc_date_data[str(d.date)]['price'] += f.unit_price * d.cpm
                            else:
                                cpc_date_data[str(d.date)] = {}
                                cpc_date_data[str(d.date)]['click'] = 0
                                cpc_date_data[str(d.date)]['price'] = 0
                else:
                    de_data = DE_ClickData.objects.filter(flight= f)
                    for d in de_data:
                        if d.eventcount > 10 and d.eventtype == 4:
                            if str(d.date) in cpc_date_data:   
                                cpc_date_data[str(d.date)]['click'] += d.eventcount
                        
                                if f.if_buy:
                                    cpc_date_data[str(d.date)]['price'] += f.unit_price
                            else:
                                cpc_date_data[str(d.date)] = {}
                                cpc_date_data[str(d.date)]['click'] = 0
                                cpc_date_data[str(d.date)]['price'] = 0
                                
            keys = cpc_date_data.keys()
            keys.sort()
            cpc_date = []
            click_data = []
            for d in keys:
                if cpc_date_data[d]['click'] == 0:
                    click_data.append(None)
                else:
                    click_data.append(cpc_date_data[d]['click'])
                if cpc_date_data[d]['click'] == 0:
                    cpc_date.append(None)
                else:
                    cpc_date.append(cpc_date_data[d]['price']*1.0/ cpc_date_data[d]['click'])
            cpc_date_chart = _get_cpc_date_chart(cpc_date, click_data, keys, None, end, start)
            write_amdata_xml(keys, cpc_date, click_data, None, 'cpc_timeseries.xml', True)
            return render_to_response('ad_resource_mgmt/mp_timeseries.html', locals(), context_instance=RequestContext(request))

@login_required
def query_media(request):

    get = request.GET
    if get.has_key('media_list') and get.has_key('channel_list') and get.has_key('flight_list') and get.has_key('campaign_id'):
        
        media_list = get['media_list'].split('|')
        channel_list = get['channel_list'].split('|')
        flight_list = get['flight_list'].split('|')
        campaign_id = get['campaign_id'].split(',')

        data = {}
        cpc = {}

        if not media_list == ['']:
            for m in media_list:
                data[m] = {}
                flights = Flight.objects.filter(DE_campaign_id__in= campaign_id, media__c_name=m)
                
                for f in flights:
                    try:
                        data[m]['price'] += f.cpc * f.click
                        data[m]['click'] += f.click
                    except KeyError:
                        data[m]['price'] = f.cpc * f.click
                        data[m]['click'] = f.click
                
                if data[m]['click'] != 0:
                    cpc[m] = data[m]['price'] / data[m]['click']
                else:
                    cpc[m] = 0
        
        if not channel_list == ['']:
            for c in channel_list:
                media_name, channel_name = c.split('->')[0], c.split('->')[1]
                channel = media_name + '<br>' + channel_name
                data[channel] = {}
                flights = Flight.objects.filter(DE_campaign_id__in= campaign_id, media__c_name=media_name, channel__c_name=channel_name)
                for f in flights:
                    try:
                        data[channel]['price'] += f.cpc * f.click
                        data[channel]['click'] += f.click
                    except KeyError:
                        data[channel]['price'] = f.cpc * f.click
                        data[channel]['click'] = f.click
                
                if data[channel]['click'] == 0:
                    cpc[channel] = 0
                else:
                    cpc[channel] = data[channel]['price'] / data[channel]['click']   

        if not flight_list == ['']:
            for fl in flight_list:
                media_name, channel_name, adform_name = fl.split('->')
                fl = media_name + '<br>' + channel_name + '<br>' + adform_name
                data[fl] = {}
                fli = fl.split('-')[-1]
                flights = Flight.objects.filter(DE_campaign_id__in= campaign_id, media_ad_info__adform=adform_name)
                
                for f in flights:
                    try:
                        data[fl]['price'] += f.cpc * f.click
                        data[fl]['click'] += f.click
                    except KeyError:
                        data[fl]['price'] = f.cpc * f.click
                        data[fl]['click'] = f.click
                
                if data[fl]['click'] == 0:
                    cpc[fl] = 0
                else:
                    cpc[fl] = data[fl]['price'] / data[fl]['click']
        
        multi_media_chart = _get_mutil_media_chart(cpc)
        write_bar_xml(cpc, 'mflights_cpc_media.xml')
        return HttpResponse(multi_media_chart)
    else:
        return HttpResponse('missing parameters')
        
@login_required
def media_filter(request, form_class=MP_MediaFilter_Form):
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            pass
    else:
        form = form_class()
        clients_dict = Client.objects.get_clients_dict()
        init_data = empty_chart()
        return render_to_response('ad_resource_mgmt/mp_mediafilter.html',{'init_data':init_data,'form':form, 'clients_dict':clients_dict}, context_instance=RequestContext(request))

def get_mediatree(request):
    if request.method == 'POST':
        post = request.POST
        if post.has_key('clients_list') and post.has_key('start_day') and post.has_key('end_day'):
            #industry_name_list = get['industry_list'].split(',')
            clients_name_list = post['clients_list'].split(',')
            start,end = _transDate(post['start_day'], post['end_day'])

            from django.db.models import Q
            media = set()
            
            media_tree = {}
            #flights = Flight.objects.select_related('ad__client','media_ad_info__media__first_category',\
            #'media_ad_info__media__second_category','media__first_category','media_second_category','channel').\
            #filter(Q(start_day__gt=start, start_day__lt=end)| Q(end_day__gt=start, end_day__lt=end)| Q(start_day__lt=start, end_day__gt=end), \
            #total_price__gt=0,ad__client__id__in=map(int, clients_name_list))
            
            from django.db import connection
            cursor = connection.cursor()
            
            if clients_name_list != ['']:
                clients = map(int, clients_name_list)
                
            if clients_name_list == ['']:
                sql = "SELECT a.media_id as mediaid, c.c_name as media,(select c_name from media_channel where id = a.channel_id) as channelname,b.adform \
                    FROM media_planning_flight a, media_mediaadinfo b, media_media c \
                    WHERE b.id = a.media_ad_info_id AND a.media_id=c.id AND c.first_category_id is not null \
                    AND ( (a.start_day between \'%s\' and \'%s\') or (a.end_day between \'%s\' and \'%s\') or (a.start_day < \'%s\' and a.end_day > \'%s\') ) \
                    GROUP BY mediaid, media, channelname, b.adform " % (start,end,start,end,start,end)
                
                sql_cate = "SELECT b.c_name as fc, (select c_name from media_mediacategory where id = c.second_category_id) as sc, c.id as mediaid, c.c_name as media\
                    FROM media_planning_flight a, media_mediacategory b, media_media c \
                    WHERE a.media_id = c.id AND c.first_category_id = b.id \
                    AND ( (a.start_day between \'%s\' and \'%s\') or (a.end_day between \'%s\' and \'%s\') or (a.start_day < \'%s\' and a.end_day > \'%s\')) \
                    GROUP BY fc, sc, mediaid, media" % (start,end,start,end,start,end)

            elif len(clients) == 1:
                sql = "SELECT a.media_id as mediaid, c.c_name as media,(select c_name from media_channel where id = a.channel_id) as channelname,b.adform \
                    FROM media_planning_flight a, ad_ad e, media_mediaadinfo b, media_media c \
                    WHERE a.ad_id = e.id  AND e.client_id = %s AND b.id = a.media_ad_info_id AND a.media_id=c.id AND c.first_category_id is not null \
                    AND ( (a.start_day between \'%s\' and \'%s\') or (a.end_day between \'%s\' and \'%s\') or (a.start_day < \'%s\' and a.end_day > \'%s\') ) \
                    GROUP BY mediaid, media, channelname, b.adform " % (clients[0], start,end,start,end,start,end)

                sql_cate = "SELECT b.c_name as fc, (select c_name from media_mediacategory where id = c.second_category_id) as sc, c.id as mediaid, c.c_name as media\
                    FROM media_planning_flight a, media_mediacategory b, media_media c, ad_ad e \
                    WHERE a.media_id = c.id AND c.first_category_id = b.id AND e.id = a.ad_id AND e.client_id = %s \
                    AND ( (a.start_day between \'%s\' and \'%s\') or (a.end_day between \'%s\' and \'%s\') or (a.start_day < \'%s\' and a.end_day > \'%s\')) \
                    GROUP BY fc, sc, mediaid, media" % (clients[0], start,end,start,end,start,end)
            else:
                sql = "SELECT a.media_id as mediaid, c.c_name as media,(select c_name from media_channel where id = a.channel_id) as channelname,b.adform \
                    FROM media_planning_flight a, ad_ad e, media_mediaadinfo b, media_media c \
                    WHERE a.ad_id = e.id  AND e.client_id in %s AND b.id = a.media_ad_info_id AND a.media_id=c.id AND c.first_category_id is not null \
                    AND ( (a.start_day between \'%s\' and \'%s\') or (a.end_day between \'%s\' and \'%s\') or (a.start_day < \'%s\' and a.end_day > \'%s\') ) \
                    GROUP BY mediaid, media, channelname, b.adform " % (tuple(clients), start,end,start,end,start,end)

                sql_cate = "SELECT b.c_name as fc, (select c_name from media_mediacategory where id = c.second_category_id) as sc, c.id as mediaid, c.c_name as media\
                    FROM media_planning_flight a, media_mediacategory b, media_media c, ad_ad e \
                    WHERE a.media_id = c.id AND c.first_category_id = b.id AND e.id = a.ad_id AND e.client_id in %s \
                    AND ( (a.start_day between \'%s\' and \'%s\') or (a.end_day between \'%s\' and \'%s\') or (a.start_day < \'%s\' and a.end_day > \'%s\')) \
                    GROUP BY fc, sc, mediaid, media" % (tuple(clients), start,end,start,end,start,end)
            
            media_cate = {}
            
            cursor.execute(sql_cate)
            rows = cursor.fetchall()
            
            for r in rows:
                fc = r[0]
                sc = r[1]
                media_id = r[2]
                media_cname = r[3]
                if fc == None:
                    fc = u"其它"

                if sc == None:
                    sc = u"其它"
                
                #media = '%s' % media_id + '|' + media_cname
                media = media_cname
                
                media_cate[media] = (fc,sc)
                
                if fc in media_tree:
                    if sc in media_tree[fc]:
                        if media in media_tree[fc][sc]:
                            pass
                        else:
                            media_tree[fc][sc][media] = {}
                    else:
                        media_tree[fc][sc] = {}
                else:
                    media_tree[fc] = {}
                    media_tree[fc][sc] = {}
                    media_tree[fc][sc][media] = {}
                
            import time
            start = time.time()
            end1 = time.time()
            
            #if len(media) == 0:
            #    return HttpResponse(json.dumps({'success':False}), mimetype="json")
            
            cursor.execute(sql)
            rows = cursor.fetchall()

            for r in rows:
                media_id = r[0]
                media_cname = r[1]
                channel_name = r[2]
                #print channel_name
                adform = r[3]
                
                #media = '%s' % media_id + '|' + media_name
                media = media_cname
                fc = media_cate[media][0]
                sc = media_cate[media][1]
                
                if media in media_tree[fc][sc]:
                    if channel_name in media_tree[fc][sc][media]:
                        if adform in media_tree[fc][sc][media][channel_name]:
                            pass
                        else:
                            media_tree[fc][sc][media][channel_name].append(adform)
                    else:
                        media_tree[fc][sc][media][channel_name] = []
                        media_tree[fc][sc][media][channel_name].append(adform)
                else:
                    media_tree[fc][sc][media] = {}
                    media_tree[fc][sc][media][channel_name] = []
                    media_tree[fc][sc][media][channel_name].append(adform)
            
            cursor.close()

            return HttpResponse(json.dumps(media_tree), mimetype="json")

#post数据是用'#$%'连接的，如果采用逗号，可能媒体，频道，广告位名称本身也包含逗号,所以再用逗号分割会出现错误,特意改为三个特殊符号
#子分类的名字是由分类和子分类的名字连接而成，为了避免子分类或者分类本身含有连字符'-'，此处用'$&'连接，频道和广告位同理
def get_mediatree_chart(request):
    if request.method == 'POST':
        post = request.POST
        if post.has_key('media_list') and post.has_key('channel_list') and post.has_key('flight_list') and post.has_key('main_cats_list') and post.has_key('sub_cats_list'):
            main_cats_list = post['main_cats_list'].split('#$%')
            sub_cats_list = post['sub_cats_list'].split('#$%')
            media_list = post['media_list'].split('#$%')
            channel_list = post['channel_list'].split('#$%')
            flight_list = post['flight_list'].split('#$%')
            start,end = _transDate(post['start_day'], post['end_day'])
            
            has_clients = True
            if post['clients_list'] == '':
                has_clients = False
            else:
                clients_list = map(int, post['clients_list'].split('#$%'))
                
            data = {}
            cpc = {}
            
            from django.db.models import Q
            if not main_cats_list == ['']:
                for mc in main_cats_list:
                    if mc == u'全部':
                        if has_clients:
                            flights = Flight.objects.filter(ad__client__id__in=clients_list).filter(Q(start_day__gt=start, start_day__lt=end)| Q(end_day__gt=start, end_day__lt=end)| Q(start_day__lt=start, end_day__gt=end), total_price__gt=0)
                        else:
                            flights = Flight.objects.filter(Q(start_day__gt=start, start_day__lt=end)| Q(end_day__gt=start, end_day__lt=end)| Q(start_day__lt=start, end_day__gt=end), total_price__gt=0)
                        for f in flights:
                            try:
                                data[u'全部']['price'] += f.cpc * f.click
                                data[u'全部']['click'] += f.click
                            except KeyError:
                                data[u'全部'] = {}
                                data[u'全部']['price'] = f.cpc * f.click
                                data[u'全部']['click'] = f.click
                    else:
                        if has_clients:
                            flights = Flight.objects.select_related('media','media__first_category').filter(media__first_category__c_name=mc).filter(ad__client__id__in=clients_list).filter(Q(start_day__gt=start, start_day__lt=end)| Q(end_day__gt=start, end_day__lt=end)| Q(start_day__lt=start, end_day__gt=end), total_price__gt=0)
                        else:
                            flights = Flight.objects.select_related('media','media__first_category').filter(media__first_category__c_name=mc).filter(Q(start_day__gt=start, start_day__lt=end)| Q(end_day__gt=start, end_day__lt=end)| Q(start_day__lt=start, end_day__gt=end), total_price__gt=0)
                        for f in flights:
                            if not f.media.first_category == None:
                                try:
                                    data[mc]['price'] += f.cpc * f.click
                                    data[mc]['click'] += f.click
                                except KeyError:
                                    data[mc] = {}
                                    data[mc]['price'] = f.cpc * f.click
                                    data[mc]['click'] = f.click
            if not sub_cats_list == ['']:
                for sc in sub_cats_list:
                    mcats , key = '-'.join(sc.split('$&')[:-1]), sc.split('$&')[-1] # subcats is made of main_cats and sub_cats using '-' to avoid name confusion
                    if has_clients:
                        flights = Flight.objects.select_related('media','media__second_category').filter(media__first_category__c_name=mcats).filter(ad__client__id__in=clients_list).filter(Q(start_day__gt=start, start_day__lt=end)| Q(end_day__gt=start, end_day__lt=end)| Q(start_day__lt=start, end_day__gt=end), total_price__gt=0)
                    else:
                        flights = Flight.objects.select_related('media','media__second_category').filter(media__first_category__c_name=mcats).filter(Q(start_day__gt=start, start_day__lt=end)| Q(end_day__gt=start, end_day__lt=end)| Q(start_day__lt=start, end_day__gt=end), total_price__gt=0)
                    for f in flights:
                        if key == u'其它':
                            if f.media.second_category == None:
                                try:
                                    data[sc]['price'] += f.cpc * f.click
                                    data[sc]['click'] += f.click
                                except KeyError:
                                    data[sc] = {}
                                    data[sc]['price'] = f.cpc * f.click
                                    data[sc]['click'] = f.click
    
                        else:
                            if not f.media.second_category == None:
                                if f.media.second_category.c_name == key:
                                    try:
                                        data[sc]['price'] += f.cpc * f.click
                                        data[sc]['click'] += f.click
                                    except KeyError:
                                        data[sc] = {}
                                        data[sc]['price'] = f.cpc * f.click
                                        data[sc]['click'] = f.click

            if not media_list == ['']:
                for m in media_list:
                    if has_clients:
                        flights = Flight.objects.select_related('media').filter(media__c_name=m).filter(ad__client__id__in=clients_list).filter(Q(start_day__gt=start, start_day__lt=end)| Q(end_day__gt=start, end_day__lt=end)| Q(start_day__lt=start, end_day__gt=end), total_price__gt=0)
                    else:
                        flights = Flight.objects.select_related('media').filter(media__c_name=m).filter(Q(start_day__gt=start, start_day__lt=end)| Q(end_day__gt=start, end_day__lt=end)| Q(start_day__lt=start, end_day__gt=end), total_price__gt=0)
                    for f in flights:
                        try:
                            data[m]['price'] += f.cpc * f.click
                            data[m]['click'] += f.click

                        except KeyError:
                            data[m] = {}
                            data[m]['price'] = f.cpc * f.click
                            data[m]['click'] = f.click

            if not channel_list == ['']:
                for c in channel_list:
                    me , key = c.split('$&')
                    if has_clients:
                        flights = Flight.objects.select_related('media','channel').filter(media__c_name=me).filter(channel__c_name=key).filter(ad__client__id__in=clients_list).filter(Q(start_day__gt=start, start_day__lt=end)| Q(end_day__gt=start, end_day__lt=end)| Q(start_day__lt=start, end_day__gt=end), total_price__gt=0)        
                    else:
                        flights = Flight.objects.select_related('media','channel').filter(media__c_name=me).filter(channel__c_name=key).filter(Q(start_day__gt=start, start_day__lt=end)| Q(end_day__gt=start, end_day__lt=end)| Q(start_day__lt=start, end_day__gt=end), total_price__gt=0)
                    for f in flights:
                        try:
                            data[c]['price'] += f.cpc * f.click
                            data[c]['click'] += f.click
                        except KeyError:
                            data[c] = {}
                            data[c]['price'] = f.cpc * f.click
                            data[c]['click'] = f.click
            
            if not flight_list == ['']:
                for fl in flight_list:
                    ch , key = '-'.join(fl.split('$&')[:-1]), fl.split('$&')[-1] # flight name is made of channel and real flight name using '-' to avoid name confusion
                    if has_clients:
                        flights = Flight.objects.filter(channel__c_name=ch).filter(ad__client__id__in=clients_list).filter(Q(start_day__gt=start, start_day__lt=end)| Q(end_day__gt=start, end_day__lt=end)| Q(start_day__lt=start, end_day__gt=end), total_price__gt=0)
                    else:
                        flights = Flight.objects.select_related('media','media__first_category','media_ad_info','channel').filter(Q(channel__c_name=ch),Q(media_ad_info__adform=key)).filter(Q(start_day__gt=start, start_day__lt=end)| Q(end_day__gt=start, end_day__lt=end)| Q(start_day__lt=start, end_day__gt=end), total_price__gt=0)
                    for f in flights:
                        try:
                            data[fl]['price'] += f.cpc * f.click
                            data[fl]['click'] += f.click
                        except KeyError:
                            data[fl] = {}
                            data[fl]['price'] = f.cpc * f.click
                            data[fl]['click'] = f.click
            # calculate cpc from data
            if not main_cats_list == ['']:
                for mc in main_cats_list:
                    if data[mc]['click'] == 0:
                        cpc[mc] = 0
                    else:
                        cpc[mc] = data[mc]['price'] / data[mc]['click']
            if not sub_cats_list == ['']:
                print sub_cats_list
                for sc in sub_cats_list:
                    print type(sc)
                    k = sc.replace('$&', '-')
                    if data[sc]['click'] == 0:
                        cpc[k] = 0
                    else:
                        cpc[k] = data[sc]['price'] / data[sc]['click']
                    
            if not media_list == ['']:
                for m in media_list:
                    if data[m]['click'] == 0:
                        cpc[m] = 0
                    else:
                        cpc[m] = data[m]['price'] / data[m]['click']
            
            if not channel_list == ['']:
                for c in channel_list:
                    k = c.replace('$&', '-')
                    if data[c]['click'] == 0:
                        cpc[k] = 0
                    else:
                        cpc[k] = data[c]['price'] / data[c]['click']
            
            if not flight_list == ['']:
                for f in flight_list :
                    #因为频道和广告位字符太长，导致fusioncharts中的部分字重合，所以特此切割一下频道，只保留两个字符，剩下的用...表示
#                    channel, flight = f.split('$&')
#                    channel_split = channel[:2]
#                    channel_split = channel_split + '..'
#                    k = channel_split + '-' + flight
                    k = f.replace('$&', '-')
                    if data[f]['click'] == 0:
                        cpc[k] = 0
                    else:
                        cpc[k] = data[f]['price'] / data[f]['click']
                            
            multi_media_chart_bar_up = _get_mutil_media_chart(cpc, 'Bar')
            multi_media_chart_bar_down = _get_mutil_media_chart(cpc, 'Bar', True)
            multi_media_chart_line_up = _get_mutil_media_chart(cpc,'Line')
            multi_media_chart_line_down = _get_mutil_media_chart(cpc, 'Line', True)
            
            write_bar_xml(cpc, 'mediaeffect_cpc_media.xml')
            request.session['cpc'] = cpc
            chart = {}
            chart['bar_up'] = multi_media_chart_bar_up
            chart['line_up'] = multi_media_chart_line_up
            chart['bar_down'] = multi_media_chart_bar_down
            chart['line_down'] = multi_media_chart_line_down
            return HttpResponse(json.dumps(chart), mimetype="json")
        else:
            return HttpResponse('missing parameters')


def get_mediatree_chart_fusionchart(request):
    cpc = {}
    if 'cpc' in request.session:
        cpc = request.session['cpc']
        del request.session['cpc']
    keys, values = _sort_dict_by_value(cpc)
    chart = base_chart(u'媒体效果对比', '')
    chart['chart']['yaxisname'] = 'cpc'
#    chart['chart']['labelDisplay'] = 'rotate'
#    chart['chart']['rotateLabels'] = '1'
     
    
    chart['data'] = []
    for key in keys:
        chart['data'].append({'label': key, 'value': cpc[key]})
    return HttpResponse(json.dumps(chart),  mimetype="json")
        
    
def get_mediacats(request):
    from MediaChooser.media.models import MediaCategory 
    if request.GET:
        nilsen_id =  request.GET.has_key('nilsen_id') and request.GET.get('nilsen_id') or 0
        has_parent = MediaCategory.objects.filter(parent=nilsen_id)
        data = [{'id':re.id,'c_name':re.c_name} for re in has_parent]
        return HttpResponse(json.dumps(data))

@login_required
def media_reco(request, form_class=MP_MediaFilter_Form):
    if request.method == "POST":
        form = form_class(request.POST)
        if form.is_valid():
            pass
    else:
        form = form_class()
        clients_dict = Client.objects.get_clients_dict()

        init_data = empty_chart()

        data2 = [0 for i in range(12)]
        chart2 = ofc_base_chart(u"媒体频道CPC", None, data2)
        element12 = Bar_3d("#D54C78", "no data", 10, data2)
        chart2.elements = [element12]
        init_media_channel_data = chart2.create()
        
        #from MediaChooser.NielsenMedia.models import NielsenCategory 
        from MediaChooser.media.models import MediaCategory 
        nielsencateg =  MediaCategory.objects.filter(parent=None)
        return render_to_response('ad_resource_mgmt/mp_media_reco.html',{'init_data':init_data
                                        ,'init_media_channel_data':init_media_channel_data
                                        ,'form':form, 'clients_dict':clients_dict
                                        ,'nielsencateg':nielsencateg}
                                        , context_instance=RequestContext(request))


import re
rx=re.compile(u"([\u3040-\ufaff])", re.UNICODE)

def cjkwrap(text, width, encoding="utf-8"):
    text = text
    if type(text) != type(u''):
        text = unicode(text,encoding)
        
    return reduce(lambda line, word, width=width: '%s%s%s' %      
                (line,
                 [' ','<br>', ''][(len(line)-line.rfind('<br>')-1
                       + len(word.split('<br>',1)[0] ) >= width) or
                      line[-1:] == '\0' and 2],
                 word),
                rx.sub(r'\1\0 ', text).split(' ')
            ).replace('\0', '')


def get_mediareco(request):
    from django.core.exceptions import  MultipleObjectsReturned
    from MediaChooser.media.models import Media,Channel,MediaAdInfo

    if request.POST:
        if request.POST.has_key('channel_id'):
            
            channel_id = request.POST.get('channel_id')
            media = Channel.objects.get(pk=channel_id).media
            media_id = media.id
            
            clients_list = request.POST.get('clients_list')
            if clients_list == '':
                clients_list = [c.id for c in Client.objects.all()]
            else:
                clients_list =  map(int, clients_list.split(',')[:-1])
            
            start_day = request.POST.get('start_day')
            end_day = request.POST.get('end_day')
            
            if start_day == '':
                start = str2date('1000-01-01')
            else:
                start = str2date(start_day)

            if end_day == '':
                end = str2date('9999-01-01')
            else:
                end = str2date(end_day)
                    
            from django.db import connection
            cursor = connection.cursor()
            if len(clients_list) == 1:
                sql = "SELECT d.adform, sum(a.click*a.cpc)/(sum(a.click)+1) as cpc \
                    FROM media_planning_flight a, ad_ad b, client_client c, media_mediaadinfo d\
                    WHERE a.media_id = %s and a.channel_id = %s and a.ad_id = b.id and b.client_id = c.id and d.id = a.media_ad_info_id and c.id = %s \
                    and ( (a.start_day between \'%s\' and \'%s\') or (a.end_day between \'%s\' and \'%s\') or (a.start_day < \'%s\' and a.end_day > \'%s\') ) \
                    GROUP BY a.media_id, a.channel_id, d.adform \
                    ORDER BY cpc ASC" % (media_id, channel_id, clients_list[0], start, end, start, end, start, end)
            else:
                sql = "SELECT d.adform, sum(a.click*a.cpc)/(sum(a.click)+1) as cpc \
                    FROM media_planning_flight a, ad_ad b, client_client c, media_mediaadinfo d\
                    WHERE a.media_id = %s and a.channel_id = %s and a.ad_id = b.id and b.client_id = c.id and d.id = a.media_ad_info_id and c.id in %s \
                    and ( (a.start_day between \'%s\' and \'%s\') or (a.end_day between \'%s\' and \'%s\') or (a.start_day < \'%s\' and a.end_day > \'%s\') ) \
                    GROUP BY a.media_id, a.channel_id, d.adform \
                    ORDER BY cpc ASC" % (media_id, channel_id, tuple(clients_list), start, end, start, end, start, end)
            
            cursor.execute(sql)

            cpc_data = []
            adforms = []
            for row in cursor:
                if row[1] > 0:
                    adforms.append(row[0])
                    cpc_data.append(row[1])
            cursor.close()
            
            _min, _max = _getMinMax(cpc_data)
            steps = int((_max - _min)/4)
            from MediaChooser.ad_resource_mgmt.chart import write_bar2_xml
            write_bar2_xml(adforms, cpc_data, media, Channel.objects.get(id=channel_id).c_name, 'mediareco_cpc_flight.xml')
            data={
                  "bg_colour" :"#FFFFFF",
                  "title": {
                    "text": u"%s - %s"  %(media.c_name, Channel.objects.get(id=channel_id).c_name)
                  },
    
                  "elements": [
                   {
                      "text": "广告位cpc", 
                      "colour": "#A0A0D4", 
                      "type": "bar_glass",
                      "values":cpc_data,
                      "tip": 'cpc =#val#',
                      "alpha":1
                    },
                    {
                      "type":"tags",
                      "values": [{'y':v,'x':k} for k,v in enumerate(cpc_data)],
                      "font":"Verdana",
                      "font-size":12,
                      "colour":"#8B864E",
                      "align-x":"center",
                      "text":"#y#"
                    }
                  ],
                   "x_axis": {
                    #"3d": 10,
                     "colour": "#909090",
                    "labels": {'labels':["%s" %(adforms[k]) for k,v in enumerate(cpc_data) ],'size':12},
                    "grid-colour": "#FFFFFF"
                  },
                  "y_axis": {
                    "min": _min,
                    "max": _max,
                    "steps": steps,
                    "grid-colour": "#CCCCCC"
                  }
                 }
    
            return HttpResponse(json.dumps(data))
        else:    
            
            clients_list = request.POST['clients_list']
            if clients_list == '':
                clients_list = [c.id for c in Client.objects.all()]
            else:
                clients_list =  map(int, clients_list.split(',')[:-1])
                
            media_id = request.POST.has_key('media_id') and request.POST.get('media_id') or ''
            media_obj  = Media.objects.get(pk=media_id)
            
            start_day = request.POST['start_day']
            end_day = request.POST['end_day']

            if start_day == '':
                start = str2date('1000-01-01')
            else:
                start = str2date(start_day)

            if end_day == '':
                end = str2date('9999-01-01')
            else:
                end = str2date(end_day)
            
            from django.db import connection
            cursor = connection.cursor()
            if len(clients_list) == 1:
                sql = "SELECT a.channel_id, d.c_name, sum(a.click*a.cpc)/(sum(a.click)+1) as cpc FROM \
                    media_planning_flight a, ad_ad b, client_client c, media_channel d \
                    WHERE a.media_id = %s and a.ad_id = b.id and b.client_id = c.id and a.channel_id = d.id and c.id = %s \
                    and ( (a.start_day between \'%s\' and \'%s\') or (a.end_day between \'%s\' and \'%s\') or (a.start_day < \'%s\' and a.end_day > \'%s\') ) \
                    GROUP BY a.channel_id, d.c_name ORDER BY cpc ASC" % (media_id, clients_list[0], start, end, start, end, start, end)
            else:
                sql = "SELECT a.channel_id, d.c_name, sum(a.click*a.cpc)/(sum(a.click)+1) as cpc FROM \
                    media_planning_flight a, ad_ad b, client_client c, media_channel d \
                    WHERE a.media_id = %s and a.ad_id = b.id and b.client_id = c.id and a.channel_id = d.id and c.id in %s \
                    and ( (a.start_day between \'%s\' and \'%s\') or (a.end_day between \'%s\' and \'%s\') or (a.start_day < \'%s\' and a.end_day > \'%s\') ) \
                    GROUP BY a.channel_id, d.c_name ORDER BY cpc ASC" % (media_id, tuple(clients_list), start, end, start, end, start, end)
            
            cursor.execute(sql)
            
            new_cpc = []
            channel_ids = []
            channel_names = []
            for row in cursor:
                if row[2] > 0:
                    new_cpc.append(row[2])
                    channel_ids.append(row[0])
                    channel_names.append(row[1])
                
            
            cursor.close()

            Average= 0
                
            minn,maxx = _getMinMax(new_cpc)
            steps = int((maxx - minn)/4)
            
            labels = ''
            if len(new_cpc) > 9:
                labels = {'labels':['']*len(new_cpc)}
            else:
                labels = {'labels':channel_names,'size':12}
            
            from MediaChooser.ad_resource_mgmt.chart import write_bar1_xml
            write_bar1_xml(channel_names, new_cpc, media_obj, channel_ids, 'mediareco_cpc_channel.xml')
            
            data={
                  "bg_colour" :"#FFFFFF",
                  "title": {
                  #"text": u"媒体- %s -CPC   平均CPC=%.4f " %(media_obj.c_name,Average)
                  "text": u"媒体 - %s - CPC" % media_obj.c_name
                  },
    
                  "elements": [
                   {
                      "text": "频道cpc", 
                      "colour": "#8B864E", 
                      "type": "bar_glass",
                      "values": [{'tip':'%s <br> %.2f' %(channel_names[k], v),
                          'top':v,
                          'bottom':None,
                          'on-click':'bar_2("%s","%s")' %(channel_ids[k],media_obj.id)} \
                        for k,v in enumerate(new_cpc) ],
                      #"values": new_cpc,
                      "colour": "#D54C78",
                      "tip": '#val#',
                      "alpha":1
                    },
    
                    {
                      "type":"tags",
                      "values": [{'y':v,'x':k} for k,v in enumerate(new_cpc)],
                      #"values": new_cpc,
                      "font":"Verdana",
                      "font-size":12,
                      "colour":"#8B864E",
                      "align-x":"center",
                      "text":"#y#"
                    },
                  ],
                   "x_axis": {
                    #"3d": 10,
                    "colour": "#909090",
                   #"labels": {'labels':channel_names,'size':12},
                   "labels": labels,
                   "grid-colour": "#FFFFFF"
                  },
                  "y_axis": {
                    "min": 0,
                    "max": maxx,
                    "steps": steps,
                    "grid-colour": "#CCCCCC"
                  }
    
                }
            
            return HttpResponse(json.dumps(data))

    if request.method == 'GET':
        get = request.GET
        if get.has_key('start_day') and get.has_key('end_day') and get.has_key('target') and get.has_key('level') and get.has_key('num') and get.has_key('cat_id') and get.has_key('clients_list') :
            start_day = get['start_day']
            end_day = get['end_day']
            target = get['target']
            level = get['level']
            num = int(get['num'])
            clients_list = get['clients_list']
            has_flight_ad_client = False
            
            flight_ad_client = Flight.objects.filter(id=None)
            
            if clients_list <> '':
                client_ids = map(int, clients_list.split(',')[:-1])
                adret = Ad.objects.filter(client__in=client_ids)
                ad_ids = [ret.id for ret in adret]
                #flight_ad_client = Flight.objects.filter(ad__in=ad_ids)
            else:
                adret = Ad.objects.all()
            
            if get['cat_id'] == 'null' or get['cat_id'] == 'a-all':
                cat_level, cat_id = 'all', 0
            else:
                cat_level, cat_id = get['cat_id'].split('-')                

            if target == 'cpc':
                start, end = _transDate(start_day, end_day)
                
                data = {}
                cpc = {}
                
                id_dict = {}
                from django.db.models import Q
                if cat_level == 'a':
                    #flights = Flight.objects.only('media').select_related('media').filter(media__first_category__id=cat_id, ad__in=list(adret)).extra(where=['(a.start_day between \'%s\' and \'%s\') or (a.end_day between \'%s\' and \'%s\') or (a.start_day < \'%s\' and a.end_day > \'%s\') )'], params=[start,end,start,end,start,end])
                    flights = Flight.objects.filter(start_day__gt=start, start_day__lt=end, media__first_category__id=cat_id, ad__in=list(adret)) | \
                            Flight.objects.filter(end_day__gt=start, end_day__lt=end, media__first_category__id=cat_id, ad__in=list(adret)) | \
                            Flight.objects.filter(start_day__lt=start, end_day__gt=end, media__first_category__id=cat_id, ad__in=list(adret))

                elif cat_level == 'b':
                    flights = Flight.objects.filter(start_day__gt=start, start_day__lt=end, media__second_category__id=cat_id, ad__in=list(adret)) | \
                            Flight.objects.filter(end_day__gt=start, end_day__lt=end, media__second_category__id=cat_id, ad__in=list(adret)) | \
                            Flight.objects.filter(start_day__lt=start, end_day__gt=end, media__second_category__id=cat_id, ad__in=list(adret))
                
                elif cat_level == 'all':
                    #flights = Flight.objects.filter(start_day__gt=start, start_day__lt=end, ad__in=list(adret)) | \
                    #        Flight.objects.filter(end_day__gt=start, end_day__lt=end, ad__in=list(adret)) | \
                    #        Flight.objects.filter(start_day__lt=start, end_day__gt=end, ad__in=list(adret))
                    flights = Flight.objects.filter(Q(ad__in=list(adret)), Q(start_day__gt=start, start_day__lt=end) | Q(end_day__gt=start, end_day__lt=end) | Q(start_day__lt=start, end_day__gt=end))
                
                if flights.count() == 0:
                    return HttpResponse(json.dumps({'success':False}), mimetype="json")

                for f in flights:
                    if level == 'media':
                        key = f.media.c_name
                        id = f.media.id
                    elif level == 'channel':
                        key = f.media.c_name + '-' + f.channel.c_name
                        id = f.channel.id

                    if key in data:
                        data[key]['price'] += f.cpc * f.click
                        data[key]['click'] += f.click
                    else:
                        data[key] = {}
                        id_dict[key] = id
                        data[key]['price'] = f.cpc * f.click
                        data[key]['click'] = f.click
                        
                for d in data:
                    if data[d]['price'] != 0:
                        cpc[d] = data[d]['price'] / data[d]['click']
                    else:
                        cpc[d] = 0
                
                    if cpc[d] <= 0.01:
                        
                        del cpc[d]                
                
                from MediaChooser.ad_resource_mgmt.chart import write_bar_withid_xml
                write_bar_withid_xml(cpc, id_dict, 'mediareco_cpc_media.xml')
                #return HttpResponse(json.dumps({
                #    'media_reco_chart_bar':_get_mutil_media_chart1(cpc, id_dict, 'Bar', num=num),
                #    'media_reco_chart_line':_get_mutil_media_chart1(cpc, id_dict, 'Line', num=num)
                #}), mimetype="json")
                return HttpResponse(json.dumps({'success':True}), mimetype="json")
            
def str2color(val):
   return ImageColor.getrgb('#'+val.rjust(6, '0'))
                
def export_chart_image(request):
    print request.POST.keys()
    parameters = request.POST.get('parameters', '')
    width = request.POST.get('meta_width', '')
    height = request.POST.get('meta_height', '')
    bgcolor = request.POST.get('meta_bgColor', '')
    data = request.POST.get('stream', '')
    
    exportFileName = 'chart'
    exportFormat = 'PNG'
    
    
    parms = parameters.split('|')
    for p in parms:
        param = p.split('=')
        if param[0] == 'exportFileName':
            if len(param) > 1:
                exportFileName = param[1]
        elif param[0] == 'exportFormat':
            if len(param) > 1:
                exportFormat = param[1]
    
    
    # Split the data into rows using ; as the spearator
    rows = data.split(';')
    
    # Create image
    bgcolor = str2color(bgcolor)
    im = Image.new('RGB', (int(width), int(height)), bgcolor)
    putpixel = im.im.putpixel
    
    for y, row in enumerate(rows):
        x = 0
    
        # Split row into pixels
        pixels = row.split(',')
        for pixel in pixels:
            # Split pixel into color and repeat value
            color, repeat = pixel.split('_')
            repeat = int(repeat)
    
            if color == '':
                # Empty color == background color
                color = bgcolor
            else:
                # Pad color to 6 characters
                color = str2color(color)
    
            while repeat:
                putpixel((x, y), color)
                x += 1
                repeat -= 1
    
    # Save image into file like object
    imstr = StringIO()
    print exportFormat
    if exportFormat == 'PNG':
        im.save(imstr, 'PNG', quality=100)
        exportFileName = exportFileName + '.png'
    elif exportFormat == 'JPG':
        im.save(imstr, 'JPEG', quality=75)
        exportFileName = exportFileName + '.jpeg'
    elif exportFormat == 'PDF':
        im.save(imstr, 'PDF', quality=100)
        exportFileName = exportFileName + '.pef'
    
    
    page = HttpResponse(imstr.getvalue())
    page['Content-Disposition'] = "attachment; filename=" + exportFileName 
    page['Content-Type']        = 'image/png'
    if exportFormat == 'JPG':
        page['Content-Type']        = 'image/jpeg'
    elif exportFormat == 'PDF':
        page['Content-Type']        = 'application/pdf'
    return page


def change_flightname(request):
    
    if request.method == 'GET' and request.GET.has_key('campaign_name') and request.GET.has_key('campaign_id'):
        campaign_id = int(request.GET['campaign_id'])
        new_campaign_name =  request.GET['campaign_name']
        
        campaign = Ad.objects.get(DE_campaign_id= campaign_id)
        campaign.name = new_campaign_name
        campaign.save()
        
        return HttpResponse(json.dumps({'success':'t','new_name':new_campaign_name}), mimetype="json")
    
##########################  CHART  ###############################
def empty_chart():
    #chart = Chart()
    data = [0,0,0,0,0,0,0,0,0,0,0,0]
    chart = ofc_base_chart(u"多媒体CPC效果对比图", None ,data)
    element = Line(media_price_color, "no data", 10, data)
    chart.elements = [element]
    return chart.create()

def ofc_base_chart(title='chart-title', x_labels=None, values=None, set_y_left_color=False, set_y_right_color=False, y_right_data=None):
    chart = Chart()
    chart.title.text = title
    chart.x_axis.labels.labels = x_labels
    chart.x_axis.labels.size = 12
    chart.x_axis.labels.colour = "#666666"
    
    chart.x_axis.grid_colour = "#FFFFFF"
    chart.y_axis.grid_colour = "#CCCCCC"
    chart.bg_colour = "#FFFFFF"
    
    if values:
        chart.y_axis.min, chart.y_axis.max = _getMinMax(values)
        chart.y_axis.steps = int((chart.y_axis.max*1.2 - chart.y_axis.min*0.8)/4)
    
    if set_y_left_color:
        chart.y_axis.colour = cpc_color
        chart.y_axis.labels.colour = cpc_color
        
    if set_y_right_color:
        chart.y_axis_right.colour = click_color
        chart.y_axis_right.labels.colour = click_color
    
    if y_right_data:
        chart.y_axis_right.min, chart.y_axis_right.max = _getMinMax(y_right_data)
        chart.y_axis_right.steps = int(chart.y_axis_right.max/4)
        
    return chart
    
def _get_cpc_date_chart(data, click_data, x_axis, campaign_cpc = None, end_day=None, start_day=None):
    
    if end_day:
        title_text = u"CPC走势图 (%s - %s)" % (start_day, end_day)
    else:
        title_text = u"CPC走势图"
    
    chart = ofc_base_chart(title_text,  axis2labels(x_axis), data, True, True, click_data)
    chart.x_axis.labels.rotate = 90
    
    element_cpc = Line_Hollow(cpc_color, "CPC", 10, data, dot_size=2, dot_colour='#0f70d3')
    #element_click = Line_Hollow(click_color, "Clicks", 10, click_data, 'right', dot_size=3, tip="#x_label#<br>clicks: #val#")
    element_click = Line_Hollow(click_color, "Clicks", 10, click_data, 'right', dot_size=2, dot_colour='#92D050')
    
    if not campaign_cpc:
        chart.elements = [element_cpc, element_click]
    else:
        #element_campaign_cpc = Line(None, campaign_cpc_color, u"平均CPC", 10, campaign_cpc, tip= u"平均cpc: #val#")
        element_campaign_cpc = Line(campaign_cpc_color, u"平均CPC", 10, campaign_cpc)
        chart.elements = [element_cpc, element_click, element_campaign_cpc]
    return chart.create()

def _get_cpc_media_chart(d, click, x):
    
    #dict_data = dict(zip(x, d))
    #x_axis, data = _sort_dict_by_value(dict_data)
    
    #dict_data = dict(zip(click, d))
    #click, data = _sort_dict_by_value(dict_data)

    #print x_axis, click

    chart = ofc_base_chart(u"媒体CPC对比图", x, d, True, True, click)
    element1 = Bar_Glass(cpc_color, "CPC", 10, d)
    element2 = Bar_Glass(click_color, "CLICK", 10, click, 'right')
    chart.elements = [element1, element2]
    
    return chart.create()
    
def _get_cpc_media_linechart(data, click_data, x_axis):

    chart = ofc_base_chart(u"媒体CPC对比图", x_axis, data, True, True, click_data)
    element_cpc = Line_Hollow(cpc_color, "CPC", 10, data, dot_size=3)
    #element_click = Line_Hollow(click_color, "CLICK", 10, click_data, 'right', dot_size=3, tip="#x_label#<br>clicks: #val#")
    element_click = Line_Hollow(click_color, "CLICK", 10, click_data, 'right', dot_size=3)
    chart.elements = [element_cpc, element_click]
    
    return chart.create()

def _get_price_media_chart(data, x_axis):
    dict_data = dict(zip(x_axis, data))
    x_axis, data = _sort_dict_by_value(dict_data)
    chart = ofc_base_chart(u"媒体投放量比较", x_axis, data)
    element1 = Bar_Glass(media_price_color, "price", 10, data)
    tags = {"type":"tags",
    "values": [{'y':v,'x':k} for k,v in enumerate(data)],"font":"Verdana","font-size":10,"colour":"#000000","align-x":"center","text":"#y#"}
    chart.elements = [element1, tags]
    return chart.create()
    
def _get_cpc_media_comp_chart(data, x_axis, end=None, start=None):

    colors = ['#92D050','#3D5C56','#A0A0D4','#BF3EFF','#EEEE00','#8B864E','#8B2500','#845533','#983762','#3dee22','#aac3dd','#abe3311','#231bcc','#ff3ff2','#edede2','#eaea22','#2222ea','#2222ea','#2222ea','#2222ea','#2222ea','#2222ea','#2222ea','1234ee','2345dd','3456aa','4512ff']
    
    if end:
        title_text = u"媒体CPC对比图 (%s - %s)" % (start, end)
    else:
        title_text = u"媒体CPC对比图"

    chart = ofc_base_chart(title_text, axis2labels(x_axis))
    
    index = 0
    chart.elements = []
    maxx = -1
    minn = 0
    
    for d in data:
        ma = max(data[d])
        if ma > maxx:
            maxx = ma

        element = Line(colors[index], d, 10, data[d])
        index += 1
        chart.elements.append(element)
    if minn == maxx == 0:
        chart.y_axis.max = 1
    else:
        chart.y_axis.max = int(maxx*1.2)
    chart.y_axis.steps = int((maxx*1.2 - minn*0.8)/4)
    chart.x_axis.labels.rotate = 90
    
    return chart.create()

def _get_cpc_mflights_chart(data, click, x_axis):
    chart = ofc_base_chart(u"多排期CPC对比图", x_axis, data, True, True, click)
    element1 = Bar_Glass(cpc_color, "CPC", 10, data)
    element2 = Bar_Glass(click_color, "CLICK", 10, click, 'right')
    chart.elements = [element1, element2]
    
    return chart.create()

def _get_mflights_chart(cpc_data, click_data, id_dict):
    
    keys_temp = []
    keys = id_dict.keys()
    
    width = 24- len(keys)/2 * 2 
    
    for k in keys:
        keys_temp.append(cjkwrap(k,width,'utf-8'))
    
    chart = ofc_base_chart(u"CPC效果对比图", keys_temp, cpc_data,True,True,click_data)
    chart.elements = []
    
    
    X = dict(zip(cpc_data,keys))
    Y = dict(zip(click_data,keys))
    values_cpc = [{'top':v,"bottom": None,'on-click':'http://211.94.190.88/dl-dev-ad/ad-res-mgmt/campaign/%s/' %(id_dict[X[v]])} for v in cpc_data]
    element = Bar_Glass(cpc_color, "CPC", 10, values_cpc)
    
    values_click = [{'top':v,"bottom": None,'on-click':'http://211.94.190.88/dl-dev-ad/ad-res-mgmt/campaign/%s/' %(id_dict[Y[v]])} for v in click_data]
    element1 = Bar_Glass(click_color, "CPC", 10, values_click,'right')
    
    chart.elements.append(element)
    chart.elements.append(element1)

    return chart.create()


def _get_mutil_media_chart1(data, id_dict, type='Bar', reverse=False, num=None):

    keys_temp, values = _sort_dict_by_value(data, reverse)
    keys = []
    new_id_dict = {}
    
    for k in keys_temp:
        kk = k
        if '-' in k:
            kk = k.split('-')[0] + '<br>' + cjkwrap(''.join(k.split('-')[1:]),10,'utf-8')
        keys.append(kk)
        new_id_dict[kk] = id_dict[k]
    keys = keys[:num]
    values = values[:num]
    
    ids = id_dict.keys()

    chart = ofc_base_chart(u"CPC效果对比图", keys, values)
    chart.elements = []

    X = dict(zip(values,keys))

    if type == 'Bar':
        values1 = [{'top':v,"bottom": None,'on-click':'bar_1("%s")' %(new_id_dict[X[v]])} for v in values]
    elif type == 'Line':
        values1 = [{'value':v,"bottom": None,'on-click':'bar_1("%s")' %(X[v])} for v in values]

    if type == 'Bar':
        element = Bar_Glass(cpc_color, "CPC", 10, values1)
    if type == 'Line':
        #element = Line_Hollow(cpc_color, "CPC", 10, values, dot_size=3,tip="#x_label#<br>cpc: #val#")
        element = Line_Hollow(cpc_color, "CPC", 10, values1, dot_size=3)

    tags = {"type":"tags","values":[{'x':v,'y':values[v],'text':'%.2f' % values[v]} for v in range(len(keys))]}

    chart.elements.append(element)
    chart.elements.append(tags)

    return chart.create()

def _get_mutil_media_chart(data, type='Bar', reverse=False, num=None):
    
    keys_temp, values = _sort_dict_by_value(data, reverse)
    keys = []
    for k in keys_temp:
        if '-' in k:
            k = k.split('-')[0] + '<br>' + cjkwrap(''.join(k.split('-')[1:]),10,'utf-8')
        keys.append(k)
    keys = keys[:num]
    values = values[:num]
    
    chart = ofc_base_chart(u"CPC效果对比图", keys, values)
    chart.elements = []

    X = dict(zip(values,keys))

    if type == 'Bar':
        values1 = [{'top':v,"bottom": None,'on-click':'bar_1("%s")' %(X[v])} for v in values]
    elif type == 'Line':
        values1 = [{'value':v,"bottom": None,'on-click':'bar_1("%s")' %(X[v])} for v in values]

    if type == 'Bar':
        element = Bar_Glass(cpc_color, "CPC", 10, values1)
    if type == 'Line':
        element = Line_Hollow(cpc_color, "CPC", 10, values1, dot_size=3)
        
    tags = {"type":"tags","values":[{'x':v,'y':values[v],'text':'%.2f' % values[v]} for v in range(len(keys))]}
    
    chart.elements.append(element)
    chart.elements.append(tags)
    
    return chart.create()

############################   utility functions   ################################

def _getMinMax(data):
    mi = min(data)
    ma = max(data)
    if mi == None:
        mi = 0
    if ma == None:
        ma = 0

    if mi == ma == 0:
        ma = 1
    else:
        mi = 0
        ma = round(ma*1.2+1) if ma is not None else 1
    return mi, ma
    
def is_weekend(date):
    """ is the data weekend ? """
    if date.weekday() == 5 or date.weekday() == 6: return True
    else: return False
        
def str2date(st):
    """ change str to date, eg: '2009-09-09' to 2009-09-09(datetime)  """
    year, month, day = st.split('-')
    return datetime.date(int(year), int(month), int(day))

def axis2labels(axis):
    """ change x-axis to date without 'year', then to label. eg: 2009-09-09 -> 09-09  """
    labels = []
    for x in axis:
        if is_weekend(str2date(x)):
            labels.append({'text':date_no_year(x), 'colour':weekend_color})
        else:
            labels.append(date_no_year(x))
    return labels

def _sort_dict_by_value(dict_data, reverse=False):
    """ sort a dict by value, return keys and value """
    keys = []
    values = []
    if type(dict_data) != type({}):
        return None
    else:
        for k, v in sorted(dict_data.items(), key=lambda x: x[1], reverse=reverse):
            keys.append(k)
            values.append(v)
    
    return keys, values
    
def _transDate(start_day, end_day):
    """ format date """
    if start_day == '':
        start = str2date('1000-01-01')
    else:
        start = str2date(start_day)
    if end_day == '':
        end = str2date('9999-01-01')
    else:
        end = str2date(end_day)

    return start, end

def base_chart(caption, subcaption, palette=3):
    chart = {}
    chart['chart'] = {}
    chart['chart']['caption'] = caption
    chart['chart']['palette'] = palette
    chart['chart']['exportHandler'] = reverse('export_chart_image')
#    chart['chart']['logoURL'] = 'http://192.168.244.215/andc-intra/themes/garland/logo.png'
#    chart['chart']['logoPosition'] = 'BL' # Bottom Left
#    chart['chart']['logoAlpha'] = '80'
#    chart['chart']['logoScale'] = '50'
#    chart['chart']['logoLink'] = 'N-http://www.and-c.com' # N means new window
    chart['chart']['decimals'] = '2'
    chart['chart']['connectNullData'] = '0'
    chart['chart']['formatNumberScale'] = '0'
    chart['chart']['exportEnabled'] = '1'
    chart['chart']['exportAtClient'] = '0'
    chart['chart']['exportAction'] = 'download'
    
#    chart['chart']['exportAtClient'] = '1'
#    chart['chart']['exportHandler'] = 'fcExporter1'
    
    return chart

def chart_api(request, campaign_id, chart_id):
    campaign = Ad.objects.get(DE_campaign_id= int(campaign_id))
    campaign._init()
        
    media_price = campaign.media_price()[0]
    
    colors = ['429EAD','4249AD', 'AD42A2', 'D4AC31']
    
    if chart_id == 'media_price_pie':
        chart = base_chart('媒体投放量', '')
        chart['data'] = []
        for c in media_price:
            chart['data'].append({'value':media_price[c],'label':c})
        return HttpResponse(json.dumps(chart), mimetype="json")
        
    if chart_id == 'date_click_cpc_line':
        chart = base_chart('排期每日cpc走势图报告', "%s - %s" % (campaign.start_day, campaign.end_day))
        chart['chart']['showvalues'] = '0'
        chart['chart']['numvisibleplot'] = '0'
        chart['chart']['pyaxisname'] = 'cpc'
        chart['chart']['syaxisname'] = 'click'
        
        chart['categories'] = []
        chart['dataset'] = []
        
        data_cpc = []
        data_click = []
        average_cpc = []
        
        category = {}
        category['category'] = []
                
        daily_cpc = campaign.daily_cpc()
        daily_click = campaign.daily_click()
        for m in campaign.date_range:
            category['category'].append({'label':'-'.join(str(m).split('-')[1:])})
            data_cpc.append({'value':daily_cpc[m]})
            data_click.append({'value':daily_click[m]})
            average_cpc.append({'value':campaign.cpc})
        
        chart['categories'].append(category)
            
        dataset_cpc = {'seriesname':'cpc', 'data':data_cpc, 'renderas':'line',"parentyaxis": "P"}
        dataset_click = {'seriesname':'click', 'data':data_click, 'renderas':'line',"parentyaxis": "S"}
        dateset_average_cpc = {'seriesname':'平均cpc', 'data':average_cpc, 'renderas':'line',"parentyaxis": "P", 'anchorRadius':'1'}
        
        chart['dataset'].append(dataset_cpc)        
        chart['dataset'].append(dataset_click)
        chart['dataset'].append(dateset_average_cpc)        
        return HttpResponse(json.dumps(chart), mimetype="json")
    
    if chart_id == 'media_click_cpc_bar':
        chart = base_chart('媒体效果对比图','')
        chart['chart']['showvalues'] = '0'
        chart['chart']['numvisibleplot'] = '0'
        chart['chart']['pyaxisname'] = 'cpc'
        chart['chart']['syaxisname'] = 'click'
        chart['categories'] = []
        chart['dataset'] = []
        
        data_cpc = []
        data_click = []
        
        category = {}
        category['category'] = []
        
        media_cpc = campaign.media_cpc()
        media_click = campaign.media_click()
        for m in media_cpc:
            category['category'].append({'label':m})
            data_cpc.append({'value':media_cpc[m]})
            data_click.append({'value':media_click[m]})
        
        chart['categories'].append(category)
            
        dataset_cpc = {'seriesname':'cpc', 'data':data_cpc, 'renderas':'bar',"parentyaxis": "P"}
        dataset_click = {'seriesname':'click', 'data':data_click, 'renderas':'bar',"parentyaxis": "S"}
        
        chart['dataset'].append(dataset_cpc)        
        chart['dataset'].append(dataset_click)        
        return HttpResponse(json.dumps(chart), mimetype="json")
    
    if chart_id == 'funnel_chart':
        import xml.etree.ElementTree as ET
        root = ET.Element('chart')
        root.attrib['caption'] = 'Conversion Ratio'
        root.attrib['palette'] = '3'
        root.attrib['showPercentValues'] = '0'
        root.attrib['percentOfPrevious'] = '1'
        root.attrib['isSliced'] = '1'
        
        root.attrib['exportEnabled'] = '1'
        root.attrib['exportAtClient'] = '0'
        root.attrib['exportAction'] = 'download'
        root.attrib['exportHandler'] = reverse('export_chart_image')
        
        
#        root.attrib['logoURL'] = 'http://192.168.244.215/andc-intra/themes/garland/logo.png'
#        root.attrib['logoPosition'] = 'BL' # Bottom Left
#        root.attrib['logoAlpha'] = '80'
#        root.attrib['logoScale'] = '50'
#        root.attrib['logoLink'] = 'N-http://www.and-c.com' # N means new window
        
        if campaign.start_day >= datetime.date.today():
            set1 = ET.SubElement(root, 'set')
            set1.attrib['label'] = u'用户点击数'
            set1.attrib['value'] = '0'
            root.attrib['caption'] = u'排期尚未开始,没有可显示的数据'
            return HttpResponse(ET.tostring(root, encoding='gb2312'), mimetype="text/xml")
           
        if campaign.client.c_name == u'联想':        
            set1 = ET.SubElement(root, 'set')
            set1.attrib['label'] = u'广告点击数'
            set1.attrib['value'] = '%s' % campaign.click

            ub = UserBehaviour.objects.get_ub_by_campaign(campaign_id)
            
            visits_sum = ub.get('visits__sum') or 0
            products_sum = ub.get('products_view__sum') or 0
            cart_addition_sum = ub.get('cart_addition__sum') or 0
            checkouts_sum = ub.get('checkouts__sum') or 0
            order_sum = ub.get('orders__sum') or 0
            
            if checkouts_sum <= order_sum:
                checkouts_sum = checkouts_sum + 0.01
            if cart_addition_sum <= checkouts_sum:
                cart_addition_sum = cart_addition_sum + 0.01
            if products_sum <= cart_addition_sum:
                products_sum = products_sum + 0.01
            if visits_sum <= products_sum:
                visits_sum = visits_sum + 0.01
            
            set2 = ET.SubElement(root, 'set')
            set2.attrib['label'] = u'用户访问数'
            set2.attrib['value'] = '%s' % visits_sum
            set3 = ET.SubElement(root, 'set')
            set3.attrib['label'] = u'产品详情页'
            set3.attrib['value'] = '%s' % products_sum
            
            set4 = ET.SubElement(root, 'set')
            set4.attrib['label'] = u'购物车'
            set4.attrib['value'] = '%s' % cart_addition_sum
            
            set5 = ET.SubElement(root, 'set')
            set5.attrib['label'] = u'checkout'
            set5.attrib['value'] = '%s' % checkouts_sum
            
            set6 = ET.SubElement(root, 'set')
            set6.attrib['label'] = u'order'
            set6.attrib['value'] = '%s' % order_sum
        
        elif campaign.ga_pid != '':
            set1 = ET.SubElement(root, 'set')
            set1.attrib['label'] = u'广告点击数'
            set1.attrib['value'] = '%s' % campaign.click

            ub = UserBehaviour.objects.get_ub_by_campaign(campaign_id)

            set2 = ET.SubElement(root, 'set')
            set2.attrib['label'] = u'用户访问数'
            set2.attrib['value'] = '%s' % ub['visits__sum']
        else:
            set1 = ET.SubElement(root, 'set')
            set1.attrib['label'] = u'用户点击数'
            set1.attrib['value'] = '0'
            root.attrib['caption'] = u'此排期没有用Omniture或者GA监测,没有可显示的数据'
        return HttpResponse(ET.tostring(root, encoding='gb2312'), mimetype="text/xml")

