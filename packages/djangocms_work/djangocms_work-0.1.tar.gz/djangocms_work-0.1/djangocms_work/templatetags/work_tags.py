# coding: utf-8

#Import Models

from djangocms_work.models import Work, Category
from django import template

register = template.Library()


@register.assignment_tag
def list_work_categories():
    categories = Category.objects.all().order_by('name')
    return categories

@register.assignment_tag
def list_work():
    works = Work.objects.all().order_by('name')
    return works

