# -*- coding: utf-8 -*-
from django.db import models
from django.utils.translation import ugettext as _
from datetime import datetime
from autoslug import AutoSlugField
from filer.fields.image import FilerImageField

class Category(models.Model):
    #Work categories"
    name = models.CharField(_('Name'), max_length=200)# (requis)
    description = models.TextField(_('Description'), null=True,blank=True)
    
    def __unicode__(self):
        return self.name

class Work(models.Model):
    #Work / Customer
    category = models.ForeignKey(Category)
    name = models.CharField(_('Name'), max_length=200)# (requis)
    description = models.TextField(_('Description'), null=True,blank=True)
    image = FilerImageField(null=True, blank=True, related_name="image_work")
    youtube_id = models.CharField(_('Youtube ID'), max_length=100)
    home_page = models.BooleanField()

    def __unicode__(self):
        return self.name

