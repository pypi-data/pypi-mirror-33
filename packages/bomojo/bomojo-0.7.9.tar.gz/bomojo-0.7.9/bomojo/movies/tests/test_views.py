# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.cache import cache
from django.test import override_settings

from mock import patch
from pybomojo import MovieNotFound

from bomojo.movies.models import Movie
from bomojo.tests import TestCase


class SearchTestCase(TestCase):
    def setUp(self):
        cache.clear()

    def test_requires_title_param(self):
        response = self.client.get('/movies/search')
        self.assertEqual(response.status_code, 400)

    def test_title_cannot_be_blank(self):
        response = self.client.get('/movies/search?title=%20')
        self.assertEqual(response.status_code, 400)

    @patch('pybomojo.search_movies')
    def test_returns_json_response(self, mock):
        mock.return_value = [
            {
                'title': 'Foo',
                'movie_id': 'foo',
                'exact': True
            }
        ]

        response = self.client.get('/movies/search?title=foo')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertJSONEqual(response.content, {
            'results': [
                {
                    'title': 'Foo',
                    'movie_id': 'foo',
                    'exact': True
                }
            ]
        })

    @patch('pybomojo.search_movies')
    def test_returns_exact_result_first(self, mock):
        mock.return_value = [
            {
                'title': 'Foo',
                'movie_id': 'foo',
                'exact': False
            },
            {
                'title': 'Fools Rush In',
                'movie_id': 'foolsrushin',
                'exact': True
            }
        ]

        response = self.client.get('/movies/search/?title=fools%20rush%20in')
        self.assertJSONEqual(response.content, {
            'results': [
                {
                    'title': 'Fools Rush In',
                    'movie_id': 'foolsrushin',
                    'exact': True
                },
                {
                    'title': 'Foo',
                    'movie_id': 'foo',
                    'exact': False
                }
            ]
        })

    @patch('pybomojo.search_movies')
    def test_formats_movie_ids(self, mock):
        mock.return_value = [
            {
                'title': 'Foo',
                'movie_id': 'foo.htm',
                'exact': True
            }
        ]

        response = self.client.get('/movies/search/?title=foo')
        self.assertJSONEqual(response.content, {
            'results': [
                {
                    'title': 'Foo',
                    'movie_id': 'foo',
                    'exact': True
                }
            ]
        })

    @override_settings(
        MOVIE_BACKEND='bomojo.tests.backends.UpperToLowerMovieBackend')
    @patch('pybomojo.search_movies')
    def test_configurable_movie_backend(self, mock):
        mock.return_value = [
            {
                'title': 'Foo',
                'movie_id': 'FOO',
                'exact': True
            }
        ]

        response = self.client.get('/movies/search/?title=foo')
        self.assertJSONEqual(response.content, {
            'results': [
                {
                    'title': 'Foo',
                    'movie_id': 'foo',
                    'exact': True
                }
            ]
        })

    @patch('pybomojo.search_movies')
    def test_caches_results(self, mock):
        mock.return_value = []

        response = self.client.get('/movies/search/?title=foo%202')
        self.assertJSONEqual(response.content, {'results': []})

        mock.side_effect = AssertionError(
            'should not have called search_movies again (expected to use '
            'cached result)')

        response = self.client.get('/movies/search/?title=foo%202')
        self.assertJSONEqual(response.content, {'results': []})

    @patch('pybomojo.search_movies')
    def test_saves_results_to_database(self, mock):
        mock.return_value = [
            {
                'title': 'Foo',
                'movie_id': 'foo',
                'exact': True
            },
            {
                'title': 'Foo 2: The Awakening',
                'movie_id': 'foo2',
                'exact': False
            }
        ]

        response = self.client.get('/movies/search/?title=foo')
        self.assertJSONEqual(response.content, {
            'results': [
                {
                    'title': 'Foo',
                    'movie_id': 'foo',
                    'exact': True
                },
                {
                    'title': 'Foo 2: The Awakening',
                    'movie_id': 'foo2',
                    'exact': False
                }
            ]
        })

        movies = Movie.objects.filter(title__search='Foo').order_by('title')
        self.assertEqual(2, len(movies))
        self.assertEqual('Foo', movies[0].title)
        self.assertEqual('foo', movies[0].external_id)
        self.assertEqual('Foo 2: The Awakening', movies[1].title)
        self.assertEqual('foo2', movies[1].external_id)

    @override_settings(MOVIE_MAX_SEARCH_RESULTS=2)
    @patch('pybomojo.search_movies')
    def test_searches_database_first(self, mock):
        self.create_movie(title='Foo')
        self.create_movie(title='Foo 2: The Awakening', external_id='foo2')

        mock.side_effect = AssertionError(
            'should not have called search_movies since '
            'MOVIE_MAX_SEARCH_RESULTS were already in the database')

        response = self.client.get('/movies/search/?title=foo')
        self.assertJSONEqual(response.content, {
            'results': [
                {
                    'title': 'Foo',
                    'movie_id': 'foo',
                    'exact': True
                },
                {
                    'title': 'Foo 2: The Awakening',
                    'movie_id': 'foo2',
                    'exact': False
                }
            ]
        })

    @override_settings(MOVIE_MAX_SEARCH_RESULTS=2)
    @patch('pybomojo.search_movies')
    def test_searches_api_after_database(self, mock):
        self.create_movie(title='Foo')

        mock.return_value = [
            {
                'title': 'Foo 2: The Awakening',
                'movie_id': 'foo2',
                'exact': False
            },
            {
                'title': 'Foo 3: Return of Foo',
                'movie_id': 'foo3',
                'exact': False
            }
        ]

        response = self.client.get('/movies/search/?title=foo')

        # Only MOVIE_MAX_SEARCH_RESULTS should be returned.
        self.assertJSONEqual(response.content, {
            'results': [
                {
                    'title': 'Foo',
                    'movie_id': 'foo',
                    'exact': True
                },
                {
                    'title': 'Foo 2: The Awakening',
                    'movie_id': 'foo2',
                    'exact': False
                }
            ]
        })

    @patch('pybomojo.search_movies')
    def test_handles_title_mismatch_between_api_and_database(self, mock):
        movie = self.create_movie(title='Foo', external_id='foo')

        mock.return_value = [
            {
                'title': 'Foo (2018)',
                'movie_id': 'foo',
                'exact': True
            }
        ]

        response = self.client.get('/movies/search/?title=foo')

        self.assertJSONEqual(response.content, {
            'results': [
                {
                    'title': 'Foo',
                    'movie_id': 'foo',
                    'exact': True
                }
            ]
        })

        # Also, the database record should have been updated.
        movie.refresh_from_db()
        self.assertEqual('Foo (2018)', movie.title)

    @patch('pybomojo.search_movies')
    def test_handles_partial_match_from_database(self, mock):
        movie = self.create_movie(title='Attack of the Foo', external_id='foo')

        mock.return_value = []

        response = self.client.get('/movies/search/?title=att')

        self.assertJSONEqual(response.content, {
            'results': [
                {
                    'title': 'Attack of the Foo',
                    'movie_id': 'foo',
                    'exact': False
                }
            ]
        })


class BoxOfficeTestCase(TestCase):
    def setUp(self):
        cache.clear()

    @patch('pybomojo.get_box_office')
    def test_returns_json_response(self, mock):
        mock.return_value = {
            'title': 'Foo 3: ',
            'href': 'http://moviewebsite.com/foo3',
            'box_office': [{
                'day': 'Fri',
                'date': 'Jul. 14 2017',
                'rank': 1,
                'gross': 22100000,
                'theaters': 4022,
                'cumulative': 22100000
            }]
        }

        response = self.client.get('/movies/foo3/boxoffice')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['content-type'], 'application/json')
        self.assertJSONEqual(response.content, {
            'title': 'Foo 3: ',
            'movie_id': 'foo3',
            'href': 'http://moviewebsite.com/foo3',
            'box_office': [{
                'day': 'Fri',
                'date': 'Jul. 14 2017',
                'rank': 1,
                'gross': 22100000,
                'theaters': 4022,
                'cumulative': 22100000
            }]
        })

    @patch('pybomojo.get_box_office')
    def test_parses_movie_ids(self, mock):
        mock.return_value = {}  # doesn't matter
        self.client.get('/movies/foo/boxoffice')
        mock.assert_called_with('foo.htm')

    @override_settings(
        MOVIE_BACKEND='bomojo.tests.backends.UpperToLowerMovieBackend')
    @patch('pybomojo.get_box_office')
    def test_configurable_movie_backend(self, mock):
        mock.return_value = {}  # doesn't matter
        self.client.get('/movies/foo/boxoffice')
        mock.assert_called_with('FOO')

    @patch('pybomojo.get_box_office')
    def test_caches_results(self, mock):
        mock.return_value = {
            'title': 'Bar',
            'href': 'http://moviewebsite.com/bar',
            'box_office': []
        }

        response = self.client.get('/movies/bar/boxoffice')
        self.assertJSONEqual(response.content, {
            'title': 'Bar',
            'movie_id': 'bar',
            'href': 'http://moviewebsite.com/bar',
            'box_office': []
        })

        mock.side_effect = AssertionError(
            'should not have called get_box_office again (expected to use '
            'cached result)')

        response = self.client.get('/movies/bar/boxoffice')
        self.assertJSONEqual(response.content, {
            'title': 'Bar',
            'movie_id': 'bar',
            'href': 'http://moviewebsite.com/bar',
            'box_office': []
        })

    @patch('pybomojo.get_box_office')
    def test_returns_404_if_movie_not_found(self, mock):
        mock.side_effect = MovieNotFound('foo')

        response = self.client.get('/movies/foo/boxoffice')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {
            'errors': {
                'movie': ['"foo" not found']
            }
        })
