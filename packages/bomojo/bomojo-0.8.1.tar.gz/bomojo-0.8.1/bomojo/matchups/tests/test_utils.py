from django.test import override_settings

from bomojo.utils import get_avatar_url


def test_get_avatar_url():
    assert (get_avatar_url('daniel.tao@gmail.com') ==
        'https://gravatar.com/avatar/3c9c19ca551799cf691fddaae5056e55?size=32&d=retro')


def test_get_avatar_url_custom_size():
    assert (get_avatar_url('daniel.tao@gmail.com', size=64) ==
        'https://gravatar.com/avatar/3c9c19ca551799cf691fddaae5056e55?size=64&d=retro')


def test_get_avatar_url_custom_default():
    assert (get_avatar_url('daniel.tao@gmail.com', default='identicon') ==
        'https://gravatar.com/avatar/3c9c19ca551799cf691fddaae5056e55?size=32&d=identicon')


@override_settings(DEFAULT_AVATAR_SIZE=48, DEFAULT_AVATAR_STYLE='robohash')
def test_get_avatar_url_uses_django_settings():
    assert (get_avatar_url('daniel.tao@gmail.com') ==
        'https://gravatar.com/avatar/3c9c19ca551799cf691fddaae5056e55?size=48&d=robohash')


@override_settings(DEFAULT_AVATAR_SIZE=48, DEFAULT_AVATAR_STYLE='robohash')
def test_get_avatar_url_parameters_override_settings():
    assert (get_avatar_url('daniel.tao@gmail.com', size=64, default='identicon') ==
        'https://gravatar.com/avatar/3c9c19ca551799cf691fddaae5056e55?size=64&d=identicon')
