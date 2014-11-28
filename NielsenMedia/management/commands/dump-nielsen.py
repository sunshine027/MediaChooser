#! /usr/bin/env python
#coding=utf-8

import re, urllib2, os
from HTMLParser import HTMLParser

import xlrd

from django.core.management.base import BaseCommand
from MediaChooser import settings
from MediaChooser.NielsenMedia.models import NielsenCategory, NielsenMedia, NielsenChannel, \
    NielsenTrafficData, Province, NielsenOverlap
from MediaChooser.utility.nielsen_dumper import get_download_idx

Headers = {
        'Host': 'services.cr-nielsen.com', 
        'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6', 
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8', 
        'Accept-Language': 'zh-cn,zh;q=0.5', 
        'Accept-Encoding': 'gzip,deflate', 
        'Accept-Charset': 'gb2312,utf-8;q=0.7,*;q=0.7', 
        'Keep-Alive': '300', 
        'Connection': 'keep-alive',
        'Referer': 'http://services.cr-nielsen.com/CR-NetRatings/login.jsp',
    }

RE_DOMAIN = '\w+.(com.cn|sh.cn|com|net|org|cn|tv)'

filepath = os.path.abspath(os.path.split(settings.__file__)[0])
#print filepath
XLS_PREFIX = os.path.join(filepath, 'utility/xls')

def _open(URL, POSTDATA=''):
    if POSTDATA:
        req = urllib2.Request(url=URL, headers=Headers, data=POSTDATA)
    else:
        req = urllib2.Request(url=URL, headers=Headers)
    return urllib2.urlopen(req)

def _open_xls(xls):
    wb = xlrd.open_workbook(xls)
    try:
        sh = wb.sheet_by_name("Sheet0")
    except:
        print "No sheet in %s named Sheet0" % xls
        return None
    return sh
    
def dump_province():
    """
        dump province data and save to database
    """
    src_html = _open(
            URL='http://services.cr-nielsen.com/CR-NetRatings/excelList/pub.ExcelIndex.do', 
            POSTDATA='week=%s'% get_download_idx()
        ).read()

    class Parser(HTMLParser):
        def handle_starttag(self, tag, attrs):
            if tag == 'a':
                for name,value in attrs:
                    if name == 'title':
                        if value.startswith("网站省级排名"):
                            e_name, c_name = value.split('_')[1].split('-')
                            p = Province.objects.get_or_create(e_name= e_name, c_name=c_name)
                            
    psr = Parser()
    psr.feed(src_html)
    
    Province.objects.get_or_create(e_name= 'all', c_name=u'全国')

def save_category(main_category_name, sub_category_name):
    
    main_category = sub_category = ''
    
    if main_category_name == u'暂无分类':
        main_category_name = ''
    else:
        main_category_e_name, main_category_c_name = main_category_name.split('-')
        main_category, flag = NielsenCategory.objects.get_or_create(e_name= main_category_e_name, c_name= main_category_c_name)
    
    if sub_category_name == u'暂无子分类':
        sub_category_name = ''
    else:
        sub_category_ename, sub_category_cname = sub_category_name.split('-')
        if main_category:
            cate = NielsenCategory.objects.get(e_name= main_category_name.split('-')[0])
            sub_category, flag = NielsenCategory.objects.get_or_create(e_name= sub_category_ename, c_name= sub_category_cname, parent= cate)
        else:
            sub_category, flag = NielsenCategory.objects.get_or_create(e_name= sub_category_ename, c_name= sub_category_cname)
    return main_category, sub_category

def save_media(media_domain, media_cname, media_ename, main_category, sub_category):
    
    if main_category == '':
        m, flag = NielsenMedia.objects.get_or_create(domain=media_domain, c_name=media_cname, e_name= media_ename)
    elif sub_category == '':
        m, flag = NielsenMedia.objects.get_or_create(domain=media_domain, c_name=media_cname, e_name= media_ename, main_category= main_category)
    else:
        m, flag = NielsenMedia.objects.get_or_create(domain=media_domain, c_name=media_cname, e_name= media_ename, main_category= main_category, sub_category= sub_category)
    return m

def save_channel(media_domain, c_media, media_cname, media_ename, main_category, sub_category):

    if c_media== '':
       c_media = None
       e_name =  media_domain
    else:
       e_name = c_media.e_name + ' ' + media_ename
    if main_category == '':
        c, flag = NielsenChannel.objects.get_or_create(domain=media_domain, media=c_media, c_name=media_cname,e_name= e_name)
    elif sub_category == '':
        c, flag = NielsenChannel.objects.get_or_create(domain=media_domain, media=c_media, c_name=media_cname,e_name= e_name, main_category= main_category)
    else:
        c, flag = NielsenChannel.objects.get_or_create(domain=media_domain, media=c_media, c_name=media_cname,e_name= e_name, main_category= main_category, sub_category= sub_category)
    return c
    
def dump_province_rank(week):
    
    provinces = Province.objects.all()
    for p in provinces:
        if p.e_name == 'all':
            continue
        #xls = XLS_PREFIX + u"网站省级排名_" + p.e_name + '-' + p.c_name + '.xls'
        xls = os.path.join(XLS_PREFIX, u"网站省级排名_" + p.e_name + '-' + p.c_name + '.xls')
        sh = _open_xls(xls)
        
        # 200 rank data per xls file
        for i in range(4,204):
            media_name = sh.cell_value(i,4)
            print "dumping " + media_name
            media_domain = media_name.split('-')[0]
            media_cname = media_name.split('-')[-1]
            media_ename = media_domain.split('.')[0]
                
            main_category, sub_category = save_category(sh.cell_value(i,5), sh.cell_value(i,6))
            
            level = sh.cell_value(i,7) # media or channel
            sample_ub = sh.cell_value(i,8)
            sample_ts = sh.cell_value(i,9)
            sample_ub_freq = sh.cell_value(i,10)
            sample_asd = sh.cell_value(i,11)
            
            if level == u'品牌':
                m = save_media(media_domain, media_cname, media_ename, main_category, sub_category)
                nt_data = NielsenTrafficData.objects.get_or_create(media=m, province=p, sample_ub=sample_ub, sample_ts=sample_ts, sample_ub_freq=sample_ub_freq, sample_asd=sample_asd, week=week)
            elif level == u'频道':
                domain = re.search(RE_DOMAIN, media_domain).group()
                c_media = NielsenMedia.objects.get(domain= domain)
                c = save_channel(media_domain, c_media, media_cname, media_ename, main_category, sub_category)
                nt_data = NielsenTrafficData.objects.get_or_create(channel=c, province=p, sample_ub=sample_ub, sample_ts=sample_ts, sample_ub_freq=sample_ub_freq, sample_asd=sample_asd, week=week)

def dump_overall_rank(week):
    
    #xls = XLS_PREFIX + u'全国网站排名_全部网站.xls'
    xls = os.path.join(XLS_PREFIX, u'全国网站排名_全部网站.xls')
    sh = _open_xls(xls)
    nrow = sh.nrows
    channel_to_dump = []
    p = Province.objects.get(e_name='all')
    # nrow-1-1
    for i in range(4, nrow-2):
        media_name = sh.cell_value(i,4)
        print "dumping " + media_name
        media_domain = '-'.join(media_name.split('-')[:-1])
        media_cname = media_name.split('-')[-1]
        media_ename = media_domain.split('.')[0]
        level = sh.cell_value(i,7) # media or channel
        sample_ub = sh.cell_value(i,13)
        sample_ts = sh.cell_value(i,14)
        sample_ub_freq = sh.cell_value(i,15)
        sample_asd = sh.cell_value(i,16)
        
        main_category, sub_category = save_category(sh.cell_value(i,5), sh.cell_value(i,6))
        
        if level == u'品牌':
            m = save_media(media_domain, media_cname, media_ename, main_category, sub_category)
            nt_data = NielsenTrafficData.objects.get_or_create(media=m, province=p, sample_ub=sample_ub, sample_ts=sample_ts, sample_ub_freq=sample_ub_freq, sample_asd=sample_asd, week=week)

        elif level == u'频道':
            domain = re.search(RE_DOMAIN, media_domain).group()
            try:
                c_media = NielsenMedia.objects.get(domain= domain)
                c = save_channel(media_domain, c_media, media_cname, media_ename, main_category, sub_category)
                nt_data = NielsenTrafficData.objects.get_or_create(channel=c, province=p, sample_ub=sample_ub, sample_ts=sample_ts, sample_ub_freq=sample_ub_freq, sample_asd=sample_asd, week=week)
            except NielsenMedia.DoesNotExist:
                channel_to_dump.append(i)
        else:
            continue
        
    print channel_to_dump
    
    for c in channel_to_dump:
        c = int(c)
        media_name = sh.cell_value(c,4)
        print "dumping " + media_name
        media_domain = '-'.join(media_name.split('-')[:-1])
        media_cname = media_name.split('-')[-1]
        media_ename = media_domain.split('.')[0]
        sample_ub = sh.cell_value(c,13)
        sample_ts = sh.cell_value(c,14)
        sample_ub_freq = sh.cell_value(c,15)
        sample_asd = sh.cell_value(c,16)
        
        main_category, sub_category = save_category(sh.cell_value(c,5), sh.cell_value(c,6))
        
        domain = re.search(RE_DOMAIN, media_domain).group()
        try:
            c_media = NielsenMedia.objects.get(domain= domain)
        except NielsenMedia.DoesNotExist:
            c_media = ''
        c = save_channel(media_domain, c_media, media_cname, media_ename, main_category, sub_category)
        nt_data = NielsenTrafficData.objects.get_or_create(channel=c, province=p, sample_ub=sample_ub, sample_ts=sample_ts, sample_ub_freq=sample_ub_freq, sample_asd=sample_asd, week=week)

def dump_overlap(week):
    
    from MediaChooser.utility.nielsen_dumper import get_overlap_files
    sid, titles = get_overlap_files(week)
    
    for t in titles:
        print "dumping overlap %s" % t
        xls = XLS_PREFIX + u'%s_overlap.xls' % t
        sh = _open_xls(xls)
        ma_domain = sh.cell_value(5,0).split('-')[0]
        ma = NielsenMedia.objects.get(domain= ma_domain)
        
        for i in range(8, 8+len(titles)-1):
            mb_domain = sh.cell_value(i,0).split('-')[0]
            mb = NielsenMedia.objects.get(domain= mb_domain)
            ub_dup = sh.cell_value(i,2)
            net_ub = sh.cell_value(i,3)
            dup = sh.cell_value(i,4)
            NielsenOverlap.objects.get_or_create(media_a=ma, media_b=mb, net_ub=net_ub, ub_dup=ub_dup, dup=dup, week=week)
                

class Command(BaseCommand):

    def handle(self, *args, **options):
        week = get_download_idx()
        dump_province()
        dump_province_rank(week)
        dump_overall_rank(week)
        dump_overlap(week)