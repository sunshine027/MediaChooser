from django.shortcuts import _get_queryset, render_to_response
from django.template import RequestContext
from django.template import loader
from django.http import HttpResponse

error_page = 'ad_resource_mgmt/error.html'

def get_object_or_error(klass, message, *args, **kwargs):
    """
        Uses get() to return an object, or raises a Http404 exception if the object
        does not exist.
        
        klass may be a Model, Manager, or QuerySet object. All other passed
        arguments and keyword arguments are used in the get() query.

        Note: Like with get(), an MultipleObjectsReturned will be raised if more than one
        object is found.
    """

    queryset = _get_queryset(klass)
    try:
        return queryset.get(*args, **kwargs)
    except queryset.model.DoesNotExist:
        #return render_to_response(error_page, {'message': message})
        return HttpResponse(loader.render_to_string(error_page, {'message': message}))