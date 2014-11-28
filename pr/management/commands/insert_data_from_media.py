#coding=utf-8

from django.core.management.base import BaseCommand
import pyodbc

from MediaChooser.media.models import Media, MediaCategory
from MediaChooser.pr.models import MediaResource, Reporter

class Command(BaseCommand):
    def handle(self, *args, **options):
       media_list = Media.objects.all()
       for media in media_list:
           if media.first_category:
               MediaResource.objects.create(media_name=media.c_name, media_property=media.first_category.c_name, url=media.domain)
           else:
               MediaResource.objects.create(media_name=media.c_name, url=media.domain)