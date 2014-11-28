from django.core.management.base import BaseCommand
from brief_proc import get_campaigns
from datetime import date, datetime

import dumpDE

from MediaChooser.ad.models import DE_ClickData, DE_Cmpaign_Processed, Ad, MediaAdInfo
from MediaChooser.media.models import Media, Channel
from MediaChooser.media_planning.models import MediaPlanning
from MediaChooser.misc.models import Company

import re
from cPickle import load
from django.core.exceptions import ObjectDoesNotExist



def gbk_to_utf8(s):
    try:
        try:
            return s.decode('gb2312').encode('utf-8')
        except:
            return s.encode('utf-8')
    except:
        return s


media_domains = load(open('media.dct'))
def _add_media(s):
    media, created = Media.objects.get_or_create(
            c_name = gbk_to_utf8(s),
            defaults = {'domain' : media_domains[s]}
        )
    return media

def _add_channel(m, c):
    channel, created = Channel.objects.get_or_create(
            media  = m,
            weight ='\xe4\xb8\xad',
            c_name = gbk_to_utf8(c)
        )
    return channel


size_matcher    = re.compile(r'(\d+)[^\d]+(\d+)')
ad_forms        = ['swf', 'flash', 'jpg', 'jpeg', 'flv', 'gif', u'\u6587\u5b57\u94fe', u'\u56fe\u7247']
form_matchers   = [re.compile(i, re.I) for i in ad_forms]
fsize_matcher_k  = re.compile(r'\D(\d+)k', re.I)
fsize_matcher_m  = re.compile(r'\D(\d+)m', re.I)

def _add_mediaadinfo(flg):
    ad_standard = flg[u'\u5e7f\u544a\u89c4\u683c'] 

    try:ad_size = '%s * %s'%size_matcher.search(ad_standard).groups()
    except:ad_size = ''

    try:
        try:
            file_size = int(fsize_matcher_k.search(ad_standard).groups()[0])
        except:
            file_size = 1024 * int(fsize_matcher_m.search(ad_standard).groups()[0])
    except: 
        file_size = 0

    try:
        ad_form = ('/').join([i.search(ad_standard).group() for i in form_matchers if i.search(ad_standard)])
    except:
        ad_form = ''

    _media = _add_media(flg[u'\u7f51\u7ad9'])
    info, created = MediaAdInfo.objects.get_or_create(
            media       = _media,
            channel     = _add_channel(_media, flg[u'\u5e7f\u544a\u4f4d\u7f6e']),
            adsize      = ad_size,
            adfilesize  = file_size,
            adformat    = gbk_to_utf8(ad_form),
            adform_detail   = gbk_to_utf8(flg[u'\u5e7f\u544a\u5f62\u5f0f'])
        )

    return info


def _add_company(company_name):
    company_name = gbk_to_utf8(company_name)

    company, created = Company.objects.get_or_create(
            c_name = company_name,
            defaults = {'if_client' : True}
        )
    return company


def _add_ad(DE_flg_id):
    ad_info = dumpDE.get_campaign_by_flightid(DE_flg_id)[0]

    ad, created = Ad.objects.get_or_create(
            DE_campaign_id = ad_info[0],
            defaults = {
                'name'          : gbk_to_utf8(ad_info[1]),
                'client'        : _add_company(gbk_to_utf8(ad_info[2])),
                'start_day'     : ad_info[3].date(),
                'end_day'       : ad_info[4].date(),
                'create_time'   : ad_info[5],
                'last_modified' : ad_info[6],
            }
        )
    return ad


def _add_flight(ad_amnt, ad_amnt_u, u_price, discount, DE_flg_id, t_price):
    MediaPlanning(
            ad              = _add_ad(DE_flg_id),
            ad_amount       = ad_amnt,
            ad_amount_unit  = ad_amnt_u,
            unit_price      = u_price, 
            discount        = discount,
            click           = 0,
            DE_flight_id    = DE_flg_id,
            total_price     = t_price
        ).save()
    pass


def _add_clicks_by_campaigns():
    camp_set = get_campaigns()
    print '\tdumping data from DE...'

    print '\tinsert to MediaChooser database...'
    for camp in camp_set:
        cur_flighs = []
        camp_id = camp['CmpgnID']

        #1.is the flight already in MC DB?
        for flg_id, flg_name, flg_num in dumpDE.get_flights_by_campaign(camp_id):
            print type(flg_name), flg_name

            flg_name = gbk_to_utf8(flg_name)

            if 0 == len(DE_Cmpaign_Processed.objects.filter(
                        campaignid = camp_id,
                        flightid   = flg_id,
                        flightnum  = flg_num,
                        flightname = flg_name
                    )
                ):
                cur_flg = DE_Cmpaign_Processed(
                        campaignid = camp_id, 
                        flightname = flg_name,
                        flightid   = flg_id,
                        flightnum  = flg_num
                    )
                cur_flighs.append(cur_flg)

        #2.insert flights.
        for i in cur_flighs:
            #2.1 insert infomation of flight
            try:
                for flg_num, flg_dct in camp['flights']:
                    if flg_num == i.flightnum - 1:
                        _add_flight(
                                DE_flg_id   = i.flightid, 
                                ad_amnt     = flg_dct[u'\u6295\u653e\u91cf'], 
                                ad_amnt_u   = flg_dct[u'\u5355\u4f4d'], 
                                u_price     = flg_dct[u'\u520a\u4f8b\u5355\u4ef7'], 
                                discount    = flg_dct[u'\u6298\u6263'], 
                                t_price     = flg_dct[u'\u6298\u540e\u603b\u4ef7'], 
                            )
            except Exception, e:
                print e.message 
            #2.2 remember not to process this flight again
            i.save()


        week_days = ['M', 'T', 'W', 'T', 'F', 'S', 'S']
        #3.insert clicks
        for flg_num, flight in camp['flights']:
            for flg_id, event_type, event_count, start_date in dumpDE.get_clicks_by_campaign(camp_id, flg_num):
                _in_planning = True
                for (_year, _month), _day, _weekday in flight['DATEs']:
                    if (_day, _weekday) == (start_date.day, week_days[start_date.weekday()]):
                        _in_planning = True
                        break
                else:
                    _in_planning = False

                try:
                    flg = MediaPlanning.objects.get(DE_flight_id=flg_id)
                    flg.media_ad_info = _add_mediaadinfo(flight)
                    flg.save()
                    DE_ClickData(
                            flight      = flg, 
                            eventtype   = event_type,
                            eventcount  = event_count,
                            date        = start_date,
                            in_planning = _in_planning
                        ).save()
                except ObjectDoesNotExist, e:
                    print e.message
    return 


class Command(BaseCommand):
    def handle(self, *args, **options):
        _add_clicks_by_campaigns()
        print 'complete'
