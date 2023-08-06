from django.conf.urls import url

from bomojo.movies import views

urlpatterns = [
    url(r'^search', views.search, name='search'),
    url(r'^(?P<movie_id>[^/]+)/boxoffice', views.box_office, name='box-office'),
]
