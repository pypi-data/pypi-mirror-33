# -*- coding: utf8 -*-
import collections
import json
import logging
import sys

import time
from requests import HTTPError
from six.moves.urllib import parse

from .eprint import eprint
from .config import get_prefix_section, Config

BASE_URL_PATH = '_ah/api/missinglink/v1/'


def __urljoin(*args):
    base = args[0]
    for u in args[1:]:
        base = parse.urljoin(base, u)

    return base


def __refresh_token_id_token(config, http_session):
    try:
        id_token = update_token(config, http_session)
    except HTTPError:
        eprint('Authorization failed, try running "mali auth init" again')
        sys.exit(1)

    return id_token


def __api_call(config, http_session, http_method_name, url, data):
    id_token = config.id_token if config.id_token else __refresh_token_id_token(config, http_session)

    for _ in range(3):
        headers = {'Authorization': 'Bearer {}'.format(id_token)}
        http_method_exec = getattr(http_session, http_method_name)
        r = http_method_exec(url, headers=headers, json=data)
        if r.status_code == 401:
            id_token = __refresh_token_id_token(config, http_session)
            continue

        r.raise_for_status()
        return r.json()

    eprint('failed to refresh the token, rerun auth init again')
    sys.exit(1)


def add_url_params(url, **params):
    try:
        from urllib import urlencode, unquote
        from urlparse import urlparse, parse_qsl, ParseResult
    except ImportError:
        # Python 3 fallback
        from urllib.parse import (
            urlencode, unquote, urlparse, parse_qsl, ParseResult
        )

    """ Add GET params to provided URL being aware of existing.

    :param url: string of target URL
    :param params: dict containing requested params to be added
    :return: string with updated URL

    >> url = 'http://stackoverflow.com/test?answers=true'
    >> new_params = {'answers': False, 'data': ['some','values']}
    >> add_url_params(url, new_params)
    'http://stackoverflow.com/test?data=some&data=values&answers=false'
    """
    # Unquoting URL first so we don't loose existing args
    url = unquote(url)
    # Extracting url info
    parsed_url = urlparse(url)
    # Extracting URL arguments from parsed URL
    get_args = parsed_url.query
    # Converting URL arguments to dict
    parsed_get_args = dict(parse_qsl(get_args))
    # Merging URL arguments dict with new params
    parsed_get_args.update(params)

    parsed_get_args = collections.OrderedDict(sorted(parsed_get_args.items()))

    # Bool and Dict values should be converted to json-friendly values
    # you may throw this part away if you don't like it :)
    parsed_get_args.update(
        {k: json.dumps(v) for k, v in parsed_get_args.items()
         if isinstance(v, (bool, dict))}
    )

    # Converting URL argument to proper query string
    encoded_get_args = urlencode(parsed_get_args, doseq=True)
    # Creating new parsed result object based on provided with new
    # URL arguments. Same thing happens inside of urlparse.
    new_url = ParseResult(
        parsed_url.scheme, parsed_url.netloc, parsed_url.path,
        parsed_url.params, encoded_get_args, parsed_url.fragment
    ).geturl()

    return new_url


def _handle_async_api(config, http_session, http_method_name, method_url, data, retry):
    if data is not None:
        data['async'] = True
    else:
        method_url = add_url_params(method_url, async=True)

    retry = retry or default_api_retry()
    result = _handle_sync_api(config, http_session, http_method_name, method_url, data, retry)

    if 'token' not in result:
        return result

    token = result['token']

    while True:
        result = _handle_sync_api(config, http_session, 'get', 'data_volumes/tasks/' + token)
        if result.get('failed'):
            raise Exception('Internal Server Error %s' % json.dumps(result))

        if result.get('finished'):
            return json.loads(result['results']) if 'results' in result else None

        time.sleep(2.0)


def _handle_sync_api(config, http_session, http_method_name, method_url, data=None, retry=None):
    import requests

    if config.refresh_token is None:
        eprint('Please run: "mali auth init" to setup authorization')
        sys.exit(1)

    url = __urljoin(config.api_host, BASE_URL_PATH, method_url)

    def api_call_with_retry(*args, **kwargs):
        return retry.call(__api_call, *args, **kwargs)

    f = __api_call if retry is None else api_call_with_retry

    try:
        return f(config, http_session, http_method_name, url, data)
    except requests.exceptions.HTTPError as ex:
        try:
            error_message = ex.response.json().get('error', {}).get('message')
        except ValueError:
            error_message = None

        if error_message is None:
            error_message = str(ex)

        eprint('\n' + error_message)
        sys.exit(1)


def handle_api(ctx_or_config, http_session, http_method_name, method_url, data=None, retry=None, async=False):
    config = ctx_or_config if isinstance(ctx_or_config, Config) else ctx_or_config.config

    if async:
        return _handle_async_api(config, http_session, http_method_name, method_url, data, retry)

    return _handle_sync_api(config, http_session, http_method_name, method_url, data, retry)


def _should_retry_ml_auth(exception):
    import requests

    logging.debug('got retry exception (ml auth) %s', exception)

    error_codes_to_retries = [
        429,  # Too many requests
    ]

    return isinstance(exception, requests.exceptions.HTTPError) and exception.response.status_code in error_codes_to_retries


def update_token(config, http_session):
    from retrying import retry

    @retry(retry_on_exception=_should_retry_ml_auth)
    def with_retry():
        url = __urljoin(config.api_host, BASE_URL_PATH, 'users/refresh_token')

        r = http_session.post(
            url,
            json={
                'refresh_token': config.refresh_token,
            })

        r.raise_for_status()

        data = r.json()

        section = get_prefix_section(config.config_prefix, 'token')
        config.set(section, 'id_token', data['id_token'])
        config.save()

        return data['id_token']

    return with_retry()


def default_api_retry(stop_max_attempt_number=None):
    from retrying import Retrying

    def retry_if_retry_possible_error(exception):
        logging.debug('got retry exception (api) %s', exception)

        return True

    return Retrying(
        retry_on_exception=retry_if_retry_possible_error,
        wait_exponential_multiplier=50,
        wait_exponential_max=5000,
        stop_max_attempt_number=stop_max_attempt_number)
