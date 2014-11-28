#coding=utf-8
"""此文件用来检查某个域名是否可用, 通过执行python manage.py check_domain来测试，以下为需要注意的地方:
    1.如果想定时执行此命令可与crontab结合，需要注意的是在crontab -e 建任务时，python必须要加全路径,而且必须在manage.py所在的目录，例如
    ***** cd /home/lhh/mediachooser; /usr/local/bin/python manage.py check_domain
    2.对于某些url，如果浏览器打开正常，而用代码打开发生异常的情况，就尝试添加header，把所有的都添加进去看是否成功，成功后再减少某一个，看看
      最后是哪个引起的"""

from django.core.management.base import BaseCommand
from django.core.mail import send_mail, BadHeaderError

from MediaChooser.client.models import DomainName

import urllib2

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        headers = { 'User-Agent' : user_agent, 'Accept': 'text/html'}
        domain_name_list = DomainName.objects.all()
        unavailabe_url_list = []
        for domain_name in domain_name_list:
            url = domain_name.domain_name 
            if  url.find('http://') == -1:
                url = 'http://' + url 
            try:
                req = urllib2.Request(url=url, headers=headers)
                res = urllib2.urlopen(req)
                if res.code != 200:
                    unavailabe_url_list.append(url)
            except Exception, e:
                unavailabe_url_list.append(url)
        if unavailabe_url_list:
            send_mail(u'不可用的域名', u'暂时不可用的url: ' + ', '.join(unavailabe_url_list), 'andc-it@and-c.com', ['andc-it@and-c.com'])
