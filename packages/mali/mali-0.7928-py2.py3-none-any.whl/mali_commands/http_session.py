# -*- coding: utf8 -*-
from mali_commands.mali_version import get_mali_version


def create_http_session():
    import requests

    session = requests.session()

    session.headers.update({'User-Agent': 'mali/{}'.format(get_mali_version())})

    return session
