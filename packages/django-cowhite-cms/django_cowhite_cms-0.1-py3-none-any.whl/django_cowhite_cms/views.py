from django.shortcuts import render, get_object_or_404
from django.views import generic as generic_views
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render

from .models import *


class PageView(generic_views.TemplateView):
    template_name = "django_cowhite_cms/page.html"

    def get_context_data(self, *args, **kwargs):
        context = super(PageView, self).get_context_data(*args, **kwargs)
        context['page'] = get_object_or_404(Page, slug=kwargs['slug'])
        return context

