#coding=utf-8

import datetime, os
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
yesterday = today - datetime.timedelta(days=1)
#yesterday = datetime.date(2010,12,02)
year, month, day = str(yesterday).split('-')
new_date = '%s/%s/%s' % (month, day, year)

cursor = connection.cursor()
sql = "SELECT a.date, a.eventcount, b.\"DE_ad_id\" \
FROM media_planning_de_clickdata a, media_planning_flight b, ad_ad c \
WHERE a.ad_id=c.id and a.flight_id=b.id and a.eventtype=4 and c.client_id=1 \
and a.date='%s' " % yesterday
cursor.execute(sql)
rows = cursor.fetchall()

filepath = os.path.abspath(os.path.split(__file__)[0])

filename = os.path.join(filepath, "lenovo%s.txt" % ''.join(str(yesterday).split('-')))
filename_fin = os.path.join(filepath, "lenovo%s.fin" % ''.join(str(yesterday).split('-')))

fd = open(filename,'w')

write_buffer = u"# Generic Ad Server template file (user: 63978 ds_id: 2) \n\
#       Tracking Code \n\
Date\tTracking Code\tEvent 21\n"

for r in rows:
    write_buffer += new_date + '\t' + '%s'%r[2] + '\t' + '%s'%r[1] + '\n'

fd.write(write_buffer)

fd.close()

fd1 = open(filename_fin,'w')
fd1.close()
cursor.close()

campaign = Ad.objects.filter(create_time__year=year, create_time__month=month, create_time__day=day)

if len(campaign) != 0:
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
    fd_c_fin = open(filename_c_fin,'w') 
    fd_c_fin.close()
    fd_c = open(filename_c, 'w')
    sql_campaign = 'select a.\"DE_ad_id\", b.name, c.c_name, d.c_name, e.adform from media_planning_flight a, ad_ad b, media_media c, media_channel d, media_mediaadinfo e where a.\"DE_campaign_id\"=b.\"DE_campaign_id\" and a.media_id=c.id and a.channel_id=d.id and a.media_ad_info_id=e.id and b.\"DE_campaign_id\"' + where 
    cursor1 = connection.cursor()
    cursor1.execute(sql_campaign)
    rows = cursor1.fetchall()
    
    write_buffer = u"## SC\tSiteCatalyst SAINT Import File\tv:2.0\n## SC\t'## SC' indicates a SiteCatalyst pre-process header. Please do not remove these lines.\n## SC\tD:2009-12-28 00:00:09\tA:63978:53\nkey\t广告名称\tCampaigns\tCampaigns^~period~\t频道\t媒体\n"
    for r in rows:
        media_name = r[2]
        channel_name = u'%s>%s' % (r[2],r[3])#.decode('gbk').encode('utf-8')
        campaign_name = r[1]#.decode('gbk').encode('utf-8')
        ad_name = u'%s>%s>%s' % (r[2],r[3],r[4])#.decode('gbk').encode('utf-8'))
        idsss = str(r[0])
        write_buffer += idsss + '\t' + ad_name + '\t' + campaign_name + '\t\t' + channel_name + '\t' + media_name + '\n'

    fd_c.write(write_buffer.encode('utf-16'))
    fd_c.close()
    cursor1.close()
    
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

    
########## upload to ftp ##########
host = "ftp2.omniture.com"
username = "lenovochina-prd_1578444"
password = "HABLcX8d"

remotepath = '/'

f = FTP(host)
f.login(username, password)
f.cwd(remotepath)
fd_ftp = open(filename, 'rb')
f.storbinary('STOR %s' % os.path.basename(filename),fd_ftp)
fd_ftp.close()

fd_fin = open(filename, 'rb')
f.storbinary('STOR %s' % os.path.basename(filename_fin),fd_fin)
fd_fin.close()

f.quit()
#os.remove(filename_fin)
#os.remove(filename)
