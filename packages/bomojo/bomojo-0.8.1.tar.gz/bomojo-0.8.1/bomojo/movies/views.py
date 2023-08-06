# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
from decimal import Decimal

from django.http import HttpResponseBadRequest, JsonResponse
from django.views.decorators.cache import cache_page

import pybomojo

from bomojo.backends import get_movie_backend
from bomojo.movies.models import Movie, PriceIndex
from bomojo.movies.renderers import render_box_office, render_movie
from bomojo.utils import get_setting, format_money


@cache_page(60 * 60 * 24)
def search(request):
    search_term = request.GET.get('title', '').strip()

    if not search_term:
        return HttpResponseBadRequest('"title" is required')

    if len(search_term) < get_setting('MOVIE_MIN_SEARCH_LENGTH'):
        return JsonResponse({'results': []})

    max_results = get_setting('MOVIE_MAX_SEARCH_RESULTS')
    movies = Movie.objects.search(search_term, max_results)

    if (len(movies) < max_results or
            not any(_is_exact_result(m, search_term) for m in movies)):
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

    backend = get_movie_backend()
    results = [_render_movie(m, backend, search_term) for m in movies]

    # Move exact result to the top. This is very inefficient, but it'll get the
    # job done for now. (The more efficient code would be slightly uglier.)
    results = ([r for r in results if r['exact']] +
               [r for r in results if not r['exact']])[:max_results]

    return JsonResponse({'results': results})


@cache_page(60 * 15)
def box_office(request, movie_id):
    try:
        box_office = pybomojo.get_box_office(
            get_movie_backend().parse_movie_id(movie_id))

        if request.GET.get('adjusted', '0') != '0':
            results = box_office.get('box_office', [])
            if len(results) == 0:
                return JsonResponse(render_box_office(box_office, movie_id))

            release_year = min([datetime.strptime(r['date'], '%b. %d, %Y').year
                                for r in results])
            inflation_map = {
                (pi.year, pi.month): pi.value
                for pi in PriceIndex.objects.filter(year__gte=release_year)
            }

            if len(inflation_map) == 0:
                return JsonResponse({
                    'errors': {
                        'adjusted': ['Inflation data is not available.']
                    }
                }, status=500)

            today = datetime.now()
            latest_cpi = inflation_map[sorted(inflation_map.keys())[-1]]

            def adjust_result(result, index):
                date = datetime.strptime(result['date'], '%b. %d, %Y')
                cpi = inflation_map.get((date.year, date.month), latest_cpi)
                result['gross'] = format_money(Decimal(result['gross']) *
                                               latest_cpi / cpi)
                if index > 0:
                    previous_result = results[index - 1]
                    result['cumulative'] = (result['gross'] +
                                            previous_result['cumulative'])
                else:
                    result['cumulative'] = result['gross']

                return result

            for i, result in enumerate(results):
                adjust_result(result, i)

        return JsonResponse(render_box_office(box_office, movie_id))
    except pybomojo.MovieNotFound as e:
        return JsonResponse({
            'errors': {
                'movie': [str(e)]
            }
        }, status=404)


def _render_movie(movie, backend, search_term):
    result = render_movie(movie, backend)
    result['exact'] = _is_exact_result(movie, search_term)
    return result


def _is_exact_result(movie, search_term):
    return movie.title.lower() == search_term
