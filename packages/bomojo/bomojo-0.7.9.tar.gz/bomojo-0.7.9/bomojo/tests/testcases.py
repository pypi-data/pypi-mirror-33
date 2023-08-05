import os

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase as DjangoTestCase

from bomojo.backends import get_movie_backend

TEST_DATA_DIR = os.path.join(settings.BASE_DIR, 'tests', 'data')


class TestCase(DjangoTestCase):
    @staticmethod
    def create_user(username, **kwargs):
        from django.contrib.auth.models import User

        user_data = {
            'username': username,
            'first_name': username.capitalize(),
            'email': f'{username}@example.com'
        }

        password = kwargs.pop('password', 'top secret')

        user_data.update(kwargs)

        user = User(**user_data)
        user.set_password(password)
        user.save()

        return user

    @staticmethod
    def create_movie(title, **kwargs):
        from bomojo.movies.models import Movie

        backend = kwargs.pop('backend', None) or get_movie_backend()

        movie_data = {
            'title': title,
            'external_id': backend.parse_movie_id(title.lower())
        }

        movie_data.update(kwargs)

        return Movie.objects.create(**movie_data)

    @staticmethod
    def create_matchup(user, movies, **kwargs):
        from bomojo.matchups.models import Matchup

        backend = kwargs.pop('backend', None) or get_movie_backend()

        matchup_data = {
            'user': user,
            'title': ' vs '.join(movies),
            'description': 'matchup between %s' % ' and '.join(movies),
            'movies': [backend.parse_movie_id(movie_id)
                       for movie_id in movies],
            'period': '30d'
        }

        matchup_data.update(kwargs)

        return Matchup.objects.create(**matchup_data)

    def create_image(self, name, file='baby.png'):
        with open(os.path.join(TEST_DATA_DIR, file), 'rb') as f:
            content = f.read()

        image = SimpleUploadedFile(name=name,
                                   content=content,
                                   content_type='image/png')

        self.addCleanup(lambda: os.remove(
            os.path.join(TEST_DATA_DIR, 'matchups', image.name)))

        return image
