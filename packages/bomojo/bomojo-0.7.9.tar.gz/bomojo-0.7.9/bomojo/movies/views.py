# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from functools import reduce

from django.db.models import Q
from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.cache import cache_page

import pybomojo

from bomojo.backends import get_movie_backend
from bomojo.movies.models import Movie
from bomojo.movies.renderers import render_box_office, render_movie
from bomojo.utils import get_setting, split_on_whitespace


@cache_page(60 * 60 * 24)
def search(request):
    search_term = request.GET.get('title', '').strip()

    if not search_term:
        return HttpResponseBadRequest('"title" is required')

    if len(search_term) < get_setting('MOVIE_MIN_SEARCH_LENGTH'):
        return JsonResponse({'results': []})

    max_results = get_setting('MOVIE_MAX_SEARCH_RESULTS')
    query = reduce(lambda q, term: q | Q(title__icontains=term),
                   split_on_whitespace(search_term), Q())
    movies = list(Movie.objects.filter(query)[:max_results])

    if len(movies) < max_results:
        api_results = pybomojo.search_movies(search_term)

        for api_result in api_results:
            movie, created = Movie.objects.get_or_create(
                external_id=api_result['movie_id'], defaults={
                    'title': api_result['title'],
                })
            if created:
                movies.append(movie)
            elif movie.title != api_result['title']:
                # On the off chance the movie's title has changed in the
                # external service, go ahead and update it now.
                movie.title = api_result['title']
                movie.save()

    movies = movies[:max_results]

    backend = get_movie_backend()
    results = [_render_movie(m, backend, search_term) for m in movies]

    # Move exact result to the top. This is very inefficient, but it'll get the
    # job done for now. (The more efficient code would be slightly uglier.)
    results = ([result for result in results if result['exact']] +
               [result for result in results if not result['exact']])

    return JsonResponse({'results': results})


@cache_page(60 * 15)
def box_office(request, movie_id):
    try:
        box_office = pybomojo.get_box_office(
            get_movie_backend().parse_movie_id(movie_id))
        return JsonResponse(render_box_office(box_office, movie_id))
    except pybomojo.MovieNotFound as e:
        return JsonResponse({
            'errors': {
                'movie': [str(e)]
            }
        }, status=404)


def _render_movie(movie, backend, search_term):
    result = render_movie(movie, backend)
    result['exact'] = movie.title.lower() == search_term
    return result
