#! /usr/bin/env python
#coding=utf-8

from MediaChooser.media.models import Media
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response

# Get media info
@login_required
def get_mediainfo(request):
    if request.method == "POST":
        pass
    else:
        medias = Media.objects.all().order_by('first_category')
        user = request.user
        return render_to_response('media/get_mediainfo.html', locals())
