#! /usr/bin/env python
#coding=utf-8

from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.models import User, Group
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist
from MediaChooser.media_weekly_report.forms import ReportItemForm
from MediaChooser.media_weekly_report.models import ReportItem, WorkType, Project, GroupLeader
from MediaChooser.client.models import Client
from datetime import date, timedelta
import time
import simplejson as json
from pyExcelerator import *

@login_required
def reportitem(request):
    if request.method == 'POST':
        user = request.user
        item_id = request.POST.get('id', None)
        response = HttpResponse()
        
        if item_id is None or item_id == '':
            # create item
            form = ReportItemForm(request.POST)
            if form.is_valid():
                ri = form.save(commit=False)
                ri.responsible_user = user
                ri.save()
                tmp = {}
                tmp["id"] = ri.id
                tmp["start_day"] = request.POST.get("start_day")
                tmp["end_day"] = request.POST.get("end_day")
                tmp["work_type"] = ri.work_type.name
                if ri.client is None:
                    tmp["client"] = ''
                else:
                    tmp["client"] = ri.client.c_name
                if ri.project is None:
                    tmp["project"] = ''
                else:
                    tmp["project"] = ri.project.name
                tmp["work_subtype"] = ri.work_subtype.name
                tmp["desc"] = ri.desc
                tmp["duration"] = ri.duration
                tmp["revenue"] = ' ' or ( ri.project.revenue and ri.work_subtype.name=='排期下单' )
                tmp["profit"] = ' ' or ( ri.project.profit and ri.work_subtype.name=='排期下单' )
                response.write(json.dumps([0, tmp]))
                return response
            else:
                response.write(json.dumps([-1, "Invalid data."]))
                return response
        else:
            # modify item
            try:
                m_item = ReportItem.objects.get(pk=int(item_id))
            except ObjectDoesNotExist:
                response.write(json.dumps([-1, "Cant find the item, maybe has been deleted already."]))
                return response
            
            form = ReportItemForm(request.POST, instance=m_item)
            ri = form.save(commit=False)
            ri.responsible_user = user
            ri.save()
            tmp = {}
            tmp["id"] = ri.id
            tmp["start_day"] = request.POST.get("start_day")
            tmp["end_day"] = request.POST.get("end_day")
            tmp["work_type"] = ri.work_type.name
            if ri.client is None:
                tmp["client"] = ''
            else:
                tmp["client"] = ri.client.c_name
            if ri.project is None:
                tmp["project"] = ''
            else:
                tmp["project"] = ri.project.name
            tmp["work_subtype"] = ri.work_subtype.name
            tmp["desc"] = ri.desc
            tmp["duration"] = ri.duration
            tmp["revenue"] = ' ' or ( ri.project.revenue and ri.work_subtype.name=='排期下单' )
            tmp["profit"] = ' ' or ( ri.project.profit and ri.work_subtype.name=='排期下单' )
            response.write(json.dumps([1, tmp]))
            return response
        

@login_required
def create_reportitem(request):
    user = request.user
    items = ReportItem.objects.filter(responsible_user=user)
    if request.method == 'POST':
        form = ReportItemForm(request.POST)
        if form.is_valid():
            rt = form.save(commit=False)
            rt.responsible_user = user
            rt.save()
            today = date.today()
            interval = today.weekday()
            form = ReportItemForm(initial={'start_day':(today-timedelta(interval, 0, 0)).isoformat(), 'end_day':(today-timedelta(interval-6, 0, 0)).isoformat()})
            
            return render_to_response('media_weekly_report/create_reportitem.html', locals())
        else:
            return render_to_response('media_weekly_report/create_reportitem.html', locals())
    else:
        today = date.today()
        interval = today.weekday()
        form = ReportItemForm(initial={'start_day':(today-timedelta(interval, 0, 0)).isoformat(), 'end_day':(today-timedelta(interval-6, 0, 0)).isoformat()})
        
    return render_to_response('media_weekly_report/create_reportitem.html', locals())


def _get_statics(request):
    def k_to_v(k, dft):
        return request.POST.get(k, dft)

    def lst_to_date(ln):
        l = k_to_v(ln, '')
        y, m , d = l = [int (i) for i in l.split('-')]
        return date(y, m, d)

    user = request.user
        
    usr_list = [user]
    #if user was leader
    if user.id in [i.leader.id for i in GroupLeader.objects.all()]:
        groups_id = [i.group.id for i in GroupLeader.objects.filter(leader__id=user.id)]
        usr_list += reduce(lambda x, y: x + y, [list(Group.objects.get(id=i).user_set.all()) for i in groups_id])
    
    usr_list = set(usr_list)

    v_start_day     = None
    v_end_day       = None
    v_work_type     = None
    v_work_subtype  = None
    v_client        = None
    v_project       = None
    v_usr           = None
    
    try: v_start_day     = lst_to_date('start_day');
    except: pass

    try: v_end_day       = lst_to_date('end_day');
    except: pass
        
    try: v_work_type     = int(k_to_v('work_type', None));
    except: pass

    try: v_work_subtype  = int(k_to_v('work_subtype', None));
    except: pass

    try: v_client        = int(k_to_v('client', None));
    except: pass

    try: v_project       = int(k_to_v('project', None));
    except: pass

    try: v_usr           = int(k_to_v('usr', None));
    except: pass

    tl = ReportItem.objects.all()

    #if user was leader
    tl =  ReportItem.objects.filter(responsible_user__id__in = [i.id for i in usr_list])

    if v_start_day:
        tl = tl.exclude(end_day__lt = v_start_day)
        today = date.today()
        interval = today.weekday()
        form = ReportItemForm(initial={'start_day':(today-timedelta(interval, 0, 0)).isoformat(), 'end_day':(today-timedelta(interval-6, 0, 0)).isoformat()})

    if v_end_day:
        tl = tl.exclude(start_day__gt = v_end_day)

    if v_work_type:
        tl = tl.filter(work_type = v_work_type)

    if v_work_subtype:
        tl = tl.filter(work_subtype = v_work_subtype)

    if v_client:
        tl = tl.filter(client__id = v_client)

    if v_project:
        tl = tl.filter(project__id = v_project)

    if v_usr:
        tl = tl.filter(responsible_user__id = v_usr)

    return user, usr_list, tl


def _fill_static_item(report_item):
    tmp_dict = {}
    tmp_dict['start_day'] = report_item.start_day.isoformat()
    tmp_dict['end_day'] = report_item.end_day.isoformat()
    tmp_dict['work_type'] = report_item.work_type.name
    tmp_dict['work_subtype'] = report_item.work_subtype.name
    tmp_dict['duration'] = report_item.duration
    tmp_dict['usr'] = report_item.responsible_user.last_name + report_item.responsible_user.first_name
    try:    tmp_dict['client'] = report_item.client.c_name
    except: tmp_dict['client'] = ''
    try:    tmp_dict['project'] = report_item.project.name
    except: tmp_dict['project'] = ''
    try:    tmp_dict['revenue'] = report_item.project.revenue
    except: tmp_dict['revenue'] = ''
    try:    tmp_dict['profit'] = report_item.project.profit
    except: tmp_dict['profit'] = ''
    try:    tmp_dict['desc'] = report_item.desc
    except: tmp_dict['desc'] = ''

    return tmp_dict

def _dct_to_td_str(dct):
    res = '''<tr>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
<td>%s</td>
</tr> '''%(
        dct['start_day'],
        dct['end_day'],
        dct['work_type'],
        dct['client'],
        dct['usr'],
        dct['project'],
        dct['work_subtype'],
        dct['desc'],
        str(dct['duration']),
        str(dct['revenue']),
        str(dct['profit']),
    )
    
    return res

@login_required
def get_statics(request):
    user, usr_list, tl = _get_statics(request)

    if request.method == 'GET':
        #items = ReportItem.objects.filter(responsible_user=user)

        today = date.today()
        interval = today.weekday()
        form = ReportItemForm()

        return render_to_response('media_weekly_report/view_reportitems.html', locals())
    else:
        response = HttpResponse()
        resault_list = []
        for i in tl:
            tmp_dict = _fill_static_item(i)
            tmp_str  = _dct_to_td_str(tmp_dict)
            resault_list.append(tmp_str)

        st_duration = 0
        for i in tl:
            try:st_duration += i.duration
            except:pass
        
        
        tmp_objs = set()
        for i in tl:
            try:
                if int(i.project.revenue) > 0:
                    tmp_objs.add(i.project)
            except:pass
        st_revenue = sum([i.revenue for i in tmp_objs])

        tmp_objs = set()
        for i in tl:
            try:
                if int(i.project.profit) > 0:
                    tmp_objs.add(i.project)
            except:pass
        st_profit = sum([i.profit for i in tmp_objs])
            
        stat_dict = {}
        stat_dict['stat_duration']  = st_duration #耗时
        stat_dict['stat_revenue']   = st_revenue #营业额
        stat_dict['stat_profit']    = st_profit #利润
        try:
            resault_str = u'''
<table cellpadding='0' cellspacing='0' border='0' class='display' id='items_table'>
<thead>
<tr>
    <th>开始日期</th>
    <th>结束日期</th>
    <th>工作类型</th>
    <th>客户名称</th>
    <th>负责人</th>
    <th>项目名称</th>
    <th>工作类别</th>
    <th>工作描述</th>
    <th>工作时长</th>
    <th>营业额</th>
    <th>利润</th>
</tr>
</thead>
<tbody id='items_table_tbody' >
    <tr>
%s
    </tr>
</tbody>
</table>'''%(''.join(resault_list))
            response.write(json.dumps([len(resault_list), resault_str, stat_dict]))
            return response
        except Exception, e:
            response.status_code = 503
            response.write('%s'%(e.message))
            return response

@login_required
def get_statics_xls(request):
    from os import remove
    
    if request.method == 'GET':
        response = HttpResponse()
        response.status_code = 503
        return response

    try:
        user, usr_list, tl = _get_statics(request)

        xls_col_tpl_dict = [
            ('start_day',u'开始日期'), ('end_day',u'结束日期'), ('work_type',u'工作类型'), 
            ('client',u'客户名称'), ('usr',u'负责人'), ('project',u'项目名称'), 
            ('work_subtype',u'工作类别'), ('desc',u'工作描述'), ('duration',u'工作时长'), 
            ('revenue',u'营业额'), ('profit',u'利润'),
         ]

        xls_dir = '/tmp/xls_dir4mediachooser/'
        w = Workbook()
        ws = w.add_sheet(u'周报')
        tmp_fn = '%s%s'%(xls_dir, request.user.id)
        
        #write column names
        for i, j in enumerate(xls_col_tpl_dict):
            ws.write(0, i, j[1])

        #fill rows
        row_num = 1
        for cur_item in tl:
            tmp_dict = _fill_static_item(cur_item)
            for i, j in enumerate(xls_col_tpl_dict):
                if tmp_dict[j[0]]:
                    ws.write(row_num, i, tmp_dict[j[0]])
                else:
                    ws.write(row_num, i, '')
            row_num += 1

        w.save(tmp_fn)
        data = open(tmp_fn).read()
        remove(tmp_fn)

        #response = HttpResponse(data,mimetype='application/octet-stream') 
        response = HttpResponse(data,mimetype='application/msexcel') 
        response['Content-Disposition'] = 'attachment; filename=%s' % 'weekly_report.xls'
        return response
    
    except Exception, e:
        response = HttpResponse()
        response.status_code = 503
        response.write('%s'%(e.message))
        return response


def get_subtypes(request):
    if request.method == 'POST':
        try:
            parent = WorkType.objects.get(id=request.POST.get('parent_id', 1))
        except ObjectDoesNotExist:
            parent = None
        
        subtypes = [i.__dict__ for i in WorkType.objects.filter(parent=parent).order_by('name')]
        
        response = HttpResponse()
        response.write(json.dumps(subtypes))
        return response
    
# used by ajax
def get_projects(request):
    if request.method == 'POST':
        try:
            client = Client.objects.get(id=request.POST.get('client_id', 0)).order_by('c_name')
        except ObjectDoesNotExist:
            client = None
            
        projects = [i.__dict__ for i in Project.objects.filter(client=client).order_by('name')]
        
        response = HttpResponse()
        response.write(json.dumps(projects))
        return response    

# used by ajax
def create_project(request):
    if request.method == 'POST':
        client_id = request.POST.get('client_id', None)
        name = request.POST.get('name', None)
        arg = {'client_id':client_id, 'name':name}
        revenue = request.POST.get('revenue', None)
        if revenue is not None and revenue != '':
            arg['revenue'] = revenue
        profit = request.POST.get('profit', None)
        if profit is not None and profit != '':
            arg['profit'] = profit
                
        response = HttpResponse()
                
        try:
#            client = Client.objects.get(id=int(client_id))
#            arg[Client] = client
            new_proj = Project(**arg)
            new_proj.save()
                    
            response.write(json.dumps([1, [new_proj.id, new_proj.name]]))
            return response
        except:
            response.write(json.dumps([0, '创建项目失败']))
            return response


def delete_report(request):
    if request.method == 'POST':
        try:
            rpt_id = request.POST.get('report_id', -1)
            ReportItem.objects.get(id=rpt_id).delete()
            response = HttpResponse()
            return response
        except:
            response = HttpResponse()
            return response
    

def get_report(request):
    if request.method == 'POST':
        try:
            rpt_id = request.POST.get('report_id', -1)
            res_item = ReportItem.objects.get(id=rpt_id)

            res_dict = {
                'start_day':    res_item.start_day.isoformat(),
                'end_day':      res_item.end_day.isoformat(),
                'work_type':    res_item.work_type_id,
                'client':       res_item.client_id,
                'project':      res_item.project_id,
                'work_subtype': res_item.work_subtype_id,
                'desc':         res_item.desc,
                'duration':     res_item.duration,
                'id':           res_item.id,
            }

            response = HttpResponse()
            response.write(json.dumps([res_dict]))
            return response
        except Exception, e:
            response = HttpResponse()
            response.status_code = 503
            response.write('%s'%(e.message))
            return response



def modify_report(request):

    def k_to_v(k, dft):
        return request.POST.get(k, dft)

    def lst_to_date(ln):
        l = k_to_v(ln, '')
        y, m , d = l = [int (i) for i in l.split('-')]
        return date(y, m, d)
    
    def k_to_obj(k, Obj):
        return Obj.objects.get(
                    id=int(
                        k_to_v(k, -1)
                    ))

    if request.method == 'POST':
        try:
            rpt_id = request.POST.get('report_id', -1)
            rpt = ReportItem.objects.get(id=rpt_id)
            
            rpt.start_day   = lst_to_date('start_day')
            rpt.end_day     = lst_to_date('end_day') 
            
            rpt.desc        = k_to_v('desc', '')
            rpt.duration    = float(k_to_v('duration', -1))
            
            rpt.client      = k_to_obj('client', Client)
            rpt.work_type   = k_to_obj('work_type', WorkType)
            rpt.work_subtype= k_to_obj('work_subtype', WorkType)
            rpt.project     = k_to_obj('project', Project)
    
            rpt.save()

            response = HttpResponse()
            return response

        except Exception, e:
            response = HttpResponse()
            response.status_code = 503
            response.write('%s'%(e.message))
            return response
            

import charts
@login_required
def chartdemo(request):
    
    response = HttpResponse()
    response.write(charts.OFC2Demo().index())
    return response


@login_required
def ofc_response(request, type):
    dict = {'linechart':charts.LineChart('line_chart', 'linechart').index(),
        }
    response = HttpResponse()
    response.write(dict[type])
    return response

