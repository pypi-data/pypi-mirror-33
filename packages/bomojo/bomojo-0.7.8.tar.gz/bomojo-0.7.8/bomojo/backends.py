from django.utils.module_loading import import_string

from bomojo.utils import get_setting


class AbstractUserBackend(object):
    """Abstract class defining required methods for any USER_BACKEND class"""
    def is_featured_contributor(self, user):
        """Indicate whether a user is allowed to make "featured" matchups"""
        raise NotImplementedError


class DefaultUserBackend(AbstractUserBackend):
    def is_featured_contributor(self, user):
        return user.is_staff


def get_user_backend():
    backend_name = get_setting('USER_BACKEND')
    backend_class = import_string(backend_name)
    return backend_class()


class AbstractMovieBackend(object):
    """Abstract class defining required methods for any MOVIE_BACKEND class

    Any movie backend needs to be able to perform lossless two-way conversions
    between external IDs provided by a service and values rendered to the end
    user. The idea is that a service may provide "ugly" IDs that shouldn't be
    rendered as-is, in which case the backend still needs to be able to produce
    the "ugly" ID from a formatted ID for requests back to the service.
    """
    def format_external_id(self, external_id):
        """Translate an external ID to something suitable for display"""
        raise NotImplementedError

    def parse_movie_id(self, movie_id):
        """Resolve an ID to a value recognized by an external service"""
        raise NotImplementedError


class DefaultMovieBackend(AbstractMovieBackend):
    def format_external_id(self, external_id):
        if external_id.endswith('.htm'):
            external_id = external_id[:-4]
        return external_id

    def parse_movie_id(self, movie_id):
        if not movie_id.endswith('.htm'):
            movie_id = f'{movie_id}.htm'
        return movie_id


def get_movie_backend():
    backend_name = get_setting('MOVIE_BACKEND')
    backend_class = import_string(backend_name)
    return backend_class()
