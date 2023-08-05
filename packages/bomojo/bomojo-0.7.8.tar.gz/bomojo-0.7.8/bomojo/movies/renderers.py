from bomojo.backends import get_movie_backend


def render_movie(movie, backend=None):
    backend = backend or get_movie_backend()

    return {
        'title': movie.title,
        'movie_id': backend.format_external_id(movie.external_id)
    }


def render_box_office(box_office, movie_id):
    return {
        'title': box_office.get('title'),
        'movie_id': movie_id,
        'href': box_office.get('href'),
        'box_office': box_office.get('box_office')
    }
