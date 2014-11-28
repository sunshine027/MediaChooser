#! /usr/bin/env python
#coding=utf-8

from MediaChooser.media_weekly_report.models import WorkType, Project, ReportItem, GroupLeader
from django.contrib import admin

class WorkTypeAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ['name']
    list_display = ('__unicode__', 'parent')
    
class ProjectAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ['name']
    list_display = ('name', 'client', 'revenue', 'profit')
    
class ReportItemAdmin(admin.ModelAdmin):
    def ch_name(obj):
            return "%s%s" % (obj.responsible_user.last_name, obj.responsible_user.first_name)
    ch_name.short_description = 'responsible_user'
    
    save_on_top = True
    search_fields = []
    list_display = ('__unicode__', 'start_day', 'end_day', 'work_type', 'client', 'project', 'work_subtype', 'responsible_user', 'duration')
    

class GroupLeaderAdmin(admin.ModelAdmin):
    save_on_top = True
    search_fields = ['leader']
    list_display = ('leader', 'group')
    

admin.site.register(WorkType, WorkTypeAdmin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(ReportItem, ReportItemAdmin)
admin.site.register(GroupLeader, GroupLeaderAdmin)
