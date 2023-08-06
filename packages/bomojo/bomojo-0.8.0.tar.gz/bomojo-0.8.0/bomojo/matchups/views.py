# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.forms.models import model_to_dict
from django.http import JsonResponse
from django.views import View

from bomojo.matchups.forms import MatchupForm
from bomojo.matchups.models import Matchup
from bomojo.matchups.renderers import render_matchup
from bomojo.utils import get_setting


class MatchupsView(View):
    ALLOWED_SORTING = ('created_on', 'updated_on')

    def get(self, request):
        if request.GET.get('featured', 'false') != 'false':
            matchups = Matchup.objects.filter(featured=True)
        elif request.user.is_authenticated:
            matchups = request.user.matchups
        else:
            return JsonResponse([], safe=False)

        sort = request.GET.get('sort', get_setting('DEFAULT_MATCHUP_SORTING'))
        if not (sort in self.ALLOWED_SORTING or
                (sort.startswith('-') and sort[1:] in self.ALLOWED_SORTING)):
            return JsonResponse({
                'errors': {
                    'sort': ['You can only sort by created_on or updated_on.']
                }
            }, status=400)

        recent_matchups = matchups.order_by(sort)[:20]
        return JsonResponse([render_matchup(matchup, include_movies=False)
                             for matchup in recent_matchups], safe=False)

    def post(self, request):
        if not request.user.is_authenticated:
            return JsonResponse({
                'errors': {
                    'creator': ['You must log in to create a matchup.']
                }
            }, status=401)

        form = MatchupForm(request, request.JSON)
        if form.is_valid():
            matchup = form.save()
            return JsonResponse(render_matchup(matchup), status=201)
        else:
            return JsonResponse({'errors': form.errors}, status=400)


class MatchupView(View):
    def get(self, request, slug):
        try:
            matchup = Matchup.objects.get(slug=slug)
            return JsonResponse(render_matchup(matchup))
        except Matchup.DoesNotExist:
            return JsonResponse({
                'errors': {
                    'slug': ['That matchup does not exist.']
                }
            }, status=404)

    def put(self, request, slug):
        if not request.user.is_authenticated:
            return JsonResponse({
                'errors': {
                    'creator': ['You must log in to edit your matchups.']
                }
            }, status=401)

        try:
            matchup = Matchup.objects.get(slug=slug)
        except Matchup.DoesNotExist:
            return JsonResponse({
                'errors': {
                    'slug': ['That matchup does not exist.']
                }
            }, status=404)

        if matchup.user != request.user:
            return JsonResponse({
                'errors': {
                    'creator': ["You cannot edit other people's matchups."]
                }
            }, status=403)

        data = model_to_dict(matchup)
        data.update(request.JSON)

        form = MatchupForm(request, data, instance=matchup)
        if form.is_valid():
            matchup = form.save()
            return JsonResponse(render_matchup(matchup), status=200)
        else:
            return JsonResponse({'errors': form.errors}, status=400)
