# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from bomojo.matchups.models import Matchup
from bomojo.movies.models import Movie


@admin.register(Matchup)
class MatchupAdmin(admin.ModelAdmin):
    list_display = ('featured', 'title', 'user', 'created_on')


@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'external_id')
