#! /usr/bin/env python
#coding=utf-8

from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.db import transaction, connection
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.sessions.backends.db import SessionStore
from django.conf import settings
from django.template import RequestContext
from MediaChooser.client.models import Client
from MediaChooser.ad.models import ActivityType, Ad, AdRelatedStaff
from MediaChooser.media.models import Media, Channel, MediaAdInfo, MediaCategory
from MediaChooser.media_planning.models import Flight, DE_ClickData
# from MediaChooser.NielsenMedia.models import NielsenMedia
import xlrd
import re
import datetime
import time
import pyodbc
import urllib2
from os import path

#import cx_Oracle
#from django.db import IntegrityError
#import simplejson as json

# function to delete a whole media planning related data from MC database
#@login_required
def delete_mp(campaign_id):
    ad = Ad.objects.get(DE_campaign_id=campaign_id)
    from django.db import connection, transaction
    cursor = connection.cursor()

    cursor.execute('delete from media_planning_de_clickdata where ad_id=%s', [ad.id])
    transaction.commit_unless_managed()
    cursor.execute('delete from media_planning_flight where ad_id=%s', [ad.id])
    transaction.commit_unless_managed()
    cursor.execute('delete from ad_adrelatedstaff where ad_id=%s', [ad.id])
    transaction.commit_unless_managed()

    ad.delete()
    return True

def clear_trashinfo():
    from django.db import connection, transaction
    cursor = connection.cursor()

    cursor.execute('delete from media_planning_de_clickdata where ad_id not in (select id from ad_ad)')
    transaction.commit_unless_managed()
    cursor.execute('delete from media_planning_flight where ad_id not in (select id from ad_ad)')
    transaction.commit_unless_managed()
    cursor.execute('delete from ad_adrelatedstaff where ad_id not in (select id from ad_ad)')
    transaction.commit_unless_managed()

    return True

# Will not be used for ever
# function to get de_number set from DE database
def get_denumberset(campaign_id):
    de_db = pyodbc.connect('DRIVER={Oracle};SERVER=211.94.190.64;DATABASE=dart;UID=mediachooser_read;PWD=read_mediachooser;')
    de_cursor = de_db.cursor()
    sql = 'select flightnumber from admanager65.ng_flights where orderid=%s and status in (1, 3)' % campaign_id
    ret = set()
    de_cursor.execute(sql)
    for row in de_cursor:
        ret.add(row[0])
    de_cursor.close()
    return ret

# function to refresh every mp
def refresh_mp_after_clickdata_update(campaign_id):
    ad = Ad.objects.get(DE_campaign_id=campaign_id)
    ad_tracked_clicks = 0
    ad_tracked_spending = 0
    for flight in Flight.objects.filter(ad=ad):
        tracked_days = 0
        tracked_clicks = 0
        tracked_cpm = 0
        for cd in DE_ClickData.objects.filter(flight=flight):
            if cd.if_planned_spending == True and cd.date < datetime.date.today(): # Sum up all spendings before today
                tracked_days += 1
                if cd.cpm > 0:
                    tracked_cpm += cd.cpm
            if cd.eventcount > settings.USEFUL_CLICK_NUMBER:
                tracked_clicks += cd.eventcount
        
        flight.ad_days_tracked = tracked_days
        flight.click = tracked_clicks
        tracked_spending = flight.unit_price*tracked_days if tracked_cpm == 0 else flight.unit_price*tracked_cpm
        flight.total_price_tracked = tracked_spending
        flight.cpc = float(tracked_spending)/flight.click if flight.click > 0 else 0
        flight.save()

        ad_tracked_spending += tracked_spending*flight.discount_after_discount if flight.if_buy == True else 0
        ad_tracked_clicks += flight.click

    ad.click = ad_tracked_clicks
    ad.cpc = float(ad_tracked_spending)/ad_tracked_clicks if ad_tracked_clicks > 0 else 0
    ad.save()

def refresh_mp(mp_id):
    print mp_id
    num_re = re.compile(r'\d*')
    if mp_id is None or num_re.search(str(mp_id)) is None:
        return '请输入有效排期号！'
    else:
        # extract all click data till now from DE NG_SUM_FIXED_H table
        de_db = pyodbc.connect('DRIVER={Oracle};SERVER=211.94.190.64;DATABASE=dart;UID=mediachooser_read;PWD=read_mediachooser;')
        # check if media planning is exist responding to that mp_id
        sql = 'select * from admanager65.ng_insertionorders where id=%s' % mp_id
        de_cursor = de_db.cursor()
        de_cursor.execute(sql)
        for row in de_cursor:
            if row[0] is None:
                return '该排期ID对应的排期不存在！'
        # check if that mp has already been uploaded to MC
        try:
            ad = Ad.objects.get(DE_campaign_id=mp_id)
        except ObjectDoesNotExist:
            return '需要首先将该排期录入MC，然后才能进行数据更新！'

        # now update click data
        sql = 'select a.flightid, a.startdate, sum(a.eventcount) from admanager65.ng_sum_fixed_h a, admanager65.ng_flights b where a.flightid=b.id and a.eventtype=4 and b.orderid=%s group by a.startdate, a.flightid' % mp_id
        de_cursor.execute(sql)
        for row in de_cursor:
            flightid = row[0]
            startdate = row[1]
            eventcount = int(row[2]*settings.CLICK_COMPENSATION_COEFFICIENT)
            try:
                flight = Flight.objects.get(DE_flight_id=flightid)
                try:
                    clickdata = DE_ClickData.objects.get(flight=flight, date=startdate)
                    clickdata.eventtype = 4
                    clickdata.eventcount = eventcount
                    clickdata.save()
                except ObjectDoesNotExist:
                    #checkout if clicks > 10
                    if eventcount > settings.USEFUL_CLICK_NUMBER:
                        # here no need to think about CPM related stuff
                        clickdata = DE_ClickData(ad=flight.ad, media=flight.media, channel=flight.channel, media_ad_info=flight.media_ad_info, flight=flight, date=startdate, if_planned_spending=False, eventtype=4, eventcount=eventcount)
                        clickdata.save()
            except ObjectDoesNotExist:
                pass
                # return {'ret':0, 'msg':'Flight not exist! flightid: ' + str(flightid) + ' date: ' + str(startdate) + ' clicks: ' + str(eventcount)}
    refresh_mp_after_clickdata_update(mp_id)

# function to handle media planning
@transaction.commit_on_success
def mp_handler(file_contents, mp_name, client_id, activitytype_id, uploader, related_staff, campaign_id):
    # try:
        try:
            c_book = xlrd.open_workbook(file_contents=file_contents)
            c_sheet = c_book.sheet_by_index(0)
        except xlrd.biffh.XLRDError:
            return {'ret':0, 'msg':'本Excel文件的格式与后缀名不一致！快速解决方案：重建一个Excel文档，把内容拷贝过去，再上传！另，请采用2003的Excel格式导入！'}
        
        # Try to find DE links
        code_index = [-1, -1]
        code_re = re.compile(r'^http://.*')
        campaignid_re = re.compile(r'campaignid=\d*')
        delink_list = []
        
        for i in xrange(c_sheet.nrows):
            for j in xrange(c_sheet.ncols):
                if c_sheet.cell_value(i, j) == u'代码' or c_sheet.cell_value(i, j) == u'广告代码' or c_sheet.cell_value(i, j) == u'DE代码':
                    code_index = [i, j]
        if code_index[1] == -1:
            return {'ret':0, 'msg':'“代码”列不存在！'}
        
        ###### 获取包含DE link的列
        # Checkout if such links r accessible; if can, retrieve the flightid & adid; at last, check out the uniqueness of those ids.
        mp_flight_ad_id_dict = {}
        for i in xrange(code_index[0]+1, c_sheet.nrows):
            cont = c_sheet.cell_value(i, code_index[1])
            re_ret = code_re.search(cont)
            if re_ret is not None:
                # Check out the accessibleness
                try:
                    delink_ret = urllib2.urlopen(cont.encode('utf8'))
                except Exception, e:
                    return {'ret':0, 'msg':str(i+1)+'行DE代码无法打开！'}
                # check campaign_id of this link
                campaignid_re_ret = campaignid_re.search(cont)
                if campaignid_re_ret is not None:
                    if int(cont[campaignid_re_ret.start()+11:campaignid_re_ret.end()]) != campaign_id:
                        return {'ret':0, 'msg':'输入的排期ID与第' + str(i+1) + '行代码中的排期ID不符，请查找原因或咨询相关人员！'}
                ret_content = delink_ret.read()
                ret_content_re = re.search(r'FlightID=(\d*)&AdID=(\d*)', ret_content)
                if ret_content_re is None:
                    return {'ret':0, 'msg':str(i+1)+'行DE代码已过期或尚未生效！'}
                else:
                    mp_flight_ad_id_dict[i] = [int(ret_content_re.group(1)), int(ret_content_re.group(2))]
                delink_list.append(i)
        if len(delink_list) == 0:
            return {'ret':0, 'msg':'包含DE代码的列数为0！'}
        
        # Check out the uniqueness of these flight&ad ids.
        flightid_list = [mp_flight_ad_id_dict[i][0] for i in mp_flight_ad_id_dict]
        if len(delink_list) != len(flightid_list):
            return {'ret':0, 'msg':'DE代码中存在重复，请检查后再上传！'}
                
        # 获取网站/广告位置/广告形式/广告规格/单位/折扣/折后单价/折后总价/DE序号   & 广告规格/投放量/总价(网站总价)/刊例单价/刊例总价
        website_index=position_index=adform_index=size_index=unit_index=discount_index=price_index=totalprice_index=spending_index=website_price_index=price_beforediscount_index=totalprice_beforediscount_index=pv_index=if_buy_index=[-1, -1]
        
        for i in xrange(delink_list[0]):
            for j in xrange(c_sheet.ncols):
                if c_sheet.cell_type(i, j) == xlrd.XL_CELL_TEXT:
                    c_v = c_sheet.cell_value(i, j)
                    if c_v == u'网站':
                        website_index = [i, j]
                    elif c_v == u'广告位置':
                        position_index = [i, j]
                    elif c_v == u'广告形式':
                        adform_index = [i, j]
                    elif c_v == u'广告规格':
                        size_index = [i, j]
                    elif c_v == u'单位':
                        unit_index = [i, j]
                    elif c_v == u'折扣':
                        discount_index = [i, j]
                    elif c_v == u'折后单价':
                        price_index = [i, j]
                    elif c_v == u'折后总价':
                        totalprice_index = [i, j]
                    elif c_v == u'购买方式':
                        if_buy_index = [i, j]
                    elif c_v == u'曝光量':
                        pv_index = [i, j]
                    elif c_v == u'投放量':
                        spending_index = [i, j]
                    elif c_v == u'总价' or c_v == u'网站总价':
                        website_price_index = [i, j]
                    elif c_v == u'刊例单价':
                        price_beforediscount_index = [i, j]
                    elif c_v == u'刊例总价':
                        totalprice_beforediscount_index = [i, j]
                    else:
                        pass
        
        # make sure these titles r in the same row
        if code_index[0]==website_index[0]==position_index[0]==adform_index[0]==size_index[0]==unit_index[0]==discount_index[0]==price_index[0]==totalprice_index[0]==spending_index[0]==website_price_index[0]==price_beforediscount_index[0]==totalprice_beforediscount_index[0]:
            pass
        else:
            return {'ret':0, 'msg':'代码:'+str(code_index[0])+'/网站:'+str(website_index[0])+'/广告位置:'+str(position_index[0])+'/广告形式:'+str(adform_index[0])+'/广告规格:'+str(size_index[0])+'/单位:'+str(unit_index[0])+'/折扣:'+str(discount_index[0])+'/折后单价:'+str(price_index[0])+'/折后总价:'+str(totalprice_index[0])+'/购买方式:'+str(if_buy_index[0])+'/投放量:'+str(spending_index[0])+'...这些列名不在同一行！'}

        # 检查"刊例单价"和"刊例总价"俩列的数据有效，即均为数值；且数据间的关系是正确的。
        # 检查"折后单价"和"折后总价"俩列的有效数据，且数据间的关系是正确的。
        flight_price_dict = {}
        flight_totalprice_dict = {}
        for i in delink_list:
            # Checkout if every flight has its own spending number.
            if c_sheet.cell_type(i, spending_index[1]) is not xlrd.XL_CELL_NUMBER:
                return {'ret':0, 'msg':str(i+1)+'行“投放量”不存在或者格式错误！'}
            if c_sheet.cell_type(i, price_beforediscount_index[1]) is not xlrd.XL_CELL_NUMBER or c_sheet.cell_type(i, totalprice_beforediscount_index[1]) is not xlrd.XL_CELL_NUMBER or c_sheet.cell_type(i, price_index[1]) is not xlrd.XL_CELL_NUMBER or c_sheet.cell_type(i, totalprice_index[1]) is not xlrd.XL_CELL_NUMBER:
                return {'ret':0, 'msg':str(i+1)+'行：刊例单价/刊例总价/折后单价/折后总价 必须存在，并且其单元格数据类型必须为数值！'}
            else:		# check if 刊例单价*投放量==刊例总价
                if float(c_sheet.cell_value(i, price_beforediscount_index[1]))*int(c_sheet.cell_value(i, spending_index[1])) > 1.05 * int(c_sheet.cell_value(i, totalprice_beforediscount_index[1])):
                    if c_sheet.cell_value(i, adform_index[1]) not in [u'关键字', u'精准广告']:
                        return {'ret':0, 'msg':str(i+1)+'行：刊例单价x投放量!=刊例总价；若为关键字或精准投放，请将广告形式命名为"关键字"或者"精准广告"'}
                if float(c_sheet.cell_value(i, price_index[1]))*int(c_sheet.cell_value(i, spending_index[1])) > 1.05 * int(c_sheet.cell_value(i, totalprice_index[1])):
                    if c_sheet.cell_value(i, adform_index[1]) not in [u'关键字', u'精准广告']:
                        return {'ret':0, 'msg':str(i+1)+'行：折后单价x投放量!=折后总价；若为关键字或精准投放，请将广告形式命名为"关键字"或者"精准广告"'}
            #flight_price_dict[i] = c_sheet.cell_value(i, price_index[1])
            flight_totalprice_dict[i] = c_sheet.cell_value(i, totalprice_index[1])
            flight_price_dict[i] = c_sheet.cell_value(i, price_index[1]) if c_sheet.cell_value(i, adform_index[1]) not in [u'关键字', u'精准广告'] else float(c_sheet.cell_value(i, totalprice_index[1]))/int(c_sheet.cell_value(i, spending_index[1]))

        # store unit info for every flight
        # store PV/if_buy/discount info for every flight
        flight_unit_dict = {}
        flight_pv_dict = {}
        flight_if_buy_dict = {}
        flight_discount_dict = {}
        for i in delink_list:
            unit_tmp = c_sheet.cell_value(i, unit_index[1]).strip().upper()
            if unit_tmp == 'CPM':
                flight_unit_dict[i] = 'CPM'
            elif unit_tmp.startswith('DAY') or unit_tmp.startswith(u'天') or unit_tmp == '' or unit_tmp is None:
                flight_unit_dict[i] = '天'
            else:
                return {'ret':0, 'msg':'某些行单位错误！'}
            
            if c_sheet.cell_type(i, pv_index[1]) is xlrd.XL_CELL_NUMBER:
                flight_pv_dict[i] = c_sheet.cell_value(i, pv_index[1])
            else:
                #return {'ret':0, 'msg':str(i)+'行PV单元格格式错误！'}
                flight_pv_dict[i] = None
            
            if c_sheet.cell_value(i, if_buy_index[1]) == u'购买':
                flight_if_buy_dict[i] = True
            elif c_sheet.cell_value(i, if_buy_index[1]) == u'赠送':
                flight_if_buy_dict[i] = False
            else:
                return {'ret':0, 'msg':str(i+1)+'行购买方式出现错误！'}

            if c_sheet.cell_type(i, discount_index[1]) is xlrd.XL_CELL_NUMBER:
                if 0 <= float(c_sheet.cell_value(i, discount_index[1])) <= 1:
                    flight_discount_dict[i] = float(c_sheet.cell_value(i, discount_index[1]))
                else:
                    return {'ret':0, 'msg':str(i+1)+'行折扣不在0~100%之间！'}
            else:
                return {'ret':0, 'msg':str(i+1)+'行折扣格式错误！'}
        
        # retrieve info about DATE
        date_row = website_index[0]
        date_dict = {}
        for j in xrange(c_sheet.ncols):
            if c_sheet.cell_type(date_row, j) == xlrd.XL_CELL_DATE or c_sheet.cell_type(date_row, j) == xlrd.XL_CELL_NUMBER:
                month_tuple = xlrd.xldate_as_tuple(c_sheet.cell_value(date_row, j), 0)
                for day_row in xrange(date_row+1, date_row+3):
                    if c_sheet.cell_type(day_row, j) == xlrd.XL_CELL_NUMBER:
                        # 在单元格类型为NUMBER的情况下，check俩个点：1，数值是递增的，且在1~31之间；2，同列date_row所在行的单元格无数据
                        date_dict[j] = datetime.date(int(month_tuple[0]), int(month_tuple[1]), int(c_sheet.cell_value(day_row, j)))
                        continue_stat = True
                        for day_col in xrange(j+1, c_sheet.ncols):
                            if c_sheet.cell_type(day_row, day_col-1) == xlrd.XL_CELL_NUMBER and continue_stat:
                                if c_sheet.cell_value(day_row, day_col) > c_sheet.cell_value(day_row, day_col-1) and 1 <= c_sheet.cell_value(day_row, day_col) <= 31 and c_sheet.cell_type(date_row, day_col) != xlrd.XL_CELL_DATE and c_sheet.cell_type(date_row, day_col) != xlrd.XL_CELL_NUMBER:
                                    try:
                                        date_dict[day_col] = datetime.date(int(month_tuple[0]), int(month_tuple[1]), int(c_sheet.cell_value(day_row, day_col)))
                                    except Exception, e:
                                        return {'ret':0, 'msg':'行'+str(day_row+1)+'列'+str(day_col+1)+'出现错误！请确保日期准确！年：'+str(month_tuple[0])+'月：'+str(month_tuple[1])+'日：'+str(int(c_sheet.cell_value(day_row, day_col)))}
                                else:
                                    continue_stat = False
        
        if len(date_dict) == 0:
            return {'ret':0, 'msg':'日期获取错误！请确认日期标题(如"2009年7月")的格式为日期！'}
        
        # get start_day & end_day of this media planning
        date_key = date_dict.keys()
        date_key.sort()
        start_day = date_dict[date_key[0]]
        end_day = date_dict[date_key[-1]]
        
        # store date and spending info for every single flight
        flight_dateclick_dict = {}
        flight_startend_dict = {}
        for i in delink_list:
            flight_dateclick_dict[i] = {}
            flight_startend_dict[i] = {}
            flight_start_day_index 	= date_key[-1]
            flight_end_day_index	= date_key[0]
            for j in date_key:
                #if c_sheet.cell_type(i, j) != xlrd.XL_CELL_EMPTY and c_sheet.cell_value(i, j) is not None and c_sheet.cell_value(i, j) != '':
                if c_sheet.cell_type(i, j) == xlrd.XL_CELL_NUMBER:
                    if j < flight_start_day_index:
                        flight_start_day_index = j
                    if j > flight_end_day_index:
                        flight_end_day_index = j
                    if flight_unit_dict[i] == 'CPM':
                        flight_dateclick_dict[i][date_dict[j]] = int(c_sheet.cell_value(i, j))
                    elif flight_unit_dict[i] == '天':
                        try:
                            for day in xrange(int(c_sheet.cell_value(i, j))):
                                flight_dateclick_dict[i][date_dict[j+day]] = 1
                        except Exception, e:
                            return {'ret':0, 'msg':'行'+str(i+1)+'列'+str(j+1)+'出现错误！值为'+str(c_sheet.cell_value(i, j))}
                    else:
                        pass
            flight_startend_dict[i]['start_day']   	= date_dict[flight_start_day_index]
            flight_startend_dict[i]['end_day']		= date_dict[flight_end_day_index]
                    
        website_rowlist = []
        for i in xrange(delink_list[0], delink_list[-1]+1):
            c_value = c_sheet.cell_value(i, website_index[1])
            c_type = c_sheet.cell_type(i, website_index[1])
            if c_value is not None and c_value is not '':
                if c_type is not xlrd.XL_CELL_NUMBER:
                    website_rowlist.append({'index':i, 'name':c_value.strip().lower()})
                else:
                    return {'ret':0, 'msg':'第'+str(i+1)+'行媒体名称错误，不能为数值，请核对！'}
        for i in xrange(len(website_rowlist)-1):
            website_rowlist[i]['end'] = website_rowlist[i+1]['index'] - 1
        # Find end line for last website
        website_rowlist[-1]['end'] = website_rowlist[-1]['index']
        tmp_if_find = False
        for i in xrange(website_rowlist[-1]['index']+1, c_sheet.nrows):
            if (not tmp_if_find) and c_sheet.cell_type(i, website_index[1]) == xlrd.XL_CELL_EMPTY and c_sheet.cell_type(i, position_index[1]) != xlrd.XL_CELL_EMPTY:
                website_rowlist[-1]['end'] = i
            else:
                tmp_if_find = True

        # 通过计算来获得每条flight的总价和单价
        # 网站总价是定的，是我们付给网站的价格。由此根据比率来获得每个flight的实际总价。再用实际总价/投放量，就获得了实际单价。
        # First check every website has total price
        #for i in xrange(len(website_rowlist)):
        #    try:
        #        if c_sheet.cell_type(website_rowlist[i]['index'], website_price_index[1]) is xlrd.XL_CELL_EMPTY:
        #            website_price_weighted = website_rowlist[i-1]['totalprice']/website_rowlist[i-1]['ratio_weighted']
        #            for k in xrange(website_rowlist[i]['index'], website_rowlist[i]['end']+1):
        #                website_price_weighted += int(c_sheet.cell_value(k, totalprice_beforediscount_index[1]))
        #            website_rowlist[i]['ratio'] = 0
        #            website_rowlist[i]['ratio_weighted'] = website_rowlist[i-1]['totalprice']/float(website_price_weighted)
        #            website_rowlist[i-1]['ratio_weighted'] = website_rowlist[i]['ratio_weighted']
        #        else:
        #            website_price = int(c_sheet.cell_value(website_rowlist[i]['index'], website_price_index[1]))
        #            website_price_another = 0
        #            website_price_weighted = 0		# 用来记录生成加权价格
        #            for k in xrange(website_rowlist[i]['index'], website_rowlist[i]['end']+1):
        #                if c_sheet.cell_type(k, totalprice_index[1]) != xlrd.XL_CELL_EMPTY and c_sheet.cell_type(k, totalprice_index[1]) != xlrd.XL_CELL_TEXT:
        #                    website_price_another += int(c_sheet.cell_value(k, totalprice_index[1]))
        #                website_price_weighted += int(c_sheet.cell_value(k, totalprice_beforediscount_index[1]))
        #            website_rowlist[i]['totalprice'] = website_price
        #            website_rowlist[i]['ratio'] = website_price/float(website_price_another)
        #            website_rowlist[i]['ratio_weighted'] = website_price/float(website_price_weighted)		# 此加权系数将赠送的广告位的价位也考虑进来
        #    except Exception, e:
        #        return {'ret':0, 'msg':e.message+' line: '+str(i)}

        # 找到网站总价，以及折上折信息
        for i in xrange(len(website_rowlist)):
            try:
                website_price = int(c_sheet.cell_value(website_rowlist[i]['index'], website_price_index[1]))
                sum_adform_price = 0
                for k in xrange(website_rowlist[i]['index'], website_rowlist[i]['end']+1):
                    if flight_if_buy_dict.get(k, False) == True:
                        sum_adform_price += flight_totalprice_dict[k]
                website_rowlist[i]['totalprice'] = website_price
                website_rowlist[i]['discount_after_discount'] = website_price/float(sum_adform_price) if sum_adform_price > 0 else 0
            except Exception, e:
                return {'ret':0, 'msg':str(e.message)+' & 第'+str(i+1)+'个网站总价存在问题，请确保其有单独总价并且是在该网站的起始列！'}
                # return {'ret':0, 'msg':[website_price, sum_adform_price, flight_totalprice_dict, flight_if_buy_dict]}
            
        #return website_rowlist
        ### put data into DB
        ### using transaction manually!!!
        # checkin AD/Campaign info
        ads = Ad.objects.filter(DE_campaign_id=campaign_id)
        if len(ads) > 0: # create new Ad in this situation
            for ad in ads:
                delete_mp(ad.DE_campaign_id)
        try:
            client = Client.objects.get(id=client_id)
        except ObjectDoesNotExist:
            return {'ret':0, 'msg':'Client ID错误！'}
        try:
            at = ActivityType.objects.get(id=activitytype_id)
        except ObjectDoesNotExist:
            return {'ret':0, 'msg':'ActivityType ID错误！'}

        # here add a action to clear trash info in MC db
        clear_trashinfo()
        
        ad = Ad(client=client, activity_type=at, DE_campaign_id=campaign_id, name=mp_name, start_day=start_day, end_day=end_day, uploader=uploader)
        ad.save()
        for staff_id in related_staff:
            adrs = AdRelatedStaff(ad=ad, staff_id=staff_id)
            adrs.save()
        
        ad_spending = 0				# store real spending
                
        de_db = pyodbc.connect('DRIVER={Oracle};SERVER=211.94.190.64;DATABASE=dart;UID=mediachooser_read;PWD=read_mediachooser;')
        
        for website in website_rowlist:
            # check & put website info into DB, get website's ID.
            website_row_index = website['index']
            discount_after_discount = website['discount_after_discount']
            ad_spending += website['totalprice']
            try:
                media = Media.objects.get(c_name = website['name'])
            except ObjectDoesNotExist:
                transaction.rollback()
                return {'ret':0, 'msg':'媒体 "' + website['name'].encode('utf8') + '" 在数据库中不存在，请检查名称是否正确，若确实不存在，请找相关人员进行添加！'}
            
            # checkin postion & adform info
            channel_name_set = set()
            adform_dict = {}
            for channel in media.related_channels.all():
                channel_name = channel.c_name.strip().lower()
                channel_name_set.add(channel_name)
                adform_dict[channel_name] = set()
                for adform in MediaAdInfo.objects.filter(channel=channel):
                    adform_dict[channel_name].add(adform.adform)
            for i in delink_list:
                if website_row_index <= i <= website['end']:
                    channel_name = c_sheet.cell_value(i, position_index[1]).strip().lower().replace(' ', '') 	# Remove spaces
                    if channel_name in channel_name_set:
                        channel = Channel.objects.get(media=media, c_name=channel_name)
                    else:
                        channel = Channel(media=media, c_name=channel_name)
                        channel.save()
                        channel_name_set.add(channel_name)
                        adform_dict[channel_name] = set()
                    adform_name = c_sheet.cell_value(i, adform_index[1]).strip().lower().replace(' ', '')		# Remove spaces
                    if adform_name in adform_dict[channel_name]:
                        adform = MediaAdInfo.objects.get(media=media, channel=channel, adform=adform_name)
                    else:
                        try:
                            adform = MediaAdInfo(media=media, channel=channel, adform=adform_name, adsize_detail=c_sheet.cell_value(i, size_index[1]).strip().lower())
                            adform.save()
                        except Exception, e:
                            transaction.rollback()
                            return {'ret':0, 'msg':'可能广告规格过长。请检查广告规格的描述是否在128个中文字符以内！'}
                        adform_dict[channel_name].add(adform_name)
                        
                    try:
                        flight = Flight.objects.get(ad=ad, DE_campaign_id=campaign_id, DE_flight_id=mp_flight_ad_id_dict[i][0])
                    except ObjectDoesNotExist:
                        spending = int(c_sheet.cell_value(i, spending_index[1]))
                        unit_price = flight_price_dict[i]
                        #total_price = float(c_sheet.cell_value(i, totalprice_index[1]))
                        total_price = flight_totalprice_dict[i]
                        unit_price_weighted = 0
                        total_price_weighted = 0

                        DE_flight_id, ngAdID = mp_flight_ad_id_dict[i]
                        clickurl = ''
                        sql = 'select clickurl from admanager65.ng_ads where id=%s' % str(ngAdID)
                        de_cursor = de_db.cursor()
                        de_cursor.execute(sql)
                        for row in de_cursor:
                            if row[0] is not None:
                                clickurl = row[0]
                        de_cursor.close()
                        click = 0
                        DE_backend_url = c_sheet.cell_value(i, code_index[1])
                        flight = Flight(ad=ad, media=media, channel=channel, media_ad_info=adform, spending=spending, unit=flight_unit_dict[i], ad_days=len(flight_dateclick_dict[i]), discount=flight_discount_dict[i], unit_price=unit_price, total_price=total_price, click=click, DE_backend_url=DE_backend_url, DE_campaign_id=campaign_id, DE_flight_id=DE_flight_id, start_day=flight_startend_dict[i]['start_day'], end_day=flight_startend_dict[i]['end_day'], unit_price_weighted=unit_price_weighted, total_price_weighted=total_price_weighted, if_buy=flight_if_buy_dict[i], pv=flight_pv_dict[i], discount_after_discount=discount_after_discount, DE_ad_id=ngAdID, clickurl=clickurl)
                        flight.save()

                    # put detailed click data into DE_ClickData. From table ng_sum_fixed_h, not from view ng_sum_fixed.
                    sql = 'select startdate, sum(eventcount) from admanager65.ng_sum_fixed_h where flightid='+str(flight.DE_flight_id)+' and eventtype=4 group by startdate'
                    de_cursor = de_db.cursor()
                    de_cursor.execute(sql)
                    de_clickdata_ret_dict = {}
                    for row in de_cursor:
                        de_clickdata_ret_dict[row[0].date()]=(4, int(row[1]*settings.CLICK_COMPENSATION_COEFFICIENT))
                        #de_clickdata_ret_dict[row[0].date()]=(4, row[1])
                    de_cursor.close()

                    ad_days_tracked = 0
                    for day in flight_dateclick_dict[i]:
                        try:
                            de_clickdata = DE_ClickData.objects.get(flight=flight, date=day)
                        except ObjectDoesNotExist:
                            if flight.unit == 'CPM':
                                de_clickdata = DE_ClickData(ad=ad, media=media, channel=channel, media_ad_info=adform, flight=flight, date=day, cpm=flight_dateclick_dict[i][day], if_planned_spending=True)
                            else:
                                de_clickdata = DE_ClickData(ad=ad, media=media, channel=channel, media_ad_info=adform, flight=flight, date=day, if_planned_spending=True)
                            de_clickdata.save()
               
        ad.spending = ad_spending
        ad.save()

        # just refresh this mp's click & cpc info, its lazy manipulation. It's better to simple above calculation.
        refresh_mp(campaign_id)
        
        # only after all data push is OK, then manually commit transaction
        transaction.commit()

        # save media planning file
        file_save_name = path.join(settings.UPLOADED_MP_DIR, time.strftime('%Y%m%d%H%M%S', time.localtime())+'-'+str(campaign_id)+'.xls')
        file_to_save = open(file_save_name, 'w')
        file_save = File(file_to_save)
        file_save.write(file_contents)
        file_save.close()
        
    	msg = '排期 "' + mp_name.encode('utf8') + '" 导入成功！'
        return {'ret':1, 'msg':msg}

#    except Exception, e:
        # transaction.rollback()
#        return {'ret':0, 'msg':e.message}

@login_required
def upload(request):
    if request.method == "POST":
        # get uploaded media planning file and other parameters
        for tt in request.FILES:
            uploaded_file = request.FILES[tt]

        client_id = int(request.POST.get('client', 0))
        activitytype_id = int(request.POST.get('activity_type', 0))
        campaign_id = int(request.POST.get('campaign', 0))
        related_staff = request.POST.getlist('related_staff')

        # process the media planning, write related infos to DB
        mp_name = '.'.join(uploaded_file.name.split('.')[:-1]) # get mp name
        ret = mp_handler(uploaded_file.read(), mp_name, client_id, activitytype_id, request.user, related_staff, campaign_id)

        # set status message
        clients = Client.objects.all().order_by('c_name')
        activity_types = ActivityType.objects.all()
        staff = User.objects.exclude( Q(email='') | Q(username='admin') | Q(username='root')).order_by('username')
        recent_uploaded = Ad.objects.filter(create_time__gte=datetime.date.today()-datetime.timedelta(days=7)).order_by('-create_time')
        return render_to_response('media_planning/mp_upload.html', locals(), context_instance=RequestContext(request))
    else:
        clients = Client.objects.all().order_by('c_name')
        activity_types = ActivityType.objects.all()
        user = request.user
        staff = User.objects.exclude( Q(email='') | Q(username='admin') | Q(username='root')).order_by('username')
        recent_uploaded = Ad.objects.filter(create_time__gte=datetime.date.today()-datetime.timedelta(days=7)).order_by('-create_time')
        return render_to_response('media_planning/mp_upload.html', locals(), context_instance=RequestContext(request))

@login_required
def my_uploads(request):
    user = request.user
    uploads = Ad.objects.filter(uploader=user).order_by('-create_time')
    return render_to_response('media_planning/my_uploads.html', locals(), context_instance=RequestContext(request))

@login_required
def uploads_checkout(request):
    if request.method == "POST":
        user = request.user
        uploaders_list = Ad.objects.distinct('uploader').values_list('uploader')
        uploaders = User.objects.filter(id__in = [ i[0] for i in uploaders_list ])
        uploader = User.objects.get(id=int(request.POST.get('uploader')))
        start_day = request.POST.get('start_day', '')
        end_day = request.POST.get('end_day', '')
        # get mps from DE
        de_db = pyodbc.connect('DRIVER={Oracle};SERVER=211.94.190.64;DATABASE=dart;UID=mediachooser_read;PWD=read_mediachooser;')
        de_cursor = de_db.cursor()
        sql = 'select a.id, a.name from admanager65.ng_insertionorders a, admanager65.ng_contacts b where a.createdbyuserid = b.linkuserid and b.email=\'%s\'' % str(uploader.email)
        if start_day != '' :
            sql += 'and a.creationdate >= to_date(\'%s\', \'YYYY-MM-DD\')' % str(start_day)
        if end_day != '' :
            sql += 'and a.creationdate <= to_date(\'%s\', \'YYYY-MM-DD\')' % str(end_day)
        de_cursor.execute(sql)
        de_mp_dict = dict()
        for row in de_cursor:
            de_mp_dict[row[0]] = row[1]
        de_cursor.close()
        # print de_mp_dict
        uploaded_num = 0
        for mp_id in de_mp_dict:
            try:
                mp = Ad.objects.get(DE_campaign_id = mp_id)
                de_mp_dict[mp_id] = mp.name
                uploaded_num += 1
            except ObjectDoesNotExist:
                de_mp_dict[mp_id] = '未上传'
                
        return render_to_response('media_planning/uploads_checkout.html', locals(), context_instance=RequestContext(request))
    else:
        user = request.user
        uploaders_list = Ad.objects.distinct('uploader').values_list('uploader')
        uploaders = User.objects.filter(id__in = [ i[0] for i in uploaders_list ])
        return render_to_response('media_planning/uploads_checkout.html', locals(), context_instance=RequestContext(request))

# Make Media table clean
def clean_media():
    for media in Media.objects.all():
        media.c_name = media.c_name.strip().lower()
        media.save()
        merge_channel(media.id)

# @login_required
def merge_media(media_id, duplicated_media_id):
    # Change duplicated_media_id to media_id for all related tables, include Channel, MediaAdInfo, Flight, DE_ClickData
    # Update related tables
    try:
        media_one = Media.objects.get(id = media_id)
        media_dup = Media.objects.get(id = duplicated_media_id)
    except ObjectDoesNotExist:
        print 'The medias u specified r not exist!'
        return False
    from django.db import connection, transaction
    cursor = connection.cursor()

    cursor.execute('update media_channel set media_id=%s where media_id=%s', [media_id, duplicated_media_id])
    transaction.commit_unless_managed()
    cursor.execute('update media_mediaadinfo set media_id=%s where media_id=%s', [media_id, duplicated_media_id])
    transaction.commit_unless_managed()
    cursor.execute('update media_planning_flight set media_id=%s where media_id=%s', [media_id, duplicated_media_id])
    transaction.commit_unless_managed()
    cursor.execute('update media_planning_de_clickdata set media_id=%s where media_id=%s', [media_id, duplicated_media_id])
    transaction.commit_unless_managed()
    
    # At last, call merge_channel
    merge_channel(media_id)

# @login_required
def merge_channel(media_id):
    # For same media, merge the channels owning the same name
    # Remove spaces in channels' name # Find same name channels, store them into dict. {channel_name:[channel_id_1, channel_id_2, ...]}
    try:
        media = Media.objects.get(id = media_id)
    except ObjectDoesNotExist:
        print 'The media dose not exist!'
        return False
    channel_name_dict = {}
    for channel in media.related_channels.all():
        channel.c_name = channel.c_name.replace(' ', '')
        channel.save()
        if channel_name_dict.has_key(channel.c_name):
            channel_name_dict[channel.c_name].append(channel.id)
        else:
            channel_name_dict[channel.c_name] = [channel.id]
    
    # Then, update related tables
    from django.db import connection, transaction
    cursor = connection.cursor()
    
    for val in channel_name_dict.values():
        if len(val) > 1:
            val.sort()
            for i in val[1:]:
                cursor.execute('update media_mediaadinfo set channel_id=%s where channel_id=%s', [val[0], i])
                transaction.commit_unless_managed()
                cursor.execute('update media_planning_flight set channel_id=%s where channel_id=%s', [val[0], i])
                transaction.commit_unless_managed()
                cursor.execute('update media_planning_de_clickdata set channel_id=%s where channel_id=%s', [val[0], i])
                transaction.commit_unless_managed()
                channel = Channel.objects.get(id = i)
                channel.delete()
    # At last, call merge_flight channels needed
    for channel in media.related_channels.all():
        merge_flight(channel)

# @login_required
# Here, flight just means MediaAdInfo
def merge_flight(channel):
    # Remove spaces in flights' name
    # Find flights owning same name under same one channel, merge them
    # Find same name flights, update related tables
    flight_name_dict = {}
    for flight in channel.related_adinfo.all():
        flight.adform = flight.adform.replace(' ', '')
        flight.save()
        if flight_name_dict.has_key(flight.adform):
            flight_name_dict[flight.adform].append(flight.id)
        else:
            flight_name_dict[flight.adform] = [flight.id]
    
    from django.db import connection, transaction
    cursor = connection.cursor()
    
    for val in flight_name_dict.values():
        if len(val) > 1:
            val.sort()
            for i in val[1:]:
                cursor.execute('update media_planning_flight set media_ad_info_id=%s where media_ad_info_id=%s', [val[0], i])
                transaction.commit_unless_managed()
                cursor.execute('update media_planning_de_clickdata set media_ad_info_id=%s where media_ad_info_id=%s', [val[0], i])
                transaction.commit_unless_managed()
                flight = MediaAdInfo.objects.get(id = i)
                flight.delete()

def check_omniturecode(date):
    # Find flights which will displayed at that day, and client is Lenovo
    planned_spends = DE_ClickData.objects.filter(date = date)
    planned_flights_set = set()
    for spend in planned_spends:
        if spend.ad.client_id == 1: 
            planned_flights_set.add(spend.flight)
    # Refer DC database to find out clickurls, stored in dict {'url1':[ad_id, ad_id, ...], 'url2':[], ...}
    url_dict = {}
    de_db = pyodbc.connect('DRIVER={Oracle};SERVER=211.94.190.64;DATABASE=dart;UID=mediachooser_read;PWD=read_mediachooser;')
    for flight in planned_flights_set:
        clickurl = ''
        sql = 'select clickurl from admanager65.ng_ads where id=%s' % str(flight.DE_ad_id)
        de_cursor = de_db.cursor()
        de_cursor.execute(sql)
        for row in de_cursor:
            if row[0] is not None:
                clickurl = row[0]
        de_cursor.close()
        if clickurl is not '':
            if url_dict.has_key(clickurl):
                url_dict[clickurl].append(flight)
            else:
                url_dict[clickurl] = [flight]
    # Check out such URLs to c if omniture code been embedded
    nosc_url_dict = {}
    cantopen_url_dict = {}
    for url in url_dict:
        try:
            page = urllib2.urlopen(url)
            page_cont = page.read()
            sitecatalyst_re_ret = re.search('SiteCatalyst', page_cont)
            if sitecatalyst_re_ret is None:
                nosc_url_dict[url] = url_dict[url]
        except Exception, e:
            # return {'error':"Cant open the following click URL: " + str(url)}
            cantopen_url_dict[url] = url_dict[url]
    # Return URLs of no omniture code
    return nosc_url_dict, cantopen_url_dict
