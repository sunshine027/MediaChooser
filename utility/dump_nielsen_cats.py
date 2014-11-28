#! /usr/bin/env python
#coding=utf-8

from django.core import serializers as se
from MediaChooser.NielsenMedia.models import NielsenCategory

def dump():
    data = se.serialize("json", NielsenCategory.objects.all(), indent=4)
    out = open('nielsencats.json','w')
    out.write(data)
    out.close()

class Command(BaseCommand):

    def handle(self, *args, **options):
        dump()