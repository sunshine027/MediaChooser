#coding=utf-8

import datetime, os, codecs
from ftplib import FTP

from django.core.management.base import BaseCommand
from django.db import connection

from MediaChooser.media_planning.models import Flight, DE_ClickData
from MediaChooser.ad.models import Ad

class Command(BaseCommand):
    def handle(self, *args, **options):
        pass

#host = "211.94.190.88"
#username = "andc-it"
#password = "it@andc"


today = datetime.date.today()
#yesterday = today - datetime.timedelta(days=1)
yesterday = datetime.date(2011,1,31)
year, month, day = str(yesterday).split('-')
new_date = '%s/%s/%s' % (month, day, year)

filepath = os.path.abspath(os.path.split(__file__)[0])

#campaign = Ad.objects.filter(create_time__year=year, create_time__month=month, create_time__day=day)
campaign = Ad.objects.filter(start_day__year=2010, start_day__month=6)
start_day = datetime.date(2011,1,1)
end_day = datetime.date(2011,1,31)

#if len(campaign) != 0:
if True:
    ids = [x.DE_campaign_id for x in campaign]
    ss = ''
    where = ''
    if len(ids) > 1:
        ss = tuple(ids)
        where = 'in %s' % str(tuple(ids)) 
    else:
        #ss = tuple(id)
        where = '= %s' % ids[0]
    filename_c = os.path.join(filepath,"lenovo%s.tab" % ''.join(str(yesterday).split('-'))) 
    filename_c_fin = os.path.join(filepath,"lenovo%s.fin" % ''.join(str(yesterday).split('-'))) 
    fd_c_fin = codecs.open(filename_c_fin,'w','utf-8') 
    fd_c_fin.close()
    fd_c = open(filename_c, 'w')
    #sql_campaign = 'select a.\"DE_ad_id\", b.name, c.c_name, d.c_name, e.adform, a.start_day, a.end_day, \
    #    a.ad_days, a.clickurl from media_planning_flight a, ad_ad b, media_media c, media_channel d, \
    #    media_mediaadinfo e where a.\"DE_campaign_id\"=b.\"DE_campaign_id\" and a.media_id=c.id and a.channel_id=d.id \
    #    and a.media_ad_info_id=e.id and b.\"DE_campaign_id\"' + where
    
    
    sql_campaign = "SELECT a.\"DE_ad_id\", b.name, c.c_name, d.c_name, e.adform, a.start_day, a.end_day, \
        a.ad_days, a.clickurl, e.adsize_detail,a.unit_price * a.discount FROM media_planning_flight a, ad_ad b, media_media c, media_channel d, \
        media_mediaadinfo e where a.\"DE_campaign_id\"=b.\"DE_campaign_id\" and a.media_id=c.id and a.channel_id=d.id \
        and a.media_ad_info_id= e.id AND b.client_id = 1 \
        AND ( (a.start_day >= \'%s\' and a.start_day <= \'%s\') or (a.end_day >= \'%s\' and a.end_day <= \'%s\') or (a.start_day <= \'%s\' and a.end_day >= \'%s\') )" % (start_day,end_day,start_day,end_day,start_day,end_day)
    """
    sql_campaign = "SELECT a.\"DE_ad_id\", b.name, c.c_name, d.c_name, e.adform, a.start_day, a.end_day, \
        a.ad_days, a.clickurl, e.adsize_detail,a.unit_price * a.discount FROM media_planning_flight a, ad_ad b, media_media c, media_channel d, \
        media_mediaadinfo e where a.\"DE_campaign_id\"=b.\"DE_campaign_id\" and a.media_id=c.id and a.channel_id=d.id \
        and a.media_ad_info_id= e.id AND b.client_id = 1 and a.\"DE_campaign_id\" = 2620"
   """ 
    cursor1 = connection.cursor()
    cursor1.execute(sql_campaign)
    rows = cursor1.fetchall()
    
    # 2730 2676 2683
    
    write_buffer = u"## SC\tSiteCatalyst SAINT Import File\tv:2.0\n## SC\t'## SC' indicates a SiteCatalyst pre-process header. Please do not remove these lines.\n## SC\tD:2009-12-28 00:00:09\tA:63978:53\nkey\tAdName\tCampaigns\tCampaigns^~period~\tMediaChannel\tMedia\tAd Form\tPrice\tPlacement Start Date\tPlacement End Date\tPlacement Total Booked Units\tContent Category\tAd Status\tClick-through URL\n"
    for r in rows:
        media_name = u'%s' % r[2]
        channel_name = u'%s>%s' % (r[2],r[3])#.decode('gbk').encode('utf-8')
        campaign_name = u'%s' % r[1]#.decode('gbk').encode('utf-8')
        ad_name = u'%s>%s>%s' % (r[2],r[3],r[4])#.decode('gbk').encode('utf-8'))
        ad_size = u'%s' % r[9]
        ad_price = u'%s' % r[10]
        idsss = u'%s' % str(r[0])
        ad_status = 'inactive'
        if r[6] >= datetime.date(int(year), int(month), int(day)) and r[5] <= datetime.date(int(year), int(month), int(day)):
            ad_status = 'active'
        
        click_through = r[8]
        if click_through is None:
            click_through = ''
        write_buffer += idsss + u'\t' + ad_name + u'\t' + campaign_name + u'\t\t' + channel_name + u'\t' + media_name + u'\t' + ad_size + u'\t' + ad_price + u'\t' + u'%s' % str(r[5]) + '\t' + str(r[6]) + '\t' + '%s' % r[7] + '\t' + 'banner' + u'\t' + ad_status + u'\t'+ click_through +u'\n'

    fd_c.write(write_buffer.encode('utf-16'))
    #fd_c.write(write_buffer.decode('gbk').encode('utf-8'))
    fd_c.close()
    cursor1.close()
    ''' 
    host = 'ftp2.omniture.com'
    username = "lenovochina-prd_7740778"
    password = "L.Q6RZcK"

    remotepath = '/'
    
    f1 = FTP(host)
    f1.login(username, password)
    f1.cwd(remotepath)
    
    fd_ftp1 = open(filename_c, 'rb')
    f1.storbinary('STOR %s' % os.path.basename(filename_c),fd_ftp1)
    fd_ftp1.close()

    fd_fin = open(filename_c_fin, 'rb')
    f1.storbinary('STOR %s' % os.path.basename(filename_c_fin),fd_fin)
    fd_fin.close()
    f1.quit()
    #os.remove(filename_c_fin)
    #os.remove(filename_c)
    ''' 

