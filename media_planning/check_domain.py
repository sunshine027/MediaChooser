#coding=utf-8

from django.core.management.base import BaseCommand
from django.core.mail import send_mail, BadHeaderError

from MediaChooser.client.models import DomainName

import httplib

class Command(BaseCommand):
    
    def handle(self, *args, **options):
        domain_name_list = DomainName.objects.all()
        unavailabe_url_list = []
        for domain_name in domain_name_list:
            url = domain_name.domain_name
            try:
                con = httplib.HTTPConnection(url)
                con.request('HEAD', '')
                res = con.getresponse()
                if res.status != 200:
                    unavailabe_url_list.append(url)
            except Exception, e:
                unavailabe_url_list.append(url)
        send_mail('不可用的域名', '暂时不可用的url包括' + ','.join(unavailabe_url_list)[:-1], 'admin@and_c.com', ['lihuanhuan@and-c.com'])
        