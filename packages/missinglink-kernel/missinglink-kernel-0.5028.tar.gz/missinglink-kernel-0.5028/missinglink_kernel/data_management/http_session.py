# -*- coding: utf8 -*-
from missinglink import get_version


def create_http_session():
    import requests

    session = requests.session()

    session.headers.update({'User-Agent': 'ml-sdk/{}'.format(get_version())})

    return session
