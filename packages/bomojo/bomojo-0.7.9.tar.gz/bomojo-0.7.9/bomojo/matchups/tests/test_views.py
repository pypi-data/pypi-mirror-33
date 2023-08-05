# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json
import os

from django.test import override_settings

from freezegun import freeze_time

from bomojo.matchups.models import Matchup
from bomojo.tests import TestCase
from bomojo.utils import get_avatar_url


class CreateTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = cls.create_user('joe')
        cls.avatar_url = get_avatar_url(cls.user.email)

        cls.create_movie('Foo')
        cls.create_movie('Foo 2', external_id='foo2.htm')
        cls.create_movie('Foo 3', external_id='foo3.htm')
        cls.create_movie('Bar')

    def setUp(self):
        super().setUp()
        self.client.force_login(self.user)

    @freeze_time('2018-03-10 22:17:00')
    def test_happy_path(self):
        response = self.client.post('/matchups/', json.dumps({
            'title': 'foo vs bar',
            'movies': ['foo', 'bar']
        }), content_type='application/json')

        self.assertEqual(201, response.status_code)
        self.assertEqual(response.json(), {
            'creator': {
                'username': 'joe',
                'avatar': self.avatar_url
            },
            'slug': 'foo-vs-bar',
            'title': 'foo vs bar',
            'image_url': None,
            'description': '',
            'movies': [
                {
                    'title': 'Foo',
                    'movie_id': 'foo'
                },
                {
                    'title': 'Bar',
                    'movie_id': 'bar'
                }
            ],
            'period': '',
            'featured': False,
            'created': '2018-03-10T22:17:00+00:00',
            'updated': '2018-03-10T22:17:00+00:00'
        })

        matchup = Matchup.objects.get(slug='foo-vs-bar')
        self.assertEqual('foo vs bar', matchup.title)
        self.assertEqual(['foo.htm', 'bar.htm'], matchup.movies)

        # Ensure fields not supplied are blank.
        self.assertEqual('', matchup.description)
        self.assertEqual('', matchup.period)

    @freeze_time('2018-03-10 22:17:00')
    def test_happy_path_all_fields(self):
        response = self.client.post('/matchups/', json.dumps({
            'title': 'foo trilogy',
            'description': 'The entire foo trilogy',
            'movies': ['foo', 'foo2', 'foo3'],
            'period': '90d'
        }), content_type='application/json')

        self.assertEqual(201, response.status_code)
        self.assertEqual(response.json(), {
            'creator': {
                'username': 'joe',
                'avatar': self.avatar_url
            },
            'slug': 'foo-trilogy',
            'title': 'foo trilogy',
            'image_url': None,
            'description': 'The entire foo trilogy',
            'movies': [
                {
                    'title': 'Foo',
                    'movie_id': 'foo'
                },
                {
                    'title': 'Foo 2',
                    'movie_id': 'foo2'
                },
                {
                    'title': 'Foo 3',
                    'movie_id': 'foo3'
                }
            ],
            'period': '90d',
            'featured': False,
            'created': '2018-03-10T22:17:00+00:00',
            'updated': '2018-03-10T22:17:00+00:00'
        })

        matchup = Matchup.objects.get(slug='foo-trilogy')
        self.assertEqual('foo trilogy', matchup.title)
        self.assertEqual('The entire foo trilogy', matchup.description)
        self.assertEqual(['foo.htm', 'foo2.htm', 'foo3.htm'], matchup.movies)
        self.assertEqual('90d', matchup.period)

    def test_requires_title_param(self):
        response = self.client.post('/matchups/', json.dumps({
            'movies': ['foo', 'bar']
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'errors': {
                'title': ['This field is required.']
            }
        })

    def test_title_cannot_be_blank(self):
        response = self.client.post('/matchups/', json.dumps({
            'title': '',
            'movies': ['foo', 'bar']
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'errors': {
                'title': ['This field is required.']
            }
        })

    def test_requires_movies_param(self):
        response = self.client.post('/matchups/', json.dumps({
            'title': 'foo vs bar'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'errors': {
                'movies': ['This field is required.']
            }
        })

    def test_movies_cannot_be_empty(self):
        response = self.client.post('/matchups/', json.dumps({
            'title': 'foo vs bar',
            'movies': []
        }), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {
            'errors': {
                'movies': ['This field is required.']
            }
        })

    def test_handles_duplicate_movies(self):
        response = self.client.post('/matchups/', json.dumps({
            'title': 'foo vs bar',
            'movies': ['foo', 'bar', 'bar']
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        response_data = response.json()

        self.assertEqual('foo vs bar', response_data['title'])
        self.assertEqual(['foo', 'bar'],
                         [m['movie_id'] for m in response_data['movies']])

    def test_401_for_unauthenticated_attempt(self):
        self.client.logout()
        response = self.client.post('/matchups/', json.dumps({
            'title': 'foo vs bar',
            'movies': ['foo', 'bar']
        }), content_type='application/json')

        self.assertEqual(401, response.status_code)
        self.assertEqual(response.json(), {
            'errors': {
                'creator': ['You must log in to create a matchup.']
            }
        })

    def test_400_for_bad_attempt_to_create_featured_matchup(self):
        response = self.client.post('/matchups/', json.dumps({
            'title': 'foo vs bar',
            'movies': ['foo', 'bar'],
            'featured': True
        }), content_type='application/json')

        self.assertEqual(400, response.status_code)
        self.assertEqual(response.json(), {
            'errors': {
                'featured': ['You must be a featured contributor to create '
                             'featured matchups.']
            }
        })

    def test_400_for_invalid_movie_ids(self):
        response = self.client.post('/matchups/', json.dumps({
            'title': 'foo vs quux',
            'movies': ['foo', 'quux']
        }), content_type='application/json')

        self.assertEqual(400, response.status_code)
        self.assertEqual(response.json(), {
            'errors': {
                'movies': ["One or more of those movies isn't recognized."]
            }
        })

    def test_featured_contributor(self):
        self.user.is_staff = True
        self.user.save()

        response = self.client.post('/matchups/', json.dumps({
            'title': 'foo vs bar',
            'movies': ['foo', 'bar'],
            'featured': True
        }), content_type='application/json')

        self.assertEqual(201, response.status_code)
        self.assertEqual(True, response.json()['featured'])

    def test_featured_contributor_custom_backend(self):
        with override_settings(
                USER_BACKEND='bomojo.tests.backends.FeatureBobBackend'):
            # Our default user (joe) should not be able to create a featured
            # matchup.
            response = self.client.post('/matchups/', json.dumps({
                'title': 'foo vs bar',
                'movies': ['foo', 'bar'],
                'featured': True
            }), content_type='application/json')

            self.assertEqual(400, response.status_code)

            # However, a user named "bob" should be, based on our custom
            # FeatureBobBackend class.
            bob = self.create_user('bob')
            self.client.force_login(bob)
            response = self.client.post('/matchups/', json.dumps({
                'title': 'foo vs bar',
                'movies': ['foo', 'bar'],
                'featured': True
            }), content_type='application/json')

            self.assertEqual(201, response.status_code)


class ShowTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_movie('Foo')
        cls.create_movie('Bar')

    @freeze_time('2018-03-10 22:17:00')
    def test_happy_path(self):
        user = self.create_user('joe')
        image = self.create_image('foo-vs-bar.png')
        self.create_matchup(user, ['foo', 'bar'], image=image)

        response = self.client.get('/matchups/foo-vs-bar')
        self.assertEqual(response.json(), {
            'creator': {
                'username': 'joe',
                'avatar': get_avatar_url(user.email)
            },
            'slug': 'foo-vs-bar',
            'title': 'foo vs bar',
            'image_url': '/media/matchups/foo-vs-bar.png',
            'description': 'matchup between foo and bar',
            'movies': [
                {
                    'title': 'Foo',
                    'movie_id': 'foo'
                },
                {
                    'title': 'Bar',
                    'movie_id': 'bar'
                }
            ],
            'period': '30d',
            'featured': False,
            'created': '2018-03-10T22:17:00+00:00',
            'updated': '2018-03-10T22:17:00+00:00'
        })

    def test_404_for_missing_matchup(self):
        response = self.client.get('/matchups/does-not-exist')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {
            'errors': {
                'slug': ['That matchup does not exist.']
            }
        })


class UpdateTestCase(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.create_movie('Foo')
        cls.create_movie('Bar')

    def test_happy_path(self):
        user = self.create_user('joe')

        with freeze_time('2018-04-28 16:14:00'):
            self.create_matchup(user, ['foo', 'bar'])

        self.client.force_login(user)
        with freeze_time('2018-04-28 16:14:01'):
            response = self.client.put('/matchups/foo-vs-bar', json.dumps({
                'title': 'updated title',
                'description': 'updated description'
            }), content_type='application/json')

        self.assertEqual(200, response.status_code)
        self.assertEqual(response.json(), {
            'creator': {
                'username': 'joe',
                'avatar': get_avatar_url(user.email)
            },
            'slug': 'foo-vs-bar',
            'title': 'updated title',
            'image_url': None,
            'description': 'updated description',
            'movies': [
                {
                    'title': 'Foo',
                    'movie_id': 'foo'
                },
                {
                    'title': 'Bar',
                    'movie_id': 'bar'
                }
            ],
            'period': '30d',
            'featured': False,
            'created': '2018-04-28T16:14:00+00:00',
            'updated': '2018-04-28T16:14:01+00:00'
        })

    def test_404_for_missing_matchup(self):
        user = self.create_user('joe')

        self.client.force_login(user)
        response = self.client.put('/matchups/foo-vs-bar', json.dumps({
            'title': 'updated title',
            'description': 'updated description'
        }), content_type='application/json')

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json(), {
            'errors': {
                'slug': ['That matchup does not exist.']
            }
        })

    def test_401_for_unauthenticated_attempt(self):
        user = self.create_user('joe')
        self.create_matchup(user, ['foo', 'bar'])

        response = self.client.put('/matchups/foo-vs-bar', json.dumps({
            'title': 'updated title',
            'description': 'updated description'
        }), content_type='application/json')

        self.assertEqual(401, response.status_code)
        self.assertEqual(response.json(), {
            'errors': {
                'creator': ['You must log in to edit your matchups.']
            }
        })

    def test_403_for_unauthorized_attempt(self):
        bob = self.create_user('bob')
        self.create_matchup(bob, ['foo', 'bar'])

        alice = self.create_user('alice')

        self.client.force_login(alice)
        response = self.client.put('/matchups/foo-vs-bar', json.dumps({
            'title': 'updated title',
            'description': 'updated description'
        }), content_type='application/json')

        self.assertEqual(403, response.status_code)
        self.assertEqual(response.json(), {
            'errors': {
                'creator': ["You cannot edit other people's matchups."]
            }
        })

    def test_400_for_bad_attempt_to_update_featured_matchup(self):
        user = self.create_user('joe')
        self.create_matchup(user, ['foo', 'bar'])

        self.client.force_login(user)
        response = self.client.put('/matchups/foo-vs-bar', json.dumps({
            'title': 'updated title',
            'description': 'updated description',
            'featured': True
        }), content_type='application/json')

        self.assertEqual(400, response.status_code)
        self.assertEqual(response.json(), {
            'errors': {
                'featured': ['You must be a featured contributor to create '
                             'featured matchups.']
            }
        })

    def test_400_for_invalid_movie_ids(self):
        user = self.create_user('joe')
        self.create_matchup(user, ['foo', 'bar'])

        self.client.force_login(user)
        response = self.client.put('/matchups/foo-vs-bar', json.dumps({
            'title': 'updated title',
            'description': 'updated description',
            'movies': ['foo', 'bar', 'quux']
        }), content_type='application/json')

        self.assertEqual(400, response.status_code)
        self.assertEqual(response.json(), {
            'errors': {
                'movies': ["One or more of those movies isn't recognized."]
            }
        })

    def test_featured_contributor(self):
        user = self.create_user('joe', is_staff=True)
        self.create_matchup(user, ['foo', 'bar'])

        self.client.force_login(user)
        response = self.client.put('/matchups/foo-vs-bar', json.dumps({
            'title': 'updated title',
            'description': 'updated description',
            'featured': True
        }), content_type='application/json')

        self.assertEqual(200, response.status_code)
        self.assertEqual(True, response.json()['featured'])

    def test_featured_contributor_custom_backend(self):
        user = self.create_user('joe', is_staff=True)
        self.create_matchup(user, ['foo', 'bar'])

        self.client.force_login(user)

        with override_settings(
                USER_BACKEND='bomojo.tests.backends.FeatureBobBackend'):
            # Our default user (joe) should not be able to make a matchup
            # featured.
            response = self.client.put('/matchups/foo-vs-bar', json.dumps({
                'title': 'updated title',
                'description': 'updated description',
                'featured': True
            }), content_type='application/json')

            self.assertEqual(400, response.status_code)

            user.username = 'bob'
            user.save()

            # However, after changing their name to "bob" they should be,
            # based on our custom FeatureBobBackend class.
            response = self.client.put('/matchups/foo-vs-bar', json.dumps({
                'title': 'updated title',
                'description': 'updated description',
                'featured': True
            }), content_type='application/json')

            self.assertEqual(200, response.status_code)


class ListTestCase(TestCase):
    def test_featured_matchups(self):
        user = self.create_user('joe')
        avatar_url = get_avatar_url(user.email)

        with freeze_time('2018-03-10 22:17:00'):
            self.create_matchup(user, ['foo', 'bar'])

        with freeze_time('2018-03-10 22:17:01'):
            self.create_matchup(user, ['foo1', 'foo2', 'foo3'],
                           title='foo trilogy',
                           description='all three foo movies')

        # Initially, no matchups should be returned since none are featured.
        response = self.client.get('/matchups/?featured=true')
        self.assertEqual(response.json(), [])

        Matchup.objects.all().update(featured=True)

        # Now that they're featured, both matchups should be returned.
        response = self.client.get('/matchups/?featured=true')
        self.assertEqual(response.json(), [
            {
                'creator': {
                    'username': 'joe',
                    'avatar': avatar_url
                },
                'slug': 'foo-trilogy',
                'title': 'foo trilogy',
                'image_url': None,
                'description': 'all three foo movies',
                'period': '30d',
                'featured': True,
                'created': '2018-03-10T22:17:01+00:00',
                'updated': '2018-03-10T22:17:01+00:00'
            },
            {
                'creator': {
                    'username': 'joe',
                    'avatar': avatar_url
                },
                'slug': 'foo-vs-bar',
                'title': 'foo vs bar',
                'image_url': None,
                'description': 'matchup between foo and bar',
                'period': '30d',
                'featured': True,
                'created': '2018-03-10T22:17:00+00:00',
                'updated': '2018-03-10T22:17:00+00:00'
            }
        ])

    def test_my_matchups(self):
        bob = self.create_user('bob')
        avatar_url = get_avatar_url(bob.email)

        with freeze_time('2018-04-30 06:47:00'):
            self.create_matchup(bob, ['foo', 'bar'])

        with freeze_time('2018-04-30 06:47:01'):
            self.create_matchup(bob, ['foo1', 'foo2', 'foo3'],
                           title='foo trilogy',
                           description='all three foo movies',
                           featured=True)

        alice = self.create_user('alice')
        self.create_matchup(alice, ['bar', 'baz'], featured=True)

        # Requesting the matchups resource should return the current user's
        # matchups. This means an empty list for an anonymous request.
        response = self.client.get('/matchups/')
        self.assertEqual(200, response.status_code)
        self.assertEqual([], response.json())

        self.client.force_login(bob)
        response = self.client.get('/matchups/')
        self.assertEqual(200, response.status_code)

        # Bob's matchups should not include Alice's matchup, even though it's
        # featured.
        self.assertEqual(response.json(), [
            {
                'creator': {
                    'username': 'bob',
                    'avatar': avatar_url
                },
                'slug': 'foo-trilogy',
                'title': 'foo trilogy',
                'image_url': None,
                'description': 'all three foo movies',
                'period': '30d',
                'featured': True,
                'created': '2018-04-30T06:47:01+00:00',
                'updated': '2018-04-30T06:47:01+00:00'
            },
            {
                'creator': {
                    'username': 'bob',
                    'avatar': avatar_url
                },
                'slug': 'foo-vs-bar',
                'title': 'foo vs bar',
                'image_url': None,
                'description': 'matchup between foo and bar',
                'period': '30d',
                'featured': False,
                'created': '2018-04-30T06:47:00+00:00',
                'updated': '2018-04-30T06:47:00+00:00'
            }
        ])

    def test_matchup_sorting(self):
        user = self.create_user('joe')

        with freeze_time('2018-05-04 19:32:00'):
            matchup1 = self.create_matchup(user, ['foo', 'bar'])

        with freeze_time('2018-05-04 19:32:01'):
            matchup2 = self.create_matchup(user, ['bar', 'baz'])

        with freeze_time('2018-05-05 19:32:00'):
            matchup2.description = 'updated matchup #2'
            matchup2.save()

        with freeze_time('2018-05-05 19:32:01'):
            matchup1.description = 'updated matchup #1'
            matchup1.save()

        self.client.force_login(user)

        def expect_results_from_sort(sort, expected_matchups):
            response = self.client.get(f'/matchups/?sort={sort}')
            self.assertEqual(200, response.status_code)
            self.assertEqual([m.slug for m in expected_matchups],
                             [m['slug'] for m in response.json()])

        expect_results_from_sort('created_on', [matchup1, matchup2])
        expect_results_from_sort('-created_on', [matchup2, matchup1])
        expect_results_from_sort('updated_on', [matchup2, matchup1])
        expect_results_from_sort('-updated_on', [matchup1, matchup2])

        response = self.client.get(f'/matchups/?sort=description')
        self.assertEqual(400, response.status_code)
        self.assertEqual(response.json(), {
            'errors': {
                'sort': ['You can only sort by created_on or updated_on.']
            }
        })

    @override_settings(DEFAULT_MATCHUP_SORTING='created_on')
    def test_default_matchup_sorting(self):
        user = self.create_user('joe')

        with freeze_time('2018-05-04 19:32:00'):
            matchup1 = self.create_matchup(user, ['foo', 'bar'])

        with freeze_time('2018-05-04 19:32:01'):
            matchup2 = self.create_matchup(user, ['bar', 'baz'])

        self.client.force_login(user)

        response = self.client.get('/matchups/')
        self.assertEqual(200, response.status_code)
        self.assertEqual([matchup1.slug, matchup2.slug],
                         [m['slug'] for m in response.json()])
