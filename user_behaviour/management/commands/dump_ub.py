#encoding=utf8
import pyodbc
import datetime
import cPickle as pickle

from django.core.management.base import BaseCommand

from MediaChooser.user_behaviour.models import UserBehaviour
from MediaChooser.media_planning.models import Flight

de_db = pyodbc.connect('DRIVER={Oracle};SERVER=211.94.190.64;DATABASE=dart;UID=mediachooser_read;PWD=read_mediachooser;')

site_common_table_name = 'admanager65.NG_ANA_MINISITECOMMON_H'
site_uv_table_name = 'admanager65.NG_ANA_MINISITEUV'

event_impression = 3
event_sitetime = 102

cursor = None

class Command(BaseCommand):

    def handle(self, *args, **options):
        results = fill_user_behaviour('2009-11-24')
        if results:
            for r in results:
                #print r
                pass
                
            cursor = None
            de_db.close()
        
def fill_user_behaviour(startdate):
    
    ub_data = []
    
    cursor = de_db.cursor()
    
    impression_sql = 'select minisite_raw as minisite, flightid, sum(impressions) as impresssions, sum(pages_raw*impressions) as total_pages \
                from %s where startdate =to_date(\'%s\',\'YYYY-MM-DD\') \
                and eventtype=%s and minisite_raw is not null and pages_raw is not null \
                and upper(NGADID_RAW)=lower(NGADID_RAW) \
                group by minisite_raw, flightid' % (site_common_table_name, startdate, event_impression)
    
    landing_sql = 'select minisite_raw as minisite, flightid, count(*) as frompages \
                from %s where startdate =to_date(\'%s\',\'YYYY-MM-DD\') \
                and eventtype=%s and minisite_raw is not null and pages_raw is not null \
                and upper(NGADID_RAW)=lower(NGADID_RAW) \
                and (frompage_raw is null or frompage_raw =\'/\') \
                group by minisite_raw, flightid' % (site_common_table_name, startdate, event_impression)
    
    bounce_sql = 'select minisite_raw as minisite, flightid, count(*) as frompages \
                from %s where startdate =to_date(\'%s\',\'YYYY-MM-DD\') \
                and eventtype=%s and minisite_raw is not null and pages_raw is not null \
                and upper(NGADID_RAW)=lower(NGADID_RAW) \
                and (frompage_raw is not null and frompage_raw <> \'/\') \
                group by minisite_raw, flightid' % (site_common_table_name, startdate, event_impression)
    
    sitetime_sql = 'select minisite_raw as minisite, flightid, sum(VIEWTIME_RAW*EVENTCOUNT) as sitetime, sum(EVENTCOUNT) as persons \
                from %s where startdate =to_date(\'%s\',\'YYYY-MM-DD\') \
                and eventtype=%s and minisite_raw is not null \
                and upper(NGADID_RAW)=lower(NGADID_RAW) \
                group by minisite_raw, flightid' % (site_common_table_name, startdate, event_sitetime)
                
    sitetime_pickle_sql = 'select minisite_raw as minisite, flightid,timeid, viewtime_raw, sum(EVENTCOUNT) as persons \
                from %s where startdate =to_date(\'%s\',\'YYYY-MM-DD\') \
                and eventtype=%s and minisite_raw is not null \
                and upper(NGADID_RAW)=lower(NGADID_RAW) \
                group by minisite_raw, flightid, timeid, viewtime_raw' % (site_common_table_name, startdate, event_sitetime)
                
    siteuv_sql = 'select minisite_raw as minisite, flightid, count(distinct NGUSERID_RAW) \
                from %s where startdate =to_date(\'%s\',\'YYYY-MM-DD\') \
                and eventtype=%s and NGUSERID_RAW is not null \
                and MINISITE_RAW is not null \
                group by minisite_raw, flightid' % (site_uv_table_name, startdate, event_impression)
    
    try:
        cursor.execute(impression_sql)
        impressions_results = cursor.fetchall()
        
        cursor.execute(sitetime_sql)
        sitetime_results = cursor.fetchall()
        
        cursor.execute(siteuv_sql)
        siteuv_results = cursor.fetchall()
        
        cursor.execute(landing_sql)
        langding_results = cursor.fetchall()
        
        cursor.execute(bounce_sql)
        bounce_results = cursor.fetchall()
        
        cursor.execute(sitetime_pickle_sql)
        pickle_results = cursor.fetchall()

    except pyodbc.Error,e:
        print e
        return None
    
    print "start dumping impression..."
    for ir in impressions_results:
        minisite = ir[0]
        de_flight_id = ir[1]
        impression = ir[2]
        total_pages = ir[3]
        average_pages = "%.2f" % (total_pages*1.0/impression)
        
        # change here !
        #f = Flight.objects.get(DE_flight_id=de_flight_id)
        f = Flight.objects.get(DE_flight_id=45657)
        
        ub, created = UserBehaviour.objects.get_or_create(minisite=minisite, DE_flight_id=int(de_flight_id), startdate=startdate, flight=f, impression=impression, average_pages=average_pages)
    
    #bounce_dict = {}
    #for lr in langding_results:
    #    minisite = lr[0]
    #    de_flight_id = lr[1]
    #    frompages = lr[2]
    #    key = minisite + '-%s' % de_flight_id
    #    print key
    #    bounce_dict[key] = frompages
    
    #for br in bounce_results:
    #    minisite = br[0]
    #    de_flight_id = br[1]
    #    frompages = br[2]
    #    key = minisite + '%s' % de_flight_id
    #    index = bounce_dict[key]
    #    bounce_rate = (index - frompages)*1.0/index
    #    ub = UserBehaviour.objects.get(minisite=minisite, DE_flight_id=de_flight_id,startdate=startdate)
    #    ub.bounce_rate = bounce_rate
    #   ub.save()
    
    print "start dumping sitetime..."
    for sr in sitetime_results:
        minisite = sr[0]
        de_flight_id = sr[1]
        sitetime = sr[2]
        person = sr[3]
        ub = UserBehaviour.objects.get(minisite=minisite, DE_flight_id=de_flight_id,startdate=startdate)
        ub.sitetime = "%.2f" % (sitetime*1.0/person)
        ub.save()
    
    print "start dumping siteuv..."
    for uv in siteuv_results:
        minisite = uv[0]
        de_flight_id = uv[1]
        siteuv = uv[2]
        
        ub = UserBehaviour.objects.get(minisite=minisite, DE_flight_id= de_flight_id,startdate=startdate)
        ub.siteuv = siteuv
        ub.save()
        
    p_dict = {}
    for p in pickle_results:
        minisite = p[0]
        de_flight_id = p[1]
        timeid = str(p[2])
        viewtime = int(p[3])
        person = int(p[4])
        
        key = minisite + '|%s' % de_flight_id
        
        if key not in p_dict:
            p_dict[key] = {}
        
        if timeid not in p_dict[key]:
            p_dict[key][timeid] = {}
        
        p_dict[key][timeid].update({viewtime:person})
        
        
    for k in p_dict:
        minisite, de_flight_id = k.split('|')
        pickle_string = pickle.dumps(p_dict[k])
        ub = UserBehaviour.objects.get(minisite=minisite, DE_flight_id= de_flight_id,startdate=startdate)
        ub.viewtime_dic = pickle_string
        ub.save()
    
    ############### unpickle example ##################
    ub = UserBehaviour.objects.get(minisite='www.canon.com.cn', DE_flight_id= 43438,startdate='2009-11-24')
    unpickle =  pickle.loads(str(ub.viewtime_dic))