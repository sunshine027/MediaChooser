import datetime

from django.shortcuts import render_to_response, get_object_or_404
from django.utils import simplejson
from django.http import HttpResponse

from MediaChooser.NielsenMedia.models import NielsenCategory, NielsenMedia, NielsenOverlap, NielsenTrafficData, Province
from MediaChooser.NielsenMedia.forms import NielsenRankForm, NielsenTrafficForm, NielsenOverlapForm

def rank(request, template):
    if request.method == 'POST':
        form = NielsenRankForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = NielsenRankForm()
    return render_to_response(template, locals())

def traffic(request, template):
    if request.method == 'POST':
        form = NielsenTrafficForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = NielsenTrafficForm()
    return render_to_response(template, locals())

def overlap(request, template):
    if request.method == 'POST':
        form = NielsenOverlapForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = NielsenOverlapForm()
        
    return render_to_response(template, locals())

def get_overlap_data(request):
    get = request.GET
    data = {}
    if get.has_key('base_media') and get.has_key('comp_media') and get.has_key('week'):
        base_media = get_object_or_404(NielsenMedia, pk=int(get['base_media']))
        p = Province.objects.get(e_name = 'all')
        week = get['week'] + ' 00:00:00'
        data['overlap'] = []
        for c in get['comp_media'].split(','):
            comp_media = get_object_or_404(NielsenMedia, pk=int(c))
            ntd = NielsenTrafficData.objects.get(media= comp_media, week= week, province = p)
            no = NielsenOverlap.objects.get(media_a= base_media, media_b= comp_media, week= week)
            data['overlap'].append({'c_name': comp_media.c_name, 'sample_ub': ntd.sample_ub, 'net_ub': no.net_ub, 'ub_dup': no.ub_dup, 'dup': no.dup})
        
        ntd_base = NielsenTrafficData.objects.get(media= base_media, week= week, province = p)
        data['media_c_name'] = base_media.c_name
        data['sample_ub'] = ntd_base.sample_ub
        data['sample_ub_freq'] = ntd_base.sample_ub_freq
        data['sample_ts'] = ntd_base.sample_ts
        data['sample_asd'] = ntd_base.sample_asd
        
        return HttpResponse(simplejson.dumps(data))

def get_media_options(request):
    get = request.GET
    if get.has_key('category'):
        c = get_object_or_404(NielsenCategory, pk=int(get['category']))
        media = NielsenMedia.objects.filter(main_category= c)
        data = [{'caption': m.c_name, 'value': m.id} for m in media]
        return HttpResponse(simplejson.dumps(data))
    
def chart(request):
    from MediaChooser.NielsenMedia.chart import chart
    return HttpResponse(chart.create(), mimetype="application/json")