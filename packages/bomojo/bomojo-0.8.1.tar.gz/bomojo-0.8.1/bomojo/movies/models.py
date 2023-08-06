# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import reduce

from django.db import models
from django.db.models import Q

from bomojo.utils import split_on_whitespace


class MovieManager(models.Manager):
    def search(self, search_term, max_results):
        queryset = self.get_queryset()
        matches = queryset.filter(title__search=search_term)

        results = list(matches[:max_results])
        if len(results) == max_results:
            return results

        matches = queryset.filter(
            title__istartswith=search_term).exclude(
            id__in=[r.id for r in results])
        results += list(matches[:(max_results - len(results))])
        if len(results) == max_results:
            return results

        query = reduce(lambda q, term: q & Q(title__icontains=term),
                       split_on_whitespace(search_term), Q())
        matches = queryset.filter(query).exclude(
            id__in=[r.id for r in results])
        results += list(matches[:(max_results - len(results))])
        return results


class Movie(models.Model):
    title = models.CharField(max_length=1024, db_index=True)
    external_id = models.CharField(max_length=2048, db_index=True, unique=True)

    objects = MovieManager()

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
