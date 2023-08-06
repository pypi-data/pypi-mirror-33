from bomojo.movies.renderers import render_movie
from bomojo.utils import get_avatar_url


def render_matchup(matchup, include_movies=True):
    result = {
        'creator': render_user(matchup.user),
        'slug': matchup.slug,
        'title': matchup.title,
        'image_url': matchup.image.url if matchup.image else None,
        'description': matchup.description,
        'period': matchup.period,
        'featured': matchup.featured,
        'created': matchup.created_on.isoformat(),
        'updated': matchup.updated_on.isoformat()
    }

    if include_movies:
        result['movies'] = [render_movie(movie) for movie
                            in matchup.get_movies()]

    return result


def render_user(user):
    return {
        'username': user.username,
        'avatar': get_avatar_url(user.email)
    }
