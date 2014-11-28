# Create your views here.
#coding=utf-8

from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import HttpResponse
from django.core.urlresolvers import reverse
from django.template import RequestContext
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.utils.encoding import smart_str, smart_unicode
from django.db import connection

from MediaChooser.pr.models import MediaResource, Reporter, BlogOwner, Moderator, OtherHumanResource, CooperateCorperationResource
from MediaChooser.pr.forms import MediaResourceForm, BlogOwnerForm, ModeratorForm, CooperateCorperationResourceForm, OtherHumanResourceForm, ReporterForm

import xlrd
import re
import datetime
import logging
email_re = re.compile(r'[0-9a-z][_.0-9a-z-]{0,31}@([0-9a-z][0-9a-z-]{0,30}[0-9a-z]\.){1,4}[a-z]{2,4}')
RECENTLY_UPDATE_INTERVAL = 14
#LOG_FILENAME = 'log/test.log'
#logging.basicConfig(filename=LOG_FILENAME,level=logging.DEBUG)
#将excel中的日期(实际拿到的是一个float型的浮点数)转化成python可用的日期
_s_date = datetime.date(1899, 12, 31).toordinal() -1
def getdate(date):
    if isinstance(date, float):
        date = int(date)
    d = datetime.date.fromordinal(_s_date + date)
    return d.strftime("%Y-%m-%d")

#将excel(linux下openoffice中的纯数字超过一定位数就变成浮点数了)中的数字型浮点数还原为整数，再转化成字符串
def get_str(float_number):
    if isinstance(float_number, float):
        float_number = int(float_number)
    return smart_unicode(float_number)

def get_update_day():
    compare_datetime = datetime.datetime.now() - datetime.timedelta(days=RECENTLY_UPDATE_INTERVAL)
    return compare_datetime
#decorater:判断某个登录者是不是属于pr组
def is_pr(fun):
    
    def new_fun(*args, **kargs):
        flag = False
        for group in args[0].user.groups.all():
            if group.name == 'pr':
                flag = True
        if flag:
            return fun(*args, **kargs)
        else:
            message = u'对不起，您没有权限访问关于PR的任何资源'
            return render_to_response('pr/message.html', locals(), context_instance=RequestContext(args[0]))
    return new_fun


def list_whole_media_resource(request):
    print 'hello'
    is_unfold = True
    count = MediaResource.objects.filter(deleted=False).count()
    media_resource_by_province_list = {}
    media_resource_by_first_category_list = {}
    media_resource_by_media_level_list = {}
    cursor = connection.cursor()
    
    cursor.execute('select trim(province), count(trim(province)) as count from pr_mediaresource where deleted=False group by trim(province)')
    results = cursor.fetchall()
    for result in results:
        media_resource_by_province_list[result[0]] = result[1]
    
    cursor.execute('select trim(first_category), count(trim(first_category)) as count from pr_mediaresource where deleted=False group by trim(first_category)')
    results = cursor.fetchall()
    for result in results:
        media_resource_by_first_category_list[result[0]] = result[1]
    
    cursor.execute('select trim(media_level), count(trim(media_level)) as count from pr_mediaresource where deleted=False group by trim(media_level)')
    results = cursor.fetchall()
    for result in results:
        media_resource_by_media_level_list[result[0]] = result[1]
        
    compare_datetime = get_update_day()
    updatecount = MediaResource.objects.filter(last_modified__gt = compare_datetime, deleted=False).count()
    return render_to_response('pr/list_whole_media_resource.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required
def list_update_media_resource(request):
    is_unfold = True
    compare_datetime = get_update_day()
    media_resource_list = MediaResource.objects.filter(last_modified__gt = compare_datetime, deleted=False)
    return render_to_response('pr/list_media_resource.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required
def list_search_media_resource(request):
    is_unfold = True
    type = request.POST['searchtype']
    val = request.POST['searchval']
    if type == 'province':
        media_resource_list = MediaResource.objects.filter(province=val, deleted=False)
    elif type == 'first_category':
        media_resource_list = MediaResource.objects.filter(first_category=val, deleted=False)
    elif type == 'media_level':
        media_resource_list = MediaResource.objects.filter(media_level=val, deleted=False)
    return render_to_response('pr/list_media_resource.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required
def add_media_resource(request):
    is_unfold = True
    if request.method == 'POST':
        media_resource_form = MediaResourceForm(request.POST)
        if media_resource_form.is_valid():
            MediaResource.objects.create(province=media_resource_form.cleaned_data['province'],
                                         city=media_resource_form.cleaned_data['city'],
                                         media_name=media_resource_form.cleaned_data['media_name'],
                                         media_type=media_resource_form.cleaned_data['media_type'],
                                         first_category=media_resource_form.cleaned_data['first_category'],
                                         second_category=media_resource_form.cleaned_data['second_category'],
                                         media_level=media_resource_form.cleaned_data['media_level'],
                                         url=media_resource_form.cleaned_data['url'],
                                         ranking=media_resource_form.cleaned_data['ranking'],
                                         visits=media_resource_form.cleaned_data['visits'],
                                         domain_company=media_resource_form.cleaned_data['domain_company'],
                                         office_address=media_resource_form.cleaned_data['office_address'],
                                         media_location=media_resource_form.cleaned_data['media_location'],
                                         page_compose_feature=media_resource_form.cleaned_data['page_compose_feature'],
                                         accepter_compose=media_resource_form.cleaned_data['accepter_compose'],
                                         accepter_age_bracket=media_resource_form.cleaned_data['accepter_age_bracket'],
                                         accepter_hobbies=media_resource_form.cleaned_data['accepter_hobbies'],
                                         accepter_value_orientation=media_resource_form.cleaned_data['accepter_value_orientation'],
                                         accepter_proportion=media_resource_form.cleaned_data['accepter_proportion'],
                                         found_day=media_resource_form.cleaned_data['found_day'],
                                         pr_contribution_require=media_resource_form.cleaned_data['pr_contribution_require'],
                                         website_management=media_resource_form.cleaned_data['website_management'],
                                         rollout_flow = media_resource_form.cleaned_data['rollout_flow'],
                                         introduction=media_resource_form.cleaned_data['introduction'],
                                         remark=media_resource_form.cleaned_data['remark']
                                         )
            return redirect(reverse('list_media_resource'))
    else:
        media_resource_form = MediaResourceForm()
    return render_to_response('pr/add_media_resource.html', locals(), context_instance=RequestContext(request))


@transaction.commit_manually
@is_pr
@login_required
def batch_add_media_resource_by_excel(request):
    file = request.FILES.get('media_resource_file', None)
    if file:
        try:
            bk = xlrd.open_workbook(file_contents=file.read())
        except Exception, e:
            return HttpResponse(u'你上传的不是.xsl结尾的excel文件，请检查后再上传')
        try:
            media_sheet = bk.sheet_by_name(u'媒体资源')
        except Exception, e:
            return HttpResponse(u'未找到命名为媒体资源的sheet')
        if media_sheet.ncols != 25:
            return HttpResponse(u'媒体资源的列数有问题，应该为25列')
        province_index=[-1, 0]
        city_index=[-1, 1]
        media_name_index=[-1, 2]
        media_type_index=[-1, 3]
        first_category_index=[-1, 4]
        second_category_index=[-1, 5]
        media_level_index=[-1, 6]
        url_index=[-1, 7]
        ranking_index=[-1, 8]
        visits_index=[-1, 9]
        domain_company_index=[-1, 10]
        office_address_index=[-1, 11]
        media_location_index=[-1, 12]
        page_compose_index=[-1, 13]
        acceptor_compose_index=[-1, 14]
        acceptor_age_index=[-1, 15]
        acceptor_hobbies_index=[-1,16]
        acceptor_value_index=[-1, 17]
        acceptor_propotion_index=[-1, 18]
        found_index=[-1, 19]
        pr_require_index=[-1, 20]
        website_management_index=[-1, 21]
        rollout_index=[-1, 22]
        introduction_index=[-1, 23]
        remark_index=[-1,24]
        try:
            for i in range(2, media_sheet.nrows):
                media_resource = MediaResource()
                media_resource.province = media_sheet.cell_value(i, province_index[1])
                media_resource.city = media_sheet.cell_value(i, city_index[1])
                media_resource.media_name = media_sheet.cell_value(i, media_name_index[1])
                media_resource.media_type = media_sheet.cell_value(i, media_type_index[1])
                media_resource.first_category = media_sheet.cell_value(i, first_category_index[1])
                media_resource.second_category = media_sheet.cell_value(i, second_category_index[1])
                media_resource.media_level = media_sheet.cell_value(i, media_level_index[1])
                media_resource.url = media_sheet.cell_value(i, url_index[1])
                media_resource.ranking = get_str(media_sheet.cell_value(i, ranking_index[1]))
                media_resource.visits = get_str(media_sheet.cell_value(i, visits_index[1]))
                media_resource.domain_company = media_sheet.cell_value(i, domain_company_index[1])
                media_resource.office_address = media_sheet.cell_value(i, office_address_index[1])
                media_resource.media_location = media_sheet.cell_value(i, media_location_index[1])
                media_resource.page_compose_feature = media_sheet.cell_value(i, page_compose_index[1])
                media_resource.accepter_compose = media_sheet.cell_value(i, acceptor_compose_index[1])
                media_resource.accepter_age_bracket = media_sheet.cell_value(i, acceptor_age_index[1])
                media_resource.accepter_hobbies = media_sheet.cell_value(i, acceptor_hobbies_index[1])
                media_resource.accepter_value_orientation = media_sheet.cell_value(i, acceptor_value_index[1])
                media_resource.accepter_proportion = media_sheet.cell_value(i, acceptor_propotion_index[1])
                found_day = media_sheet.cell_value(i, found_index[1])
                try:
                    if found_day:
                        found_day = getdate(found_day)
                    else:
                        found_day = None
                except Exception, e:
                    transaction.rollback()
                    return HttpResponse(u'第' + str(i+1) + u'行的成立日期有问题，请检查后上传')
                media_resource.found_day = found_day
                media_resource.pr_contribution_require = media_sheet.cell_value(i, pr_require_index[1])
                media_resource.website_management = media_sheet.cell_value(i, website_management_index[1])
                media_resource.rollout_flow = media_sheet.cell_value(i, rollout_index[1])
                media_resource.introduction = media_sheet.cell_value(i, introduction_index[1])
                media_resource.remark = media_sheet.cell_value(i, remark_index[1])
                media_resource.save()
        except Exception, e:
            transaction.rollback()
            return HttpResponse(u'第' + str(i+1) + u'行的数据有问题，请检查后上传')
        transaction.commit()
        return HttpResponse('succesful')
    else:
        return HttpResponse('请上传文件')

@is_pr  
@login_required    
def list_media_resource(request):
    media_resource_list = MediaResource.objects.filter(deleted=False)
    #展开二级目录
    is_unfold = True
    return render_to_response('pr/list_media_resource.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required
def edit_media_resource(request, media_resource_id):
    is_unfold = True
    media_resource = get_object_or_404(MediaResource, pk=media_resource_id)
    if request.method == 'POST':
        media_resource_form = MediaResourceForm(request.POST)
        if media_resource_form.is_valid():
            media_resource.province = media_resource_form.cleaned_data['province']
            media_resource.city = media_resource_form.cleaned_data['city']
            media_resource.media_name = media_resource_form.cleaned_data['media_name']
            media_resource.media_type = media_resource_form.cleaned_data['media_type']
            media_resource.first_category = media_resource_form.cleaned_data['first_category']
            media_resource.second_category = media_resource_form.cleaned_data['second_category']
            media_resource.media_level = media_resource_form.cleaned_data['media_level']
            media_resource.url = media_resource_form.cleaned_data['url']
            media_resource.ranking = media_resource_form.cleaned_data['ranking']
            media_resource.visits = media_resource_form.cleaned_data['visits']
            media_resource.domain_company = media_resource_form.cleaned_data['domain_company']
            media_resource.office_address = media_resource_form.cleaned_data['office_address']
            media_resource.media_location = media_resource_form.cleaned_data['media_location']
            media_resource.page_compose_feature = media_resource_form.cleaned_data['page_compose_feature']
            media_resource.accepter_compose = media_resource_form.cleaned_data['accepter_compose']
            media_resource.accepter_age_bracket = media_resource_form.cleaned_data['accepter_age_bracket']
            media_resource.accepter_hobbies = media_resource_form.cleaned_data['accepter_hobbies']
            media_resource.accepter_value_orientation = media_resource_form.cleaned_data['accepter_value_orientation']
            media_resource.accepter_proportion = media_resource_form.cleaned_data['accepter_proportion']
            media_resource.found_day = media_resource_form.cleaned_data['found_day']
            media_resource.pr_contribution_require = media_resource_form.cleaned_data['pr_contribution_require']
            media_resource.website_management = media_resource_form.cleaned_data['website_management']
            media_resource.rollout_flow = media_resource_form.cleaned_data['rollout_flow']
            media_resource.introduction = media_resource_form.cleaned_data['introduction']
            media_resource.remark = media_resource_form.cleaned_data['remark']
            media_resource.save()
            return redirect(reverse('list_media_resource'))
                                         
    else:
        media_resource = get_object_or_404(MediaResource, pk=media_resource_id)
        data = {
                'province': media_resource.province,
                'city': media_resource.city,
                'media_name': media_resource.media_name,
                'media_type': media_resource.media_type,
                'first_category': media_resource.first_category,
                'second_category': media_resource.second_category,
                'media_level': media_resource.media_level,
                'url': media_resource.url,
                'ranking': media_resource.ranking,
                'visits': media_resource.visits,
                'domain_company': media_resource.domain_company,
                'office_address': media_resource.office_address,
                 'media_location': media_resource.media_location,
                 'page_compose_feature': media_resource.page_compose_feature,
                 'accepter_compose': media_resource.accepter_compose,
                 'accepter_age_bracket': media_resource.accepter_age_bracket,
                 'accepter_hobbies': media_resource.accepter_hobbies,
                 'accepter_value_orientation': media_resource.accepter_value_orientation,
                 'accepter_proportion': media_resource.accepter_proportion,
                 'found_day': media_resource.found_day,
                 'pr_contribution_require': media_resource.pr_contribution_require,
                 'website_management': media_resource.website_management,
                 'rollout_flow': media_resource.rollout_flow,
                 'introduction': media_resource.introduction,
                 'remark': media_resource.remark
                }
        media_resource_form = MediaResourceForm(data)
    return render_to_response('pr/edit_media_resource.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required
def delete_media_resource(request, media_resource_id):
    media_resource = get_object_or_404(MediaResource, pk=media_resource_id)
    media_resource.deleted = True
    media_resource.save()
    return redirect(reverse('list_media_resource'))

@is_pr
@login_required
def list_human_resource_by_media(request):
    #展开二级目录
    is_unfold = True
    media_name = request.POST['media_name']
    reporter_count = Reporter.objects.filter(deleted=False, media_name=media_name).count()
    reporter_list = Reporter.objects.filter(deleted=False, media_name=media_name)
    blogowner_count = BlogOwner.objects.filter(deleted=False, media_name=media_name).count()
    blogowner_list = BlogOwner.objects.filter(deleted=False, media_name=media_name)
    moderator_count = Moderator.objects.filter(deleted=False, media_name=media_name).count()
    moderator_list = Moderator.objects.filter(deleted=False, media_name=media_name)
    human_resource_count = reporter_count + blogowner_count + moderator_count
    return render_to_response('pr/list_human_resource_by_media.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required
def list_search_human_resource(request):
    is_unfold = True
    type = request.POST['searchtype']
    val = request.POST['searchval']
    searchmodel = request.POST['searchmodel']
    if searchmodel == 'reporter':
        if type == 'media_property':
            reporter_list = Reporter.objects.filter(deleted=False, media_property=val)
        elif type == 'media_level':
            reporter_list = Reporter.objects.filter(deleted=False, media_level=val)
        elif type == 'industry_type':
            reporter_list = Reporter.objects.filter(deleted=False, industry_type=val)
        return render_to_response('pr/list_reporter.html', locals(), context_instance=RequestContext(request))
    elif searchmodel == 'blogowner':
        if type == 'attr':
            blog_owner_list = BlogOwner.objects.filter(deleted=False, attr=val)
        elif type == 'media_name':
            blog_owner_list = BlogOwner.objects.filter(deleted=False, media_name=val)
        return render_to_response('pr/list_blog_owner.html', locals(), context_instance=RequestContext(request))
    elif searchmodel == 'moderator':
        if type == 'industry_type':
            moderator_list = Moderator.objects.filter(deleted=False, industry_type=val)
        elif type == 'bbs_type':
            moderator_list = Moderator.objects.filter(deleted=False, bbs_type=val)
        return render_to_response('pr/list_moderator.html', locals(), context_instance=RequestContext(request))

@login_required
def list_whole_human_resource(request):
    is_unfold = True
    reporter_count = Reporter.objects.filter(deleted=False).count()
    blogowner_count = BlogOwner.objects.filter(deleted=False).count()
    moderator_count = Moderator.objects.filter(deleted=False).count()
    other_resource_count = OtherHumanResource.objects.filter(deleted=False).count()
    human_resource_count = reporter_count + blogowner_count + moderator_count + other_resource_count
    compare_datetime = get_update_day()
    update_reporter_count = Reporter.objects.filter(last_modified__gt = compare_datetime, deleted=False).count()
    update_blogowner_count = BlogOwner.objects.filter(last_modified__gt = compare_datetime, deleted=False).count()
    update_moderator_count = Moderator.objects.filter(last_modified__gt = compare_datetime, deleted=False).count()
    update_other_resource_count = OtherHumanResource.objects.filter(last_modified__gt = compare_datetime, deleted=False).count()
    cursor = connection.cursor()
    reporter_by_media_property_list = {}
    reporter_by_media_level_list = {}
    reporter_by_industry_type_list = {}
    cursor.execute('select trim(media_property), count(trim(media_property)) as count from pr_reporter where deleted=False group by  trim(media_property)')
    results = cursor.fetchall()
    for result in results:
        reporter_by_media_property_list[result[0]] = result[1]
    cursor.execute('select trim(media_level), count(trim(media_level)) as count from pr_reporter where deleted=False group by trim(media_level)')
    results = cursor.fetchall()
    for result in results:
        reporter_by_media_level_list[result[0]] = result[1]
    cursor.execute('select trim(industry_type), count(trim(industry_type)) as count from pr_reporter where deleted=False group by trim(industry_type)')
    results = cursor.fetchall()
    for result in results:
        reporter_by_industry_type_list[result[0]] = result[1]
    
    blogowner_by_attr_list = {}  
    blogowner_by_media_name_list = {}
    cursor.execute('select trim(attr), count(trim(attr)) as count from pr_blogowner where deleted=False group by trim(attr)')
    results = cursor.fetchall()
    for result in results:
        blogowner_by_attr_list[result[0]] = result[1]
    cursor.execute('select trim(media_name), count(trim(media_name)) as count from pr_blogowner where deleted=False group by trim(media_name)')
    results = cursor.fetchall()
    for result in results:
        blogowner_by_media_name_list[result[0]] = result[1]
        
     
    moderator_by_industry_type_list = {}  
    moderator_by_bbs_type_list = {}
    cursor.execute('select trim(industry_type), count(trim(industry_type)) as count from pr_moderator where deleted=False group by trim(industry_type)')
    results = cursor.fetchall()
    for result in results:
        moderator_by_industry_type_list[result[0]] = result[1]
    cursor.execute('select trim(bbs_type), count(trim(bbs_type)) as count from pr_moderator where deleted=False group by trim(bbs_type)')
    results = cursor.fetchall()
    for result in results:
        moderator_by_bbs_type_list[result[0]] = result[1]
    
    return render_to_response('pr/list_whole_human_resource.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required
def add_reporter(request):
    is_unfold = True
    if request.method == 'POST':
        reporter_form = ReporterForm(request.POST)
        if reporter_form.is_valid():
            Reporter.objects.create(province=reporter_form.cleaned_data['province'],
                                     city=reporter_form.cleaned_data['city'],
                                     media_name=reporter_form.cleaned_data['media_name'],
                                     media_type=reporter_form.cleaned_data['media_type'],
                                     media_property=reporter_form.cleaned_data['media_property'],
                                     channel=reporter_form.cleaned_data['channel'],
                                     name=reporter_form.cleaned_data['name'],
                                     gender=reporter_form.cleaned_data['gender'],
                                     position=reporter_form.cleaned_data['position'],
                                     industry_type=reporter_form.cleaned_data['industry_type'],
                                     new_or_old=reporter_form.cleaned_data['new_or_old'],
                                     proper_work=reporter_form.cleaned_data['proper_work'],
                                     other_proper=reporter_form.cleaned_data['other_proper'],
                                     media_level=reporter_form.cleaned_data['media_level'],
                                     fixed_number=reporter_form.cleaned_data['fixed_number'],
                                     fax=reporter_form.cleaned_data['fax'],
                                     mobile_number=reporter_form.cleaned_data['mobile_number'],
                                     email=reporter_form.cleaned_data['email'],
                                     company_address=reporter_form.cleaned_data['company_address'],
                                     home_address=reporter_form.cleaned_data['home_address'],
                                     msn=reporter_form.cleaned_data['msn'],
                                     qq=reporter_form.cleaned_data['qq'],
                                     zip_code=reporter_form.cleaned_data['zip_code'],
                                     id_number=reporter_form.cleaned_data['id_number'],
                                     birthday=reporter_form.cleaned_data['birthday'],
                                     car_carry_circle=reporter_form.cleaned_data['car_carry_circle'],
                                     graduate_school=reporter_form.cleaned_data['graduate_school'],
                                     education=reporter_form.cleaned_data['education'],
                                     style=reporter_form.cleaned_data['style'],
                                     hobbies=reporter_form.cleaned_data['hobbies'],
                                     work_experience=reporter_form.cleaned_data['work_experience'],
                                     last_work_time=reporter_form.cleaned_data['last_work_time'],
                                     best_communicate_time=reporter_form.cleaned_data['best_communicate_time'],
                                     require_to_pr_company=reporter_form.cleaned_data['require_to_pr_company'],
                                     honor=reporter_form.cleaned_data['honor'],
                                     other_info=reporter_form.cleaned_data['other_info'],
                                    )
            return redirect(reverse('list_reporter'))
    else:
        reporter_form = ReporterForm()
    return render_to_response('pr/add_reporter.html', locals(), context_instance=RequestContext(request))


@transaction.commit_manually
@is_pr
@login_required 
def batch_add_reporter_by_excel(request):
    file = request.FILES.get('reporter_file', None)
    if file:
        try:
            bk = xlrd.open_workbook(file_contents=file.read())
        except Exception, e:
            return HttpResponse(u'你上传的不是.xsl结尾的excel文件，请检查后再上传')
        try:
            media_sheet = bk.sheet_by_name(u'记者资源')
        except Exception, e:
            return HttpResponse(u'未找到命名为记者资源的sheet')
        if media_sheet.ncols != 36:
            return HttpResponse(u'记者资源的列数有问题，应该为36列')
        province_index=[-1, 0]
        city_index=[-1, 1]
        media_name_index=[-1, 2]
        media_type_index=[-1, 3]
        media_property_index=[-1, 4]
        channel_index=[-1, 5]
        media_level_index=[-1, 6]
        name_index=[-1, 7]
        gender_index=[-1, 8]
        position_index=[-1, 9]
        industry_type_index=[-1, 10]
        new_or_old_index=[-1, 11]
        proper_work_index=[-1, 12]
        other_proper_index=[-1, 13]
        fixed_number_index=[-1, 14]
        fax_index=[-1, 15]
        mobile_number_index=[-1,16]
        email_index=[-1, 17]
        company_address_index=[-1, 18]
        home_address_index=[-1, 19]
        zip_code_index=[-1, 20]
        msn_index=[-1, 21]
        qq_index=[-1, 22]
        car_carry_circle_index=[-1, 23]
        id_number_index=[-1, 24]
        birthday_index=[-1,25]
        graduate_school_index=[-1, 26]
        education_index=[-1, 27]
        style_index=[-1, 28]
        hobbies_index=[-1, 29]
        work_experience_index=[-1, 30]
        last_work_time_index=[-1, 31]
        best_communicate_time_index=[-1, 32]
        require_to_pr_company_index=[-1, 33]
        honor_index=[-1, 34]
        other_info_index=[-1, 35]
        
        try:
            for i in range(1, media_sheet.nrows):
                reporter = Reporter()
                reporter.province = media_sheet.cell_value(i, province_index[1])
                reporter.city = media_sheet.cell_value(i, city_index[1])
                reporter.media_name = media_sheet.cell_value(i, media_name_index[1])
                reporter.media_type = media_sheet.cell_value(i, media_type_index[1])
                reporter.media_property = media_sheet.cell_value(i, media_property_index[1])
                reporter.channel = media_sheet.cell_value(i, channel_index[1])
                reporter.media_level = media_sheet.cell_value(i, media_level_index[1])
                reporter.name = media_sheet.cell_value(i, name_index[1])
                reporter.gender = media_sheet.cell_value(i, gender_index[1])
                reporter.position = media_sheet.cell_value(i, position_index[1])
                reporter.industry_type = media_sheet.cell_value(i, industry_type_index[1])
                reporter.new_or_old = media_sheet.cell_value(i, new_or_old_index[1])
                reporter.proper_work = media_sheet.cell_value(i, proper_work_index[1])
                reporter.other_proper = media_sheet.cell_value(i, other_proper_index[1])
                reporter.fixed_number = get_str(media_sheet.cell_value(i, fixed_number_index[1]))
                reporter.fax = get_str(media_sheet.cell_value(i, fax_index[1]))
                mobile = get_str(media_sheet.cell_value(i, mobile_number_index[1]))
#                if mobile != '' and len(mobile) != 11:
#                    transaction.rollback()
#                    return HttpResponse(u'第' + str(i+1) + u'行的手机位数有问题，请检查后再上传')
                reporter.mobile_number = mobile
                email = media_sheet.cell_value(i, email_index[1])
#                if email != '':
#                    if not email_re.match(email):
#                        transaction.rollback()
#                        return HttpResponse(u'第' + str(i+1) + u'行的邮箱格式有问题，请检查后再上传')
                reporter.email = email
                reporter.company_address = media_sheet.cell_value(i, company_address_index[1])
                reporter.home_address = media_sheet.cell_value(i, home_address_index[1])
                msn = media_sheet.cell_value(i, msn_index[1])
#                if msn != '':
#                    if not email_re.match(msn):
#                        transaction.rollback()
#                        return HttpResponse(u'第' + str(i+1) + u'行的msn格式有问题，请检查后再上传')
                reporter.msn = msn
                reporter.qq = get_str(media_sheet.cell_value(i, qq_index[1]))
                reporter.zip_code = get_str(media_sheet.cell_value(i, zip_code_index[1]))
                id_number = get_str(media_sheet.cell_value(i, id_number_index[1]))
                if id_number != '' and len(id_number) != 18:
                    transaction.rollback()
                    return HttpResponse(u'第' + str(i+1) + u'行的身份证号位数有问题，请检查后再上传')
                reporter.id_number = id_number
                birthday = media_sheet.cell_value(i, birthday_index[1])
                try:
                    if birthday:
                        birthday = getdate(birthday)
                    else:
                        birthday = None
                except Exception, e:
                    transaction.rollback()
                    return HttpResponse(u'第' + str(i+1) + u'行的出生日期有问题，请检查后上传')
                reporter.birthday = birthday
                reporter.car_carry_circle = media_sheet.cell_value(i, car_carry_circle_index[1])
                reporter.graduate_school = media_sheet.cell_value(i, graduate_school_index[1])
                reporter.education = media_sheet.cell_value(i, education_index[1])
                reporter.style = media_sheet.cell_value(i, style_index[1])
                reporter.hobbies = media_sheet.cell_value(i, hobbies_index[1])
                reporter.work_experience = media_sheet.cell_value(i, work_experience_index[1])
                last_work_time = media_sheet.cell_value(i, last_work_time_index[1])
                try:
                    if last_work_time:
                        last_work_time = getdate(last_work_time)
                    else:
                        last_work_time = None
                except Exception, e:
                    transaction.rollback()
                    return HttpResponse(u'第' + str(i+1) + u'行的目前单位就职时间有问题，请检查后上传')
                reporter.last_work_time = last_work_time
                reporter.best_communicate_time = media_sheet.cell_value(i, best_communicate_time_index[1])
                reporter.require_to_pr_company = media_sheet.cell_value(i, require_to_pr_company_index[1])
                reporter.honor = media_sheet.cell_value(i, honor_index[1])
                reporter.other_info = media_sheet.cell_value(i, other_info_index[1])
                reporter.save()
        except Exception, e:
#            print e
            transaction.rollback()
            return HttpResponse(u'第' + str(i+1) + u'行的数据有问题，请检查后上传')
        transaction.commit()
        return HttpResponse('succesful')
    else:
        return HttpResponse(u'请上传文件')

@is_pr
@login_required
def edit_reporter(request, reporter_id):
    is_unfold = True
    reporter = get_object_or_404(Reporter, pk=reporter_id)
    if request.method == 'POST':
        reporter_form = ReporterForm(request.POST)
        if reporter_form.is_valid():
            reporter.province = reporter_form.cleaned_data['province']
            reporter.city = reporter_form.cleaned_data['city']
            reporter.media_name = reporter_form.cleaned_data['media_name']
            reporter.media_type = reporter_form.cleaned_data['media_type']
            reporter.media_property = reporter_form.cleaned_data['media_property']
            reporter.channel = reporter_form.cleaned_data['channel']
            reporter.media_level = reporter_form.cleaned_data['media_level']
            reporter.name = reporter_form.cleaned_data['name']
            reporter.gender = reporter_form.cleaned_data['gender']
            reporter.position = reporter_form.cleaned_data['position']
            reporter.industry_type = reporter_form.cleaned_data['industry_type']
            reporter.new_or_old = reporter_form.cleaned_data['new_or_old']
            reporter.proper_work = reporter_form.cleaned_data['proper_work']
            reporter.other_proper = reporter_form.cleaned_data['other_proper']
            reporter.fixed_number = reporter_form.cleaned_data['fixed_number']
            reporter.fax = reporter_form.cleaned_data['fax']
            reporter.mobile_number = reporter_form.cleaned_data['mobile_number']
            reporter.email = reporter_form.cleaned_data['email']
            reporter.msn = reporter_form.cleaned_data['msn']
            reporter.qq = reporter_form.cleaned_data['qq']
            reporter.company_address = reporter_form.cleaned_data['company_address']
            reporter.home_address = reporter_form.cleaned_data['home_address']
            reporter.zip_code = reporter_form.cleaned_data['zip_code']
            reporter.id_number = reporter_form.cleaned_data['id_number']
            reporter.birthday = reporter_form.cleaned_data['birthday']
            reporter.car_carry_circle = reporter_form.cleaned_data['car_carry_circle']
            reporter.graduate_school = reporter_form.cleaned_data['graduate_school']
            reporter.education = reporter_form.cleaned_data['education']
            reporter.style = reporter_form.cleaned_data['style']
            reporter.hobbies = reporter_form.cleaned_data['hobbies']
            reporter.work_experience = reporter_form.cleaned_data['work_experience']
            reporter.last_work_time = reporter_form.cleaned_data['last_work_time']
            reporter.best_communicate_time = reporter_form.cleaned_data['best_communicate_time']
            reporter.require_to_pr_company = reporter_form.cleaned_data['require_to_pr_company']
            reporter.honor = reporter_form.cleaned_data['honor']
            reporter.other_info = reporter_form.cleaned_data['other_info']
            reporter.save()
            return redirect(reverse('list_reporter'))
    else:
        data = {
                'province' : reporter.province,
                'city' : reporter.city,
                'media_name' : reporter.media_name,
                'media_type' : reporter.media_type,
                'media_property' : reporter.media_property,
                'channel' : reporter.channel,
                'media_level' : reporter.media_level,
                'name' : reporter.name,
                'gender' : reporter.gender,
                'position' : reporter.position,
                'industry_type' : reporter.industry_type,
                'new_or_old' : reporter.new_or_old,
                'proper_work' : reporter.proper_work,
                'other_proper' : reporter.other_proper,
                'fixed_number' : reporter.fixed_number,
                'fax' : reporter.fax,
                'mobile_number' : reporter.mobile_number,
                'email' : reporter.email,
                'msn' : reporter.msn,
                'qq' : reporter.qq,
                'company_address' : reporter.company_address,
                'home_address' : reporter.home_address,
                'zip_code' : reporter.zip_code,
                'id_number' : reporter.id_number,
                'birthday' : reporter.birthday,
                'car_carry_circle' : reporter.car_carry_circle,
                'graduate_school' : reporter.graduate_school,
                'education' : reporter.education,
                'style' : reporter.style,
                'hobbies' : reporter.hobbies,
                'work_experience' : reporter.work_experience,
                'last_work_time' : reporter.last_work_time,
                'best_communicate_time' : reporter.best_communicate_time,
                'require_to_pr_company' : reporter.require_to_pr_company,
                'honor' : reporter.honor,
                'other_info' : reporter.other_info,
                }
        reporter_form = ReporterForm(data)
    return render_to_response('pr/edit_reporter.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required    
def list_reporter(request):
    is_unfold = True
    reporter_list = Reporter.objects.filter(deleted=False)
    return render_to_response('pr/list_reporter.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required
def list_update_reporter(request):
    is_unfold = True
    compare_datetime = get_update_day()
    reporter_list = Reporter.objects.filter(last_modified__gt = compare_datetime, deleted=False)
    return render_to_response('pr/list_reporter.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required    
def delete_reporter(request, reporter_id):
    reporter = get_object_or_404(Reporter, pk=reporter_id)
    reporter.deleted = True
    reporter.save()
    return redirect(reverse('list_reporter'))

@is_pr
@login_required
def add_blog_owner(request):
    is_unfold = True
    if request.method == 'POST':
        blog_owner_form = BlogOwnerForm(request.POST)
        if blog_owner_form.is_valid():
            BlogOwner.objects.create(blog_name=blog_owner_form.cleaned_data['blog_name'],
                                     name=blog_owner_form.cleaned_data['name'],
                                     attr=blog_owner_form.cleaned_data['attr'],
                                     content_industry_type=blog_owner_form.cleaned_data['content_industry_type'],
                                     blog_flow=blog_owner_form.cleaned_data['blog_flow'],
                                     blog_link=blog_owner_form.cleaned_data['blog_link'],
                                     media_name=blog_owner_form.cleaned_data['media_name'],
                                     writing_style=blog_owner_form.cleaned_data['writing_style'],
                                     mobile=blog_owner_form.cleaned_data['mobile'],
                                     email=blog_owner_form.cleaned_data['email'],
                                     qq=blog_owner_form.cleaned_data['qq'],
                                     msn=blog_owner_form.cleaned_data['msn'],
                                     writing_time=blog_owner_form.cleaned_data['writing_time'],
                                     introduction=blog_owner_form.cleaned_data['introduction'],
                                     cooperate_evaluation=blog_owner_form.cleaned_data['cooperate_evaluation'],
                                     advantage=blog_owner_form.cleaned_data['advantage'],
                                     other_info=blog_owner_form.cleaned_data['other_info'],
                                     )
            return redirect(reverse('list_blog_owner'))
    else:
        blog_owner_form = BlogOwnerForm()
    return render_to_response('pr/add_blog_owner.html', locals(), context_instance=RequestContext(request))

@transaction.commit_manually
@is_pr
@login_required
def batch_add_blog_owner_by_excel(request):
    file = request.FILES.get('blog_owner_file', None)
    if file:
        try:
            bk = xlrd.open_workbook(file_contents=file.read())
        except Exception, e:
            return HttpResponse(u'你上传的不是.xsl结尾的excel文件，请检查后再上传')
        try:
            sheet = bk.sheet_by_name(u'博主')
        except Exception, e:
            return HttpResponse(u'未找到命名为博主的sheet')
        if sheet.ncols != 17:
            return HttpResponse(u'博主的列数有问题，应该为17列')
        blog_name_index = [-1, 0]
        name_index = [-1, 1]
        attr_index = [-1, 2]
        content_industry_type_index = [-1, 3]
        blog_flow_index = [-1, 4]
        blog_link_index = [-1, 5]
        media_name_index = [-1, 6]
        writing_style_index = [-1, 7]
        mobile_index = [-1, 8]
        email_index = [-1, 9]
        qq_index = [-1, 10]
        msn_index = [-1, 11]
        writing_time_index = [-1, 12]
        introduction_index = [-1, 13]
        cooperate_evaluation_index = [-1, 14]
        advantage_index = [-1, 15]
        other_info_index = [-1, 16]
        try:
            for i in range(1, sheet.nrows):
                blog_owner = BlogOwner()
                blog_owner.blog_name = sheet.cell_value(i, blog_name_index[1])
                blog_owner.name = sheet.cell_value(i, name_index[1])
                blog_owner.attr = sheet.cell_value(i, attr_index[1])
                blog_owner.content_industry_type = sheet.cell_value(i, content_industry_type_index[1])
                blog_owner.blog_flow = get_str(sheet.cell_value(i, blog_flow_index[1]))
                blog_owner.blog_link = sheet.cell_value(i, blog_link_index[1])
                blog_owner.media_name = sheet.cell_value(i, media_name_index[1])
                blog_owner.writing_style = sheet.cell_value(i, writing_style_index[1])
                mobile = get_str(sheet.cell_value(i, mobile_index[1]))
#                if mobile !='' and len(mobile) != 11:
#                    transaction.rollback()
#                    return HttpResponse(u'第' + str(i+1) + u'行的手机位数有问题，请检查后再上传')
                blog_owner.mobile = mobile
                email = sheet.cell_value(i, email_index[1])
#                if email != '':
#                    if not email_re.match(email):
#                        transaction.rollback()
#                        return HttpResponse(u'第' + str(i+1) + u'行的邮箱格式有问题，请检查后再上传')
                blog_owner.email = email
                blog_owner.qq = get_str(sheet.cell_value(i, qq_index[1]))
                blog_owner.msn = sheet.cell_value(i, msn_index[1])
                blog_owner.writing_time = sheet.cell_value(i, writing_time_index[1])
                blog_owner.introduction = sheet.cell_value(i, introduction_index[1])
                blog_owner.cooperate_evaluation = sheet.cell_value(i, cooperate_evaluation_index[1])
                blog_owner.advantage = sheet.cell_value(i, advantage_index[1])
                blog_owner.other_info = sheet.cell_value(i, other_info_index[1])
                blog_owner.save()
        except Exception, e:
            transaction.rollback()
            return HttpResponse(u'第' + str(i+1) + u'行的数据有问题，请检查后再上传')
        transaction.commit()
        return HttpResponse('succesful')
    else:
        return HttpResponse(u'请上传excel文件')

@is_pr
@login_required
def edit_blog_owner(request, blog_owner_id):
    is_unfold = True
    blog_owner = get_object_or_404(BlogOwner, pk=blog_owner_id)
    if request.method == 'POST':
        blog_owner_form = BlogOwnerForm(request.POST)
        if blog_owner_form.is_valid():
            blog_owner.blog_name = blog_owner_form.cleaned_data['blog_name']
            blog_owner.name = blog_owner_form.cleaned_data['name']
            blog_owner.attr = blog_owner_form.cleaned_data['attr']
            blog_owner.content_industry_type = blog_owner_form.cleaned_data['content_industry_type']
            blog_owner.blog_flow = blog_owner_form.cleaned_data['blog_flow']
            blog_owner.blog_link = blog_owner_form.cleaned_data['blog_link']
            blog_owner.media_name = blog_owner_form.cleaned_data['media_name']
            blog_owner.writing_style = blog_owner_form.cleaned_data['writing_style']
            blog_owner.mobile = blog_owner_form.cleaned_data['mobile']
            blog_owner.email = blog_owner_form.cleaned_data['email']
            blog_owner.qq = blog_owner_form.cleaned_data['qq']
            blog_owner.msn = blog_owner_form.cleaned_data['msn']
            blog_owner.writing_time = blog_owner_form.cleaned_data['writing_time']
            blog_owner.introduction = blog_owner_form.cleaned_data['introduction']
            blog_owner.cooperate_evaluation = blog_owner_form.cleaned_data['cooperate_evaluation']
            blog_owner.advantage = blog_owner_form.cleaned_data['advantage']
            blog_owner.other_info = blog_owner_form.cleaned_data['other_info']
            blog_owner.save()
            return redirect(reverse('list_blog_owner'))
    else:
        data = {
                'blog_name' : blog_owner.blog_name,
                'name' : blog_owner.name,
                'attr' : blog_owner.attr,
                'content_industry_type' : blog_owner.content_industry_type,
                'blog_flow' : blog_owner.blog_flow,
                'blog_link' : blog_owner.blog_link,
                'media_name' : blog_owner.media_name,
                'writing_style' : blog_owner.writing_style,
                'mobile': blog_owner.mobile,
                'email' : blog_owner.email,
                'qq' : blog_owner.qq,
                'msn' : blog_owner.msn,
                'writing_time' : blog_owner.writing_time,
                'introduction' : blog_owner.introduction,
                'cooperate_evaluation' : blog_owner.cooperate_evaluation,
                'advantage' : blog_owner.advantage,
                'other_info': blog_owner.other_info
                }
        blog_owner_form = BlogOwnerForm(data)
    return render_to_response('pr/edit_blog_owner.html', locals(), context_instance=RequestContext(request))
    
@is_pr
@login_required
def delete_blog_owner(request, blog_owner_id):
    blog_owner = get_object_or_404(BlogOwner, pk=blog_owner_id)
    blog_owner.deleted = True
    blog_owner.save()
    return redirect(reverse('list_blog_owner'))

@is_pr
@login_required
def list_blog_owner(request):
    is_unfold = True
    blog_owner_list = BlogOwner.objects.filter(deleted=False)
    return render_to_response('pr/list_blog_owner.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required
def list_update_blog_owner(request):
    is_unfold = True
    compare_datetime = get_update_day()
    blog_owner_list = BlogOwner.objects.filter(last_modified__gt = compare_datetime, deleted=False)
    return render_to_response('pr/list_blog_owner.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required
def add_moderator(request):
    is_unfold = True
    if request.method == 'POST':
        moderator_form = ModeratorForm(request.POST)
        if moderator_form.is_valid():
            Moderator.objects.create(industry_type=moderator_form.cleaned_data['industry_type'],
                                     bbs_type=moderator_form.cleaned_data['bbs_type'],
                                     media_name=moderator_form.cleaned_data['media_name'],
                                     channel=moderator_form.cleaned_data['channel'],
                                     bbs_block=moderator_form.cleaned_data['bbs_block'],
                                     bbs_link=moderator_form.cleaned_data['bbs_link'],
                                     alexa_ranking=moderator_form.cleaned_data['alexa_ranking'],
                                     block_advantage=moderator_form.cleaned_data['block_advantage'],
                                     moderator_id=moderator_form.cleaned_data['moderator_id'],
                                     name=moderator_form.cleaned_data['name'],
                                     mobile_number =moderator_form.cleaned_data['mobile_number'],
                                     email=moderator_form.cleaned_data['email'],
                                     qq=moderator_form.cleaned_data['qq'],
                                     msn=moderator_form.cleaned_data['msn'],
                                     cooperate_evaluation=moderator_form.cleaned_data['cooperate_evaluation'],
                                     other_info=moderator_form.cleaned_data['other_info'],
                                     )
            return redirect(reverse('list_moderator'))
    else:
        moderator_form = ModeratorForm()
    return render_to_response('pr/add_moderator.html', locals(), context_instance=RequestContext(request))

@transaction.commit_manually
@is_pr
@login_required
def batch_add_moderator_by_excel(request):
    file = request.FILES.get('moderator_file', None)
    if file:
        try:
            bk = xlrd.open_workbook(file_contents=file.read())
        except Exception, e:
            return HttpResponse(u'你上传的不是.xsl结尾的excel文件，请检查后再上传')
        try:
            sheet = bk.sheet_by_name(u'版主')
        except Exception, e:
            return HttpResponse(u'未找到命名为版主的sheet')
        if sheet.ncols != 16:
            return HttpResponse(u'版主的列数有问题，应该为16列')
        industry_type_index = [-1, 0]
        bbs_type_index = [-1, 1]
        media_name_index = [-1, 2]
        channel_index = [-1, 3]
        bbs_block_index = [-1, 4]
        bbs_link_index = [-1, 5]
        alexa_ranking_index = [-1, 6]
        block_advantage_index = [-1, 7]
        moderator_id_index = [-1, 8]
        name_index = [-1, 9]
        mobile_number_index = [-1, 10]
        email_index = [-1, 11]
        qq_index = [-1, 12]
        msn_index = [-1, 13]
        cooperate_evaluation_index = [-1, 14]
        other_info_index = [-1, 15]
        try:
            for i in range(1, sheet.nrows):
                moderator = Moderator()
                moderator.industry_type = sheet.cell_value(i, industry_type_index[1])
                moderator.bbs_type = sheet.cell_value(i, bbs_type_index[1])
                moderator.media_name = sheet.cell_value(i, media_name_index[1])
                moderator.channel = sheet.cell_value(i, channel_index[1])
                moderator.bbs_block = sheet.cell_value(i, bbs_block_index[1])
                moderator.bbs_link = sheet.cell_value(i, bbs_link_index[1])
                moderator.alexa_ranking = get_str(sheet.cell_value(i, alexa_ranking_index[1]))
                moderator.block_advantage = sheet.cell_value(i, block_advantage_index[1])
                moderator.moderator_id = get_str(sheet.cell_value(i, moderator_id_index[1]))
                moderator.name = sheet.cell_value(i, name_index[1])
                mobile = get_str(sheet.cell_value(i, mobile_number_index[1]))
#                if mobile != '' and len(mobile) != 11:
#                    transaction.rollback()
#                    return HttpResponse(u'第' + str(i+1) + u'行的手机位数有问题，请检查后再上传')
                moderator.mobile_number = mobile
                email = sheet.cell_value(i, email_index[1])
#                if email != '':
#                    if not email_re.match(email):
#                        transaction.rollback()
#                        return HttpRespnse(u'第' + str(i+1) + u'行的邮箱格式有问题，请检查后再上传')
                moderator.email = email
                moderator.qq = get_str(sheet.cell_value(i, qq_index[1]))
                moderator.msn = sheet.cell_value(i, msn_index[1])
                moderator.cooperate_evaluation = sheet.cell_value(i, cooperate_evaluation_index[1])
                moderator.other_info = sheet.cell_value(i, other_info_index[1])
                moderator.save()
        except Exception, e:
            transaction.rollback()
            return HttpResponse(u'第' + str(i+1) + u'行的数据有问题，请检查后再上传')
        transaction.commit()
        return HttpResponse('succesful')
    else:
        return HttpResponse(u'请上传excel文件')

@is_pr
@login_required
def edit_moderator(request, moderator_id):
    is_unfold = True
    moderator = get_object_or_404(Moderator, pk=moderator_id)
    if request.method == 'POST':
        moderator_form = ModeratorForm(request.POST)
        if moderator_form.is_valid():
            moderator.bbs_type = moderator_form.cleaned_data['bbs_type']
            moderator.industry_type = moderator_form.cleaned_data['industry_type']
            moderator.media_name = moderator_form.cleaned_data['media_name']
            moderator.channel = moderator_form.cleaned_data['channel']
            moderator.bbs_block = moderator_form.cleaned_data['bbs_block']
            moderator.bbs_link = moderator_form.cleaned_data['bbs_link']
            moderator.alexa_ranking = moderator_form.cleaned_data['alexa_ranking']
            moderator.block_advantage = moderator_form.cleaned_data['block_advantage']
            moderator.moderator_id = moderator_form.cleaned_data['moderator_id']
            moderator.name = moderator_form.cleaned_data['name']
            moderator.mobile_number = moderator_form.cleaned_data['mobile_number']
            moderator.email = moderator_form.cleaned_data['email']
            moderator.qq = moderator_form.cleaned_data['qq']
            moderator.msn = moderator_form.cleaned_data['msn']
            moderator.cooperate_evaluation = moderator_form.cleaned_data['cooperate_evaluation']
            moderator.other_info = moderator_form.cleaned_data['other_info']
            moderator.save()
            return redirect(reverse('list_moderator'))
    else:
        data = {
                 'bbs_type' : moderator.bbs_type,
                 'industry_type' : moderator.industry_type,
                 'media_name' : moderator.media_name,
                 'channel': moderator.channel,
                 'bbs_block' : moderator.bbs_block,
                 'bbs_link' : moderator.bbs_link,
                 'alexa_ranking' : moderator.alexa_ranking,
                 'block_advantage' : moderator.block_advantage,
                 'moderator_id' : moderator.moderator_id,
                 'name' : moderator.name,
                 'mobile_number' : moderator.mobile_number,
                 'email' : moderator.email,
                 'qq' : moderator.qq,
                 'msn' : moderator.msn,
                 'cooperate_evaluation' : moderator.cooperate_evaluation,
                 'other_info': moderator.other_info
                }
        moderator_form = ModeratorForm(data)
    return render_to_response('pr/edit_moderator.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required
def list_moderator(request):
    is_unfold = True
    moderator_list = Moderator.objects.filter(deleted=False)
    return render_to_response('pr/list_moderator.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required
def list_update_moderator(request):
    is_unfold = True
    compare_datetime = get_update_day()
    moderator_list = Moderator.objects.filter(last_modified__gt = compare_datetime, deleted=False)
    return render_to_response('pr/list_moderator.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required
def delete_moderator(request, moderator_id):
    moderator = get_object_or_404(Moderator, pk=moderator_id)
    moderator.deleted = True
    moderator.save()
    return redirect(reverse('list_moderator'))

@is_pr
@login_required
def add_cooperate_resource(request):
    is_unfold = True
    if request.method == 'POST':
        cooperate_resource_form = CooperateCorperationResourceForm(request.POST)
        if cooperate_resource_form.is_valid():
            CooperateCorperationResource.objects.create(comany_name=cooperate_resource_form.cleaned_data['comany_name'],
                                     contactor=cooperate_resource_form.cleaned_data['contactor'],
                                     fixed_number=cooperate_resource_form.cleaned_data['fixed_number'],
                                     mobile_number=cooperate_resource_form.cleaned_data['mobile_number'],
                                     email=cooperate_resource_form.cleaned_data['email'],
                                     service_area=cooperate_resource_form.cleaned_data['service_area'],
                                     charge_way=cooperate_resource_form.cleaned_data['charge_way'],
                                     month_cost_content=cooperate_resource_form.cleaned_data['month_cost_content'],
                                     company_advantage=cooperate_resource_form.cleaned_data['company_advantage'],
                                     success_case=cooperate_resource_form.cleaned_data['success_case'],
                                     company_introduction=cooperate_resource_form.cleaned_data['company_introduction'],
                                     offer_price=cooperate_resource_form.cleaned_data['offer_price'],
                                     cooperate_client=cooperate_resource_form.cleaned_data['cooperate_client'],
                                     cooperate_type=cooperate_resource_form.cleaned_data['cooperate_type'],
                                     cooperate_content=cooperate_resource_form.cleaned_data['cooperate_content'],
                                     cooperate_amount=cooperate_resource_form.cleaned_data['cooperate_amount'],
                                     finish_quality=cooperate_resource_form.cleaned_data['finish_quality'],
                                     media_score=cooperate_resource_form.cleaned_data['media_score'],
                                     other_info=cooperate_resource_form.cleaned_data['other_info']
                                     )
            return redirect(reverse('list_cooperate_resource'))
    else:
        cooperate_resource_form = CooperateCorperationResourceForm()
    return render_to_response('pr/add_cooperate_resource.html', locals(), context_instance=RequestContext(request))

@transaction.commit_manually
@is_pr
@login_required
def batch_add_cooperate_resource_by_excel(request):
    file = request.FILES.get('cooperate_resource_file', None)
    if file:
        try:
            bk = xlrd.open_workbook(file_contents=file.read())
        except Exception, e:
            return HttpResponse(u'你上传的不是.xsl结尾的excel文件，请检查后再上传')
        try:
            sheet = bk.sheet_by_name(u'外协资源')
        except Exception, e:
            return HttpResponse(u'未找到命名为外协资源的sheet')
        if sheet.ncols != 19:
            return HttpResponse(u'外协资源的列数有问题，应该为19列')
        comany_name_index = [-1, 0]
        contactor_index = [-1, 1]
        fixed_number_index = [-1, 2]
        mobile_number_index = [-1, 3]
        email_index = [-1, 4]
        service_area_index = [-1, 5]
        charge_way_index = [-1, 6]
        month_cost_content_index = [-1, 7]
        company_advantage_index = [-1, 8]
        success_case_index = [-1, 9]
        company_introduction_index = [-1, 10]
        offer_price_index = [-1, 11]
        cooperate_client_index = [-1, 12]
        cooperate_type_index = [-1, 13]
        cooperate_content_index = [-1, 14]
        cooperate_amount_index = [-1, 15]
        finish_quality_index = [-1, 16]
        media_score_index = [-1, 17]
        other_info_index = [-1, 18]
        
        try:
            for i in range(1, sheet.nrows):
                cooperate_resource = CooperateCorperationResource()
                cooperate_resource.comany_name = sheet.cell_value(i, comany_name_index[1])
                cooperate_resource.contactor = sheet.cell_value(i, contactor_index[1])
                cooperate_resource.fixed_number = sheet.cell_value(i, fixed_number_index[1])
                mobile = get_str(sheet.cell_value(i, mobile_number_index[1]))
#                if mobile != '' and len(mobile) != 11:
#                    transaction.rollback()
#                    return HttpResponse(u'第' + str(i+1) + u'行的手机位数有问题，请检查后再上传')
                cooperate_resource.mobile_number = mobile
                email = sheet.cell_value(i, email_index[1])
#                if email != '':
#                    if not email_re.match(email):
#                        transaction.rollback()
#                        return HttpResponse(u'第' + str(i+1) +u'行的邮箱格式有问题，请检查后再上传')
                cooperate_resource.email = email
                cooperate_resource.service_area = sheet.cell_value(i, service_area_index[1])
                cooperate_resource.charge_way = sheet.cell_value(i, charge_way_index[1])
                cooperate_resource.month_cost_content = sheet.cell_value(i, month_cost_content_index[1])
                cooperate_resource.company_advantage = sheet.cell_value(i, company_advantage_index[1])
                cooperate_resource.success_case = sheet.cell_value(i, success_case_index[1])
                cooperate_resource.company_introduction = sheet.cell_value(i, company_introduction_index[1])
                cooperate_resource.offer_price = sheet.cell_value(i, offer_price_index[1])
                cooperate_resource.cooperate_client = sheet.cell_value(i, cooperate_client_index[1])
                cooperate_resource.cooperate_type = sheet.cell_value(i, cooperate_type_index[1])
                cooperate_resource.cooperate_content = sheet.cell_value(i, cooperate_content_index[1])
                cooperate_resource.cooperate_amount = sheet.cell_value(i, cooperate_amount_index[1])
                cooperate_resource.finish_quality = sheet.cell_value(i, finish_quality_index[1])
                cooperate_resource.media_score = get_str(sheet.cell_value(i, media_score_index[1]))
                cooperate_resource.other_info = sheet.cell_value(i, other_info_index[1])
                cooperate_resource.save()
        except Exception, e:
            transaction.rollback()
            return HttpResponse(u'第' + str(i+1) + u'行的数据有问题，请检查后再上传')
        transaction.commit()
        return HttpResponse('succesful')
    else:
        return HttpResponse(u'请上传文件')

@is_pr
@login_required
def edit_cooperate_resource(request, cooperate_resource_id):
    is_unfold = True
    cooperate_resource = get_object_or_404(CooperateCorperationResource, pk=cooperate_resource_id)
    if request.method == 'POST':
        cooperate_resource_form = CooperateCorperationResourceForm(request.POST)
        if cooperate_resource_form.is_valid():
            cooperate_resource.comany_name = cooperate_resource_form.cleaned_data['comany_name']
            cooperate_resource.contactor = cooperate_resource_form.cleaned_data['contactor']
            cooperate_resource.fixed_number = cooperate_resource_form.cleaned_data['fixed_number']
            cooperate_resource.mobile_number = cooperate_resource_form.cleaned_data['mobile_number']
            cooperate_resource.email = cooperate_resource_form.cleaned_data['email']
            cooperate_resource.service_area = cooperate_resource_form.cleaned_data['service_area']
            cooperate_resource.charge_way = cooperate_resource_form.cleaned_data['charge_way']
            cooperate_resource.month_cost_content = cooperate_resource_form.cleaned_data['month_cost_content']
            cooperate_resource.company_advantage = cooperate_resource_form.cleaned_data['company_advantage']
            cooperate_resource.success_case = cooperate_resource_form.cleaned_data['success_case']
            cooperate_resource.company_introduction = cooperate_resource_form.cleaned_data['company_introduction']
            cooperate_resource.offer_price = cooperate_resource_form.cleaned_data['offer_price']
            cooperate_resource.cooperate_client = cooperate_resource_form.cleaned_data['cooperate_client']
            cooperate_resource.cooperate_type = cooperate_resource_form.cleaned_data['cooperate_type']
            cooperate_resource.cooperate_content = cooperate_resource_form.cleaned_data['cooperate_content']
            cooperate_resource.cooperate_amount = cooperate_resource_form.cleaned_data['cooperate_amount']
            cooperate_resource.finish_quality = cooperate_resource_form.cleaned_data['finish_quality']
            cooperate_resource.media_score = cooperate_resource_form.cleaned_data['media_score']
            cooperate_resource.other_info = cooperate_resource_form.cleaned_data['other_info']
            cooperate_resource.save()
            return redirect(reverse('list_cooperate_resource'))
    else:
        data = {
                'comany_name' : cooperate_resource.comany_name,
                'contactor' : cooperate_resource.contactor,
                'fixed_number' : cooperate_resource.fixed_number,
                'mobile_number' : cooperate_resource.mobile_number,
                'email' : cooperate_resource.email,
                'service_area' : cooperate_resource.service_area,
                'charge_way' : cooperate_resource.charge_way,
                'month_cost_content' : cooperate_resource.month_cost_content,
                'company_advantage' : cooperate_resource.company_advantage,
                'success_case' : cooperate_resource.success_case,
                'company_introduction' : cooperate_resource.company_introduction,
                'offer_price' : cooperate_resource.offer_price,
                'cooperate_client' : cooperate_resource.cooperate_client,
                'cooperate_type' : cooperate_resource.cooperate_type,
                'cooperate_content' : cooperate_resource.cooperate_content,
                'cooperate_amount' : cooperate_resource.cooperate_amount,
                'finish_quality' : cooperate_resource.finish_quality,
                'media_score' : cooperate_resource.media_score,
                'other_info': cooperate_resource.other_info
                }
        cooperate_resource_form = CooperateCorperationResourceForm(data)
    return render_to_response('pr/edit_cooperate_resource.html', locals(), context_instance=RequestContext(request))
    
@is_pr
@login_required
def delete_cooperate_resource(request, cooperate_resource_id):
    cooperate_resource = get_object_or_404(CooperateCorperationResource, pk=cooperate_resource_id)
    cooperate_resource.deleted = True
    cooperate_resource.save()
    return redirect(reverse('list_cooperate_resource'))

@is_pr
@login_required
def list_cooperate_resource(request):
    is_unfold = True
    cooperate_resource_list = CooperateCorperationResource.objects.filter(deleted=False)
    return render_to_response('pr/list_cooperate_resource.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required
def add_other_resource(request):
    is_unfold = True
    if request.method == 'POST':
        other_resource_form = OtherHumanResourceForm(request.POST)
        if other_resource_form.is_valid():
            OtherHumanResource.objects.create(attr=other_resource_form.cleaned_data['attr'],
                                     industry_type=other_resource_form.cleaned_data['industry_type'],
                                     name=other_resource_form.cleaned_data['name'],
                                     works_style=other_resource_form.cleaned_data['works_style'],
                                     city=other_resource_form.cleaned_data['city'],
                                     mobile_number=other_resource_form.cleaned_data['mobile_number'],
                                     email=other_resource_form.cleaned_data['email'],
                                     qq=other_resource_form.cleaned_data['qq'],
                                     msn=other_resource_form.cleaned_data['msn'],
                                     making_time=other_resource_form.cleaned_data['making_time'],
                                     cooperate_evaluation=other_resource_form.cleaned_data['cooperate_evaluation'],
                                     other_info=other_resource_form.cleaned_data['other_info']
                                     )
            return redirect(reverse('list_other_resource'))
    else:
        other_resource_form = OtherHumanResourceForm()
    return render_to_response('pr/add_other_resource.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required
def edit_other_resource(request, other_resource_id):
    is_unfold = True
    other_resource = get_object_or_404(OtherHumanResource, pk=other_resource_id)
    if request.method == 'POST':
        other_resource_form = OtherHumanResourceForm(request.POST)
        if other_resource_form.is_valid():
            other_resource.attr = other_resource_form.cleaned_data['attr']
            other_resource.industry_type = other_resource_form.cleaned_data['industry_type']
            other_resource.name = other_resource_form.cleaned_data['name']
            other_resource.works_style = other_resource_form.cleaned_data['works_style']
            other_resource.city = other_resource_form.cleaned_data['city']
            other_resource.mobile_number = other_resource_form.cleaned_data['mobile_number']
            other_resource.email = other_resource_form.cleaned_data['email']
            other_resource.qq = other_resource_form.cleaned_data['qq']
            other_resource.msn = other_resource_form.cleaned_data['msn']
            other_resource.making_time = other_resource_form.cleaned_data['making_time']
            other_resource.cooperate_evaluation = other_resource_form.cleaned_data['cooperate_evaluation']
            other_resource.other_info = other_resource_form.cleaned_data['other_info']
            other_resource.save()
            return redirect(reverse('list_other_resource'))
    else:
        data = {
                'attr' : other_resource.attr,
                'industry_type' : other_resource.industry_type,
                'name' : other_resource.name,
                'works_style' : other_resource.works_style,
                'city' : other_resource.city,
                'mobile_number' : other_resource.mobile_number,
                'email' : other_resource.email,
                'qq' : other_resource.qq,
                'msn' : other_resource.msn,
                'making_time' : other_resource.making_time,
                'cooperate_evaluation' : other_resource.cooperate_evaluation,
                'other_info': other_resource.other_info
                }
        other_resource_form = OtherHumanResourceForm(data)
    return render_to_response('pr/edit_other_resource.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required   
def delete_other_resource(request, other_resource_id):
    other_resource = get_object_or_404(OtherHumanResource, pk=other_resource_id)
    other_resource.deleted = True
    other_resource.save()
    return redirect(reverse('list_other_resource'))

@is_pr
@login_required 
def list_update_other_resource(request):
    is_unfold = True
    compare_datetime = get_update_day()
    other_resource_list = OtherHumanResource.objects.filter(last_modified__gt = compare_datetime, deleted=False)
    return render_to_response('pr/list_other_resource.html', locals(), context_instance=RequestContext(request))

@is_pr
@login_required
def list_other_resource(request):
    is_unfold = True
    other_resource_list = OtherHumanResource.objects.filter(deleted=False)
    return render_to_response('pr/list_other_resource.html', locals(), context_instance=RequestContext(request))