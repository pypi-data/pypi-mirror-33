"""
bomojo test backends

This module exists to provide example custom backends, to test the library's
support for customizing certain behavior.
"""

from bomojo.backends import AbstractMovieBackend, AbstractUserBackend


class FeatureBobBackend(AbstractUserBackend):
    def is_featured_contributor(self, user):
        return user.username == 'bob'


class UpperToLowerMovieBackend(AbstractMovieBackend):
    def format_external_id(self, external_id):
        return external_id.lower()

    def parse_movie_id(self, movie_id):
        return movie_id.upper()
