# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=1024, db_index=True)
    external_id = models.CharField(max_length=2048, db_index=True, unique=True)
