from django.conf.urls import url

from bomojo.matchups.views import MatchupView, MatchupsView

urlpatterns = [
    url(r'^$', MatchupsView.as_view(), name='matchups'),
    url(r'^(?P<slug>[^/]+)$', MatchupView.as_view(), name='matchup'),
]
