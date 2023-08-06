from django.test import RequestFactory, override_settings

from bomojo.matchups.forms import MatchupForm
from bomojo.tests import TestCase


class MatchupFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_movie('Foo')
        cls.create_movie('Foo 2', external_id='foo2')
        cls.create_movie('Foo 3', external_id='foo3')
        cls.create_movie('Bar')

    def setUp(self):
        super().setUp()
        self.user = self.create_user('joe')
        self.request = RequestFactory().post('/matchup')

        # Simulate the user being authenticated.
        self.request.user = self.user

    def test_happy_path(self):
        form = MatchupForm(self.request, {
            'title': 'foo trilogy',
            'description': 'The entire foo trilogy',
            'movies': ['foo', 'bar'],
            'period': '30d'
        })

        self.assertTrue(form.is_valid(), form.errors)

        matchup = form.save()

        self.assertEqual(matchup.title, 'foo trilogy')
        self.assertEqual(matchup.description, 'The entire foo trilogy')
        self.assertEqual(matchup.movies, ['foo.htm', 'bar.htm'])
        self.assertEqual(matchup.period, '30d')

    def test_minimal_fields(self):
        form = MatchupForm(self.request, {
            'title': 'foo vs bar',
            'movies': ['foo', 'bar']
        })

        self.assertTrue(form.is_valid(), form.errors)

        matchup = form.save()

        self.assertEqual(matchup.title, 'foo vs bar')
        self.assertEqual(matchup.description, '')
        self.assertEqual(matchup.movies, ['foo.htm', 'bar.htm'])
        self.assertEqual(matchup.period, '')

    def test_parses_movie_ids(self):
        form = MatchupForm(self.request, {
            'title': 'foo vs bar',
            'movies': ['foo.htm', 'bar.htm']
        })

        self.assertTrue(form.is_valid(), form.errors)

        matchup = form.save()

        self.assertEqual(matchup.title, 'foo vs bar')
        self.assertEqual(matchup.description, '')
        self.assertEqual(matchup.movies, ['foo.htm', 'bar.htm'])
        self.assertEqual(matchup.period, '')

    def test_title_cannot_be_omitted(self):
        form = MatchupForm(self.request, {
            'description': 'The entire foo trilogy',
            'movies': ['foo1', 'foo2', 'foo3']
        })

        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('required', *form.errors['title'])

    def test_title_cannot_be_blank(self):
        form = MatchupForm(self.request, {
            'title': '',
            'description': 'The entire foo trilogy',
            'movies': ['foo1', 'foo2', 'foo3']
        })
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('required', *form.errors['title'])

    def test_movies_cannot_be_omitted(self):
        form = MatchupForm(self.request, {
            'title': 'foo vs bar'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('movies', form.errors)
        self.assertIn('required', *form.errors['movies'])

    def test_movies_cannot_be_empty(self):
        form = MatchupForm(self.request, {
            'title': 'foo vs bar',
            'movies': []
        })
        self.assertFalse(form.is_valid())
        self.assertIn('movies', form.errors)
        self.assertIn('required', *form.errors['movies'])

    def test_movies_must_be_valid(self):
        form = MatchupForm(self.request, {
            'title': 'foo vs quux',
            'movies': ['foo', 'quux']
        })
        self.assertFalse(form.is_valid())
        self.assertIn('movies', form.errors)

    def test_period_must_be_valid_if_provided(self):
        form = MatchupForm(self.request, {
            'title': 'foo vs bar',
            'movies': ['foo', 'bar'],
            'period': 'blah'
        })
        self.assertFalse(form.is_valid())
        self.assertIn('period', form.errors)
        self.assertIn('valid', *form.errors['period'])

    def test_featured_only_allowed_for_featured_contributors(self):
        form = MatchupForm(self.request, {
            'title': 'foo vs bar',
            'movies': ['foo', 'bar'],
            'featured': True
        })
        self.assertFalse(form.is_valid())
        self.assertIn('featured', form.errors)

        self.user.is_staff = True
        self.user.save()

        # Re-initialize form to run validation again with updated data.
        form = MatchupForm(self.request, {
            'title': 'foo vs bar',
            'movies': ['foo', 'bar'],
            'featured': True
        })
        self.assertTrue(form.is_valid())
