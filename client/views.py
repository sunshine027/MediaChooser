#! /usr/bin/env python
#coding=utf-8

from django.http import HttpResponse
from MediaChooser.client.models import Client
from django.db import IntegrityError

import simplejson as json

# used for ajax
def create_client(request):
    if request.method == 'POST':
        c_name = request.POST.get('c_name', None)
        e_name = request.POST.get('e_name', None)
        desc = request.POST.get('desc', None)
        
        response = HttpResponse()
        
        try:
            new_client = Client(c_name=c_name, e_name=e_name, desc=desc)
            new_client.save()
            
            response.write(json.dumps([1, [new_client.id, new_client.c_name, new_client.e_name]]))
            return response
        except IntegrityError:
            response.write(json.dumps([0, '客户名已存在，请不要重复创建！']))
            return response
        except:
            response.write(json.dumps([0, '创建客户失败！']))
            return response
