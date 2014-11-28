from django.db import models
#coding=utf-8

# Create your models here.

#province_choices = ((u'河北', u'河北'), (u'内蒙古', u'内蒙古'), (u'辽宁', u'辽宁'), (u'黑龙江', u'黑龙江')
#                    , (u'吉林', u'吉林'), (u'新疆', u'新疆'), (u'山西', u'山西'), (u'河南', u'河南')
#                    , (u'陕西', u'陕西'), (u'宁夏', u'宁夏'), (u'青海', u'青海'), (u'西藏', u'西藏')
#                    , (u'甘肃', u'甘肃'), (u'山东', u'山东'), (u'湖南', u'湖南'), (u'湖北', u'湖北')
#                    , (u'江苏', u'江苏'), (u'安徽', u'安徽'), (u'浙江', u'浙江'), (u'上海', u'上海')
#                    , (u'贵州', u'贵州'), (u'广东', u'广东'), (u'广西', u'广西'), (u'福建', u'福建')
#                    , (u'四川', u'四川'), (u'北京', u'北京'), (u'天津', u'天津'), (u'重庆', u'重庆')
#                    , (u'云南', u'云南'), (u'海南', u'海南'), (u'江西', u'江西'))

#媒体资源表
class MediaResource(models.Model):
    province = models.CharField('省份', max_length=32, help_text='省份', blank=True)
    city = models.CharField('城市', max_length=32, help_text='城市', blank=True)
    media_name = models.CharField('媒体名称', max_length=64, help_text='媒体名称', blank=True)
    media_type = models.CharField('媒体类型', max_length=64, help_text='媒体类型', blank=True)
    first_category = models.CharField('一级分类', max_length=64, help_text='媒体性质', blank=True)                     
    second_category = models.CharField('二级分类', max_length=64, help_text='频道', blank=True)
    media_level = models.CharField('媒体级别', max_length=32, help_text='媒体级别', blank=True)
    url = models.CharField('网址', max_length=128, help_text='网址', blank=True)
    ranking = models.CharField('排名', max_length=128, help_text='排名', blank=True)
    visits = models.CharField('访问量', max_length=128, help_text='访问量', blank=True)
    domain_company = models.CharField('主管单位', max_length=256, help_text='主管单位', blank=True)
    office_address = models.CharField('办公地址', max_length=256, help_text='办公地址', blank=True)
    media_location = models.CharField('媒体定位', max_length=256, help_text='媒体定位', blank=True)
    page_compose_feature = models.TextField('版面构成及特点', help_text='版面构成及特点', blank=True)
    accepter_compose = models.CharField('受众构成', max_length=256, help_text='受众构成', blank=True)
    accepter_age_bracket = models.CharField('受众年龄段', max_length=256, help_text='受众年龄段', blank=True)
    accepter_hobbies = models.TextField('受众浏览爱好', help_text='受众浏览爱好', blank=True)
    accepter_value_orientation = models.TextField('受众价值取向', help_text='受众价值取向', blank=True)
    accepter_proportion = models.CharField('受众男女比例', max_length=64, help_text='受众男女比例', blank=True)
    found_day = models.DateField('成立日期', help_text='成立日期', blank=True, null=True)
    pr_contribution_require = models.TextField('公关稿件要求', help_text='公关稿件要求', blank=True)
    website_management = models.TextField('网站管理体制', help_text='网站管理体制', blank=True)
    rollout_flow = models.TextField('上线流程', help_text='上线流程', blank=True)
    introduction = models.TextField('简介', help_text='简介', blank=True)
    remark = models.TextField('备注', help_text='备注', blank=True)
    deleted = models.BooleanField('是否删除', help_text='备注', default=False)
    last_modified = models.DateTimeField('上次修改时间', auto_now=True)
    created_time = models.DateTimeField('增加时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '媒体资源'
        verbose_name_plural = '媒体资源'
        
    def __unicode__(self):
        return self.media_name
        
        
#记者表
class Reporter(models.Model):
    province = models.CharField('省份', max_length=32, help_text='省份', blank=True)
    city = models.CharField('城市', max_length=32, help_text='城市', blank=True)
    media_name = models.CharField('媒体名称', max_length=64, help_text='媒体名称', blank=True)
    media_type = models.CharField('媒体类型', max_length=64, help_text='媒体类型', blank=True)
    media_property = models.CharField('媒体性质', max_length=64, help_text='媒体性质', blank=True)
    channel = models.CharField('频道', max_length=64, help_text='频道', blank=True)
    media_level = models.CharField('媒体级别', max_length=32, help_text='媒体级别', blank=True)
    name = models.CharField('姓名', max_length=64, help_text='姓名', blank=True)
    gender = models.CharField('性别', max_length=32, help_text='性别', blank=True)
    position = models.CharField('职务', max_length=128, help_text='职务', blank=True)
    industry_type = models.CharField('行业类型', max_length=64, help_text='行业类型', blank=True)
    new_or_old = models.CharField('是否是新记者', max_length=64, help_text='是否是新记者', blank=True)
    proper_work = models.CharField('可配合的工作', max_length=128, help_text='可配合的工作', blank=True)
    other_proper = models.CharField('其他配合', max_length=128, help_text='其他配合', blank=True)
    fixed_number = models.CharField('座机', max_length=128, help_text='座机', blank=True)
    fax = models.CharField('传真', max_length=128, help_text='传真', blank=True)
    mobile_number = models.CharField('手机', max_length=256, help_text='手机', blank=True)
    email = models.CharField('邮箱', max_length=256, help_text='邮箱', blank=True)
    company_address = models.CharField('单位地址', max_length=128, help_text='单位地址', blank=True)
    home_address = models.CharField('家庭地址', max_length=128, help_text='家庭地址', blank=True)
    zip_code = models.CharField('邮编', max_length=64, help_text='邮编', blank=True)
    msn = models.CharField('MSN', max_length=256, help_text='MSN', blank=True)
    qq = models.CharField('QQ', max_length=64, help_text='QQ', blank=True)
    car_carry_circle = models.CharField('发布频次及时间', max_length=64, help_text='汽车版刊发周期', blank=True)
    id_number = models.CharField('身份证号码', max_length=18, help_text='身份证号码', blank=True)
    birthday = models.DateField('出生日期', help_text='出生日期', blank=True, null=True)
    graduate_school = models.CharField('毕业学校', max_length=128, help_text='毕业学校', blank=True)
    education = models.CharField('学历', max_length=64, help_text='学历', blank=True)
    style = models.TextField('行文风格', help_text='行文风格', blank=True)
    hobbies = models.TextField('爱好及特长', help_text='爱好及特长', blank=True)
    work_experience = models.TextField('工作经历', help_text='工作经历', blank=True)
    last_work_time = models.DateField('目前单位就职时间', help_text='目前单位就职时间', blank=True, null=True)
    best_communicate_time = models.CharField('最佳沟通时间', help_text='最佳沟通时间', max_length=128, blank=True)
    require_to_pr_company= models.TextField('对公关公司的要求', help_text='对公关公司的要求', blank=True) 
    honor = models.TextField('个人成就及荣誉', help_text='个人成就及荣誉', blank=True) 
    other_info = models.TextField('其他', help_text='其他', blank=True)  
    deleted = models.BooleanField('是否删除', help_text='备注', default=False)   
    last_modified = models.DateTimeField('上次修改时间', auto_now=True)
    created_time = models.DateTimeField('增加时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '记者'
        verbose_name_plural = '记者'
        
    def __unicode__(self):
        return self.name
#博主表
class BlogOwner(models.Model):
    blog_name = models.CharField('博客名称', max_length=64, help_text='博客名称', blank=True)
    name = models.CharField('博主姓名', max_length=64, help_text='博主姓名', blank=True)
    attr = models.CharField('博主属性', max_length=128, help_text='博主属性', blank=True)
    content_industry_type = models.CharField('内容行业类型', max_length=64, blank=True, help_text='内容行业类型')
    blog_flow = models.CharField('博客流量', max_length=64, help_text='博客流量', blank=True)
    blog_link = models.URLField('博客链接', help_text='博客链接', blank=True, null=True)
    media_name = models.CharField('媒体名称', max_length=256, help_text='网站', blank=True)
    writing_style = models.TextField('博主写作风格', help_text='博主写作风格', blank=True)
    mobile = models.CharField('博主手机', max_length=64, help_text='博主手机', blank=True)
    email = models.CharField('邮箱',  max_length=256, help_text='邮箱', blank=True, null=True)
    qq = models.CharField('QQ', max_length=64, help_text='QQ', blank=True, null=True)
    msn = models.CharField('MSN', max_length=256, help_text='MSN', blank=True, null=True)
    writing_time = models.CharField('撰写时间', help_text='撰写时间', max_length=64, blank=True)
    introduction = models.TextField('博主简介', help_text='博主简介', blank=True)
    cooperate_evaluation = models.TextField('合作评价', help_text='合作评价', blank=True)
    advantage = models.TextField('优势', help_text='优势', blank=True)
    other_info = models.TextField('其他', help_text='其他', blank=True)
    deleted = models.BooleanField('是否删除', help_text='备注', default=False)
    last_modified = models.DateTimeField('上次修改时间', auto_now=True)
    created_time = models.DateTimeField('增加时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '博主'
        verbose_name_plural = '博主'
        
    def __unicode__(self):
        return self.name
#版主表
class Moderator(models.Model):
    industry_type = models.CharField('行业类型', max_length=64, help_text='行业类型', blank=True)
    bbs_type = models.CharField('BBS类型', max_length=64, help_text='BBS类型', blank=True)
    media_name = models.CharField('媒体名称', max_length=64, help_text='网站', blank=True)
    channel = models.CharField('频道', max_length=64, help_text='频道', blank=True)
    bbs_block = models.CharField('BBS版块', max_length=256, help_text='BBS版块', blank=True)
    bbs_link = models.URLField('BBS链接', help_text='BBS链接', blank=True, null=True)
    alexa_ranking = models.CharField('Alexa排名', max_length=64, help_text='Alexa排名', blank=True)
    block_advantage = models.TextField('版块优势', help_text='版块优势', blank=True)
    moderator_id = models.CharField('版主ID', max_length=256, help_text='版主ID', blank=True)
    name = models.CharField('真实姓名', max_length=64, help_text='真实姓名', blank=True)
    mobile_number = models.CharField('手机', max_length=64, help_text='手机', blank=True)
    email = models.CharField('邮箱', max_length=256, help_text='邮箱', blank=True, null=True)
    qq = models.CharField('QQ', max_length=64, help_text='QQ', blank=True, null=True)
    msn = models.CharField('MSN', max_length=256, help_text='MSN', blank=True, null=True)
    cooperate_evaluation = models.TextField('合作评价', help_text='合作评价', blank=True)
    other_info = models.TextField('其他', help_text='其他', blank=True)
    deleted = models.BooleanField('是否删除', help_text='备注', default=False)
    last_modified = models.DateTimeField('上次修改时间', auto_now=True)
    created_time = models.DateTimeField('增加时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '版主'
        verbose_name_plural = '版主'
        
    def __unicode__(self):
        return self.name
    
#其他表  
class OtherHumanResource(models.Model):
    attr = models.CharField('属性', max_length=64, help_text='属性', blank=True)
    industry_type = models.CharField('适合行业类型', max_length=32, help_text='适合行业类型', blank=True)
    name = models.CharField('姓名', max_length=64, help_text='姓名', blank=True)
    works_style = models.TextField('作品风格', help_text='作品风格', blank=True)
    city = models.CharField('所在城市', max_length=64, help_text='所在城市', blank=True)
    mobile_number = models.CharField('手机', max_length=256, help_text='手机', blank=True)
    email = models.CharField('邮箱',  max_length=256, help_text='邮箱', blank=True, null=True)
    qq = models.CharField('QQ', max_length=64, help_text='QQ', blank=True)
    msn = models.CharField('MSN',  max_length=256, help_text='MSN', blank=True, null=True)
    making_time = models.CharField('制作时间', max_length=128, help_text='制作时间', blank=True)
    cooperate_evaluation = models.TextField('合作评价', help_text='合作评价', blank=True)
    other_info = models.TextField('其他', help_text='其他', blank=True)
    deleted = models.BooleanField('是否删除', help_text='备注', default=False)
    last_modified = models.DateTimeField('上次修改时间', auto_now=True)
    created_time = models.DateTimeField('增加时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '其他'
        verbose_name_plural = '其他'
        
    def __unicode__(self):
        return self.attr + '-' + self.name
    
#外协资源表    
class CooperateCorperationResource(models.Model):
    comany_name = models.CharField('公司名称', max_length=64, help_text='公司名称', blank=True)
    contactor = models.CharField('联系人', max_length=32, help_text='联系人', blank=True)
    fixed_number = models.CharField('座机', max_length=64, help_text='座机', blank=True)
    mobile_number = models.CharField('手机', max_length=64, help_text='手机', blank=True)
    email = models.CharField('邮箱', max_length=256, help_text='邮箱', blank=True, null=True)
    service_area = models.CharField('服务范围', max_length=256, help_text='服务范围', blank=True)
    charge_way = models.CharField('收费方式', max_length=256, help_text='收费方式', blank=True)
    month_cost_content = models.CharField('月费包含内容', max_length=256, help_text='月费包含内容', blank=True)
    company_advantage = models.TextField('公司优势', help_text='公司优势', blank=True)
    success_case = models.TextField('成功案例', help_text='成功案例', blank=True)
    company_introduction = models.TextField('公司简介', help_text='公司简介', blank=True)
    offer_price = models.CharField('报价', max_length=256,  help_text='报价', blank=True)
    cooperate_client = models.TextField('合作客户', help_text='合作客户', blank=True)
    cooperate_type = models.CharField('合作类型', max_length=32,  help_text='合作类型', blank=True)
    cooperate_content = models.TextField('合作内容', help_text='合作内容', blank=True)
    cooperate_amount = models.CharField('合作金额', max_length=256,  help_text='合作金额', blank=True)
    finish_quality = models.CharField('完成质量', max_length=256, help_text='完成质量', blank=True)
    media_score = models.CharField('媒介评分', max_length=256,  help_text='媒介评分', blank=True)
    other_info = models.TextField('其他', help_text='其他', blank=True)
    deleted = models.BooleanField('是否删除', help_text='备注', default=False)
    last_modified = models.DateTimeField('上次修改时间', auto_now=True)
    created_time = models.DateTimeField('增加时间', auto_now_add=True)
    
    class Meta:
        verbose_name = '外协资源'
        verbose_name_plural = '外协资源'
        
    def __unicode__(self):
        return self.comany_name