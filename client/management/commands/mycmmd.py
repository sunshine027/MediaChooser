#encoding=utf8

import os,sys 
import datetime,time

sys.path.append(r'/usr/home/hekun/')
os.environ['DJANGO_SETTINGS_MODULE']= "MediaChooser.settings"
from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404

from MediaChooser.ad.models import  Ad
from MediaChooser.media_planning.models import DE_ClickData,Flight
from dumpDE import get_from_ng_sum_fixed_click as get_fixed_click


class Command(BaseCommand):
	pass


	def handle(self, *args, **options):
		pass

def html(msg):
	if msg:
		msg = msg
	else:
		msg = '数据库内发现没有录入新信息'
	message = '''<div style='border:1px solid #ccc'><span style='color: rgb(28, 93, 161);font-size:30px;'>邮件提示</span>
         <div style='padding:20px; font-size:14px; color: rgb(32, 0, 0);font-family: Verdana; background-color: rgb(222, 232, 243);'>
         %s</div></div>''' %(msg)

	return message



__ad_obj = []
__flight_obj = []
__flight_obj_click = []
de_flight_id = []


def email_flag(mt,tmp):
	if tmp == 1:
		__ad_obj.append(mt)
	elif tmp == 2:
		__flight_obj.append(mt)
	elif tmp == 3:
		__flight_obj_click.append(mt)
	elif tmp == 4:
		de_flight_id.append(mt)




def send_email(mt):
	try:
		import smtplib,mimetypes
		from email import Encoders
		from email.MIMEBase import MIMEBase
		from email.MIMEText import MIMEText
		from email.MIMEMultipart import MIMEMultipart
		import zipfile
		email_list  = ['hekun06@gmail.com','haur09@hotmail.com','ludanfeng@and-c.com']
		for email in email_list:
			accept = email
			msg = MIMEMultipart()
			msg['Subject'] = '[ MediaChooser 邮件 ]'
			msg['From'] = 'mail.and-c.com'
			msg['To'] = accept
			if mt:
				x = html(mt)
			else:
				x = html()
			txt = MIMEText(x,'html','utf-8')
			msg.attach(txt)
			s = smtplib.SMTP('mail.and-c.com')#smtp.163.com
			s.login('hekun','hekun_123abc')
			s.sendmail('hekun@and-c.com',accept,msg.as_string())
			s.close()
			print '----------- Email Send Succesful --------------'
	except Exception ,e:
		print 'send email exception:' + str(e)


now = datetime.datetime.now()
today = datetime.date(now.year,now.month,now.day)
tmr = today - datetime.timedelta(days=1) 

ad = Ad.objects.filter(start_day__lte = tmr , end_day__gte=tmr)

for _ad in ad:
	print  '_ad' , _ad.id

	X = Flight.objects.filter(ad=_ad,start_day__lte = tmr,end_day__gte=tmr)

	De_click_data = []
	#effect = []
	effect = False

	cpc_clicks = []
	clicks = []

	for flight_obj in X:

		de_click_data = DE_ClickData.objects.filter(ad=_ad.id,flight=flight_obj.id,date=tmr)

		print 'de_click_data',de_click_data


		if de_click_data.count() > 0:
			x,y,z = get_object_or_404(Flight,id=flight_obj.id).DE_flight_id , de_click_data[0].id , flight_obj.id
			
			ret = get_fixed_click(x,str(tmr))

			#print 'ret/////////////',ret

			
			if ret:
				_click= int(ret[0])
				print  '_click', _click
				de_flight_obj = get_object_or_404(DE_ClickData,id=y)
				de_flight_obj.eventtype= 4
				de_flight_obj.eventcount=_click
				if de_flight_obj.eventcount > 10:
					print '>10'
					#effect.append((True,z))
					effect = True
				else:
					email_flag(flight_obj.id,3)
					#send_email('de_flight_id为%s的广告位click数小于10' %(x.id))
				de_flight_obj.save()


				de_click_data = DE_ClickData.objects.filter(flight=flight_obj.id)

				eventcounts = [de.eventcount for de in de_click_data if de.eventtype ==4]


				_click = sum(eventcounts)

				#de_click_data2  = DE_ClickData.objects.filter(ad=_ad.id,flight=flight_obj.id)

				#De_click_data += de_click_data2

	#print 'De_click_data',De_click_data
				#clicks  = sum([obj.eventcount for obj in  De_click_data  if obj.eventcount > 0])
				#print 'clicks',clicks
				
	#print '[]', De_click_data 

	#for obj in X:		

				_flight_obj = Flight.objects.get(id=flight_obj.id)
				_flight_obj.click = _click

				#if effect <> [ ]:
					#if (True,obj.id) in effect:
				
					#	flight_obj.ad_days_tracked += 1
					#	flight_obj.save()
				if effect:
					_flight_obj.ad_days_tracked = len(eventcounts)
					_flight_obj.save()
					
				cpc  = ( _flight_obj.unit_price * _flight_obj.ad_days_tracked )/  _flight_obj.click
				_flight_obj.cpc = cpc
				_flight_obj.save()

		

				if  _flight_obj.cpc * _flight_obj.click > 0:
					cpc_clicks.append(_flight_obj.cpc * _flight_obj.click )
				if _flight_obj.click > 0:
					clicks.append(_flight_obj.click)


				
				print 'click-----------',_flight_obj.click,_flight_obj.cpc * _flight_obj.click
			else:
				email_flag(x,2)
				#send_email('%s :这条广告位不存在' %(flight_obj.id) )
		else:
			email_flag(flight_obj.id,4)
	else:
		email_flag(_ad.id,1)
		#send_email("id为%s的这条广告下没有数据" %(_ad.id))

	#if email_flag():
	
	try:
		print '####',sum(cpc_clicks), sum(clicks),sum(cpc_clicks) / sum(clicks)
		_ad.click  = sum(clicks)
		_ad.cpc =    sum(cpc_clicks) / sum(clicks)
		_ad.save()

	except ZeroDivisionError:
		print '.......'


x,y,z = de_flight_id,__flight_obj,__flight_obj_click 

if len(x) ==0 :
	send_email('没有监测到数据')

if y and z:
	send_email('<b>'+' <br/>'.join([ f.ad.name.encode('utf-8')+'</b>&nbsp;&nbsp;下deflightid=' + str(f.DE_flight_id) +'广告位不存在' for f in Flight.objects.filter(DE_flight_id__in=y)]) 
		   +'<br/><b>' +  ''.join([f.ad.name.encode('utf-8')+'</b>&nbsp;&nbsp;下flightid=' +  str(z) + '的广告位click数小于10' for f in Flight.objects.filter(id__in=z)]) 
		  )
__ad_obj = __flight_obj=  __flight_obj_click = de_flight_id = []

	





'''
flight =  [Flight.objects.filter(ad=_ad,start_day__lte = tmr,end_day__gte=tmr) for _ad in ad]

flight_ids = [f.id for f in flight[0] ]

print 'flight_ids',flight_ids


de_click_data = [ DE_ClickData.objects.filter(flight=flight_id) for flight_id in flight_ids]

print 'de_click_data',[de_click_obj.id for de_click_obj in  de_click_data[0]]


de_click_data = DE_ClickData.objects.filter(date=tmr)
flights = [de_c_d.flight.id  for de_c_d in de_click_data]

print 'flights',flights



try:
    de_click_data = DE_ClickData.objects.filter(date=tmr)
    flights = [de_c_d.flight.id  for de_c_d in de_click_data]
    de_flights =  [(get_object_or_404(Flight,id=f).DE_flight_id,f) for f  in flights]
    while len(de_flights)>0:
	fid = de_flights.pop()
	ret = get_fixed_click(fid[0],str(tmr)) # de_flight_id,date
	if ret <> None:
		effect = False
		_click= int(ret[0])
		print _click ,'click' 
		de_flight_obj = de_click_data.filter(flight=fid[1])[0]
		de_flight_obj.eventtype= 4
		de_flight_obj.eventcount=_click
		if de_flight_obj.eventcount > 10:	
			effect = True
		de_flight_obj.save()
		print 'de_flight_id',de_flight_obj.id
	clicks  = sum([obj.eventcount for obj in  DE_ClickData.objects.filter(flight=fid[1])])
	flight_obj = Flight.objects.get(id=fid[1])
	flight_obj.click = clicks
	if effect:
		flight_obj.da_days_tracked += 1
		flight_obj.save()
	flight_obj.cpc = ( unit_price * flight_obj.da_days_tracked )/  flight_obj.click
	flight_obj.save()
	print flight_obj.id 
    else:
	 print 'no data'
	 send_email()
except Exception, e:
    print str(e)
print 'complet'
'''