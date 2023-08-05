# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.exceptions import ValidationError
from django.forms import ModelForm

from bomojo.backends import get_movie_backend, get_user_backend
from bomojo.matchups.models import Matchup
from bomojo.movies.models import Movie
from bomojo.utils import deduplicate


class MatchupForm(ModelForm):
    class Meta:
        model = Matchup
        fields = ['title', 'description', 'movies', 'period', 'featured']

    def __init__(self, request, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.instance.user = request.user

    def clean_featured(self):
        if self.cleaned_data['featured']:
            user_backend = get_user_backend()
            if not user_backend.is_featured_contributor(self.instance.user):
                raise ValidationError('You must be a featured contributor to '
                                      'create featured matchups.',
                                      code='not_featured_contributor')
        return self.cleaned_data['featured']

    def clean_movies(self):
        movie_ids = deduplicate(self.cleaned_data['movies'])
        backend = get_movie_backend()
        movie_ids = [backend.parse_movie_id(movie_id)
                     for movie_id in movie_ids]
        movies = Movie.objects.filter(external_id__in=movie_ids)
        if len(movies) != len(movie_ids):
            raise ValidationError("One or more of those movies isn't "
                                  "recognized.")
        return movie_ids
