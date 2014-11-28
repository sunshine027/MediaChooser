#! /usr/bin/env python
#coding=utf-8

import datetime

from django.http import HttpResponse
from django.shortcuts import render_to_response

def track(request):
    cid =  request.GET['cid']
    ip = request.META['REMOTE_ADDR']
    try:
        refer = request.GET['refer']
    except:
        refer = ''
    location = request.GET['location']
    #user_agent = request.GET['ua']
    db = get_db()
    logs = db.logs
    log = {'date': datetime.datetime.now(),
           'ip': ip,
           'c_id': cid,
           'refer':refer,
           'location':location
        }
    logs.insert(log)
    
    now = datetime.datetime.now()
    year, month, day, hour = now.year, now.month, now.day, now.hour
    tracking = db.tracking
    tracking.update( {'year':year, 'month':month, 'day':day, 'hour':hour,'c_id':cid}, {'$inc':{'pv': 1}}, upsert=True)
    #tracking = db.tracking
    #if db.today_logs.find({'ip':ip}).count()>0:
    #    tracking.update( $inc : {uv:0, pv: 1})
    #else
    #tracking.update( $inc : {uv:1})
    
    #pass
    return HttpResponse('1',mimetype='text/plain')

def summary(request, template):
    
    db = get_db()
    #logs = db.logs.find()
    #lenovo-201003-01
    #
    count18 = db.tracking.find({'day':18,'c_id':'lenovo-201003-01'})
    count19 = db.tracking.find({'day':19,'c_id':'lenovo-201003-01'})
    count20 = db.tracking.find({'day':20,'c_id':'lenovo-201003-01'})
    count21 = db.tracking.find({'day':21,'c_id':'lenovo-201003-01'})
    count22 = db.tracking.find({'day':22,'c_id':'lenovo-201003-01'})
    count23 = db.tracking.find({'day':4,'c_id':'555'})
    sum = 0
    #for c in count:
    #    sum = sum + c['pv']
    #today = datetime.datetime.today()
    #yy = today - datetime.timedelta(days=2)
    #y = today - datetime.timedelta(days=1)
    #today_count = db.logs.find({"date":{"$lt":y}}).count()
    #count_ip = len(logs.distinct('ip'))
    return render_to_response(template,locals())
    

def test(request, template):
    
    return render_to_response(template)

def get_db():
    from pymongo import Connection
    db_host = '211.94.190.82'
    db_host_port = 27017
    conn = Connection(db_host, db_host_port)
    db = conn.andc_tracking
    return db
    
