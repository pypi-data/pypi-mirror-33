# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models


class Movie(models.Model):
    title = models.CharField(max_length=1024, db_index=True)
    external_id = models.CharField(max_length=2048, db_index=True, unique=True)

    def __str__(self):
        return f'{self.title} ({self.external_id})'


class PriceIndex(models.Model):
    class Meta:
        unique_together = [
            ('year', 'month')
        ]

    year = models.IntegerField(db_index=True)
    month = models.IntegerField()
    value = models.DecimalField(max_digits=12, decimal_places=3)

    def __str__(self):
        return f'{self.year}-{self.month:02}: {self.value}'
