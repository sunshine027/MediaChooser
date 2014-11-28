#! /usr/bin/env python
#coding=utf-8

from django.core.management.base import BaseCommand
from MediaChooser.media_planning.views import delete_mp
import sys

class Command(BaseCommand):
    def handle(self, *args, **options):
        pass

mp_id = sys.argv[2]

ret = delete_mp(mp_id)
print ret
