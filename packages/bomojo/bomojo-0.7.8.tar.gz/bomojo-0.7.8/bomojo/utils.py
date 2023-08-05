from collections import OrderedDict
import hashlib

from django.conf import settings

from bomojo import defaults


def get_avatar_url(email, size=None, default=None):
    email = email.lower()
    size = size or get_setting('DEFAULT_AVATAR_SIZE')
    default = default or get_setting('DEFAULT_AVATAR_STYLE')

    digest = hashlib.new('md5', email.encode('utf-8')).hexdigest()
    return 'https://gravatar.com/avatar/%(digest)s?size=%(size)d&d=%(default)s' % {
        'digest': digest,
        'size': size,
        'default': default
    }


def get_setting(setting_name):
    return getattr(settings, setting_name, getattr(defaults, setting_name))


def deduplicate(values):
    """Returns a list of the same values but with duplicates removed

    Unlike list(set(values)), this function preserves the ordering of the
    original list.
    """
    return list(OrderedDict.fromkeys(values))
