# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class Machines(models.Model):
    session = models.CharField(max_length=50)
    visit = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    #job_pairs = models.CharField(max_length=50)#not sure about data type
    image_id = models.CharField(max_length=50)
    #measurement = models.CharField(max_length=50)
    time = models.CharField(max_length=50)
    #job = models.CharField(max_length=50)
    forwarder_id = models.CharField(max_length=50)

    def __str__(self):
        return self.time + " - " + self.forwarder_id

