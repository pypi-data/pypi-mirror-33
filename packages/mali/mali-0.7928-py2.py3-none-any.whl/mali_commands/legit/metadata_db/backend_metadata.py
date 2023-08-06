# -*- coding: utf8 -*-
import io
import json

import logging
import os
import sys
from contextlib import contextmanager

import requests
import six

from ..scam import QueryParser
from ..api import default_api_retry
from ..backend_mixin import BackendMixin
from .base_metadata_db import BaseMetadataDB, MetadataOperationError
from six.moves.urllib.parse import urlencode


class WrapUnicodePy2(object):
    def __init__(self, fp):
        self.__fp = fp

    def write(self, s):
        return self.__fp.write(s)

    def seek_to_beginning(self):
        return self.__fp.seek(0)


class WrapUnicodePy3(object):
    def __init__(self, fp):
        self.__fp = fp

    def write(self, s):
        return self.__fp.write(s.encode('utf8'))

    def seek_to_beginning(self):
        return self.__fp.seek(0)


class _StreamArray(list):
    def __init__(self, total_rows):
        super(_StreamArray, self).__init__()
        self._stream = None
        self._total_rows = total_rows

    def __iter__(self):
        return self._csv_enum(self._stream)

    # according to the comment below
    def __len__(self):
        return self._total_rows

    @classmethod
    def _csv_enum(cls, stream):
        import csv

        reader = csv.DictReader(stream)
        replace_names = {'_sha': 'path', '_hash': 'id', '_commit_sha': 'version'}
        for row in reader:
            row_params = {}
            meta = {}
            for key, val in row.items():
                if val == '':
                    continue

                is_meta = key.startswith('_')
                if is_meta:
                    key = replace_names.get(key, key[1:])
                    row_params[key] = val
                    continue

                meta[key] = val

            if meta:
                row_params['meta'] = meta

            yield row_params


class _StreamArrayFromUrl(_StreamArray):
    def __init__(self, total_rows, result_url):
        super(_StreamArrayFromUrl, self).__init__(total_rows)
        r = requests.get(result_url, stream=True)  # allowed to use requests

        if r.encoding is None:
            r.encoding = 'utf-8'

        self._stream = r.iter_lines(decode_unicode=True)


class _CachedSessionWrapper(object):
    def __init__(self, session, cache_folder_full_path):
        from requests_cache import CachedSession

        self.__session = session
        self._first_request = None
        self.__cached_session = CachedSession(cache_folder_full_path)  # used as utility to store requests
        self.__wrap_cached_session_send(self.__session)

    @classmethod
    def convert_result_to_response(cls, result_url, total_rows, total_size, explicit_query):
        response_data = {
            'ok': True,
            'total_data_points': total_rows,
            'total_size': total_size,
            'explicit_query': explicit_query,
            'data_points': _StreamArrayFromUrl(total_rows, result_url)
        }

        raw_bytes = io.BytesIO()
        wrap_unicode_class = WrapUnicodePy2 if six.PY2 else WrapUnicodePy3
        raw_string = wrap_unicode_class(raw_bytes)
        json.dump(response_data, raw_string)
        raw_string.seek_to_beginning()

        response = requests.Response()
        response.raw = raw_bytes
        response.status_code = 200

        return response

    def store_response(self, response):
        response.request = self._first_request
        cache_key = self.__cached_session.cache.create_key(self._first_request)
        self.__cached_session.cache.save_response(cache_key, response)

    # the first request is the "real" requests (the next are async response check)
    # we store only the first request, check if there is a cached response attached to it
    # in case there is a cached response we send using the cached session class in case it needs to further
    # handle the cache entry
    def __handle_first_request(self, request):
        if self._first_request is not None:
            return None

        self._first_request = request

        cache_key = self.__cached_session.cache.create_key(self._first_request)

        response, timestamp = self.__cached_session.cache.get_response_and_time(cache_key)

        return response

    def __wrap_cached_session_send(self, session):
        prev_session_send = session.send

        def wrapped_send(request, **kwargs):
            session.send = prev_session_send
            response = self.__handle_first_request(request)
            if response is not None:
                return response

            return prev_session_send(request, **kwargs)

        session.send = wrapped_send


class BackendMetadataDB(BackendMixin, BaseMetadataDB):
    max_query_retry = 3
    default_cache_file_name = 'missinglink_query_v' + str(sys.version_info[0])

    def __init__(self, connection, config, session, handle_api, cache_folder=None):
        super(BackendMetadataDB, self).__init__(connection, config, session, handle_api)
        self.__query_parser = QueryParser()

        if cache_folder:
            self.__cache_folder_full_path = os.path.join(cache_folder, self.default_cache_file_name)
        else:
            self.__cache_folder_full_path = self.default_cache_file_name

    def _create_table(self):
        pass

    def _query_head_data(self, sha_list):
        with self._connection.get_cursor() as session:
            url = 'data_volumes/%s/metadata/head' % self._volume_id
            msg = {
                'sha': sha_list,
            }

            result = self._handle_api(
                self._config, session, 'post', url, msg,
                retry=default_api_retry(stop_max_attempt_number=self.max_query_retry))

            for data_item in result.get('metadata_json') or []:
                yield json.loads(data_item)

    def _add_missing_columns(self, data_object):
        pass

    def get_data_for_commit(self, sha, commit_sha):
        raise NotImplementedError(self.get_data_for_commit)

    def _add_data(self, data):
        pass

    def add_data_using_url(self, metadata_url, isolation_token):
        if not metadata_url:
            logging.debug('no data provided')
            return

        logging.debug('add data %s', metadata_url)

        with self._connection.get_cursor() as session:
            url = 'data_volumes/%s/metadata/head/add' % self._volume_id

            msg = {
                'metadata_url': metadata_url,
                'isolation_token': isolation_token,
            }

            return self._handle_api(self._config, session, 'post', url, msg, retry=default_api_retry(), async=True)

    @classmethod
    def _create_iter_data(cls, result):
        def handle_meta_item(val, data_point, result_data_point):
            if isinstance(val, dict):
                result_data_point['meta'] = val
                return

            meta = result_data_point.setdefault('meta', {})
            for meta_key_val in data_point['meta']:
                meta[meta_key_val['key']] = meta_key_val.get('val')

        def _iter_data():
            for data_point in result.get('data_points') or []:
                result_data_point = {}

                for key, val in data_point.items():
                    if key == 'meta':
                        handle_meta_item(val, data_point, result_data_point)
                    else:
                        result_data_point[key] = val

                yield result_data_point

        return _iter_data()

    def __is_stable_query(self, query_text):
        from ..scam import visit_query
        from .version_visitor import VersionVisitor

        tree = self.__query_parser.parse_query(query_text)

        version_visitor = VersionVisitor()
        visit_query(version_visitor, tree)

        is_stable_version = version_visitor.version not in ['head', 'staging']

        return is_stable_version

    def query(self, query_text, **kwargs):
        version_query = query_text if query_text else '@version:head'

        async = kwargs.pop('async', False)

        is_stable_version = self.__is_stable_query(query_text)

        if is_stable_version:
            session_wrapper = _CachedSessionWrapper(self._session, self.__cache_folder_full_path)
        else:
            logging.info('not a stable query, caching cannot be used')
            session_wrapper = None

        params = {
            'query': version_query
        }

        for key, val in kwargs.items():
            if val is None:
                continue

            params[key] = val

        url = 'data_volumes/%s/query/?%s' % (self._volume_id, urlencode(params))

        result = self._handle_api(
            self._config, self._session, 'get', url, retry=default_api_retry(stop_max_attempt_number=self.max_query_retry), async=async)

        is_live_async_response = async and isinstance(result, (list, tuple))
        if is_live_async_response:
            result_url, total_rows, total_size, explicit_query = result

            response = _CachedSessionWrapper.convert_result_to_response(result_url, total_rows, total_size, explicit_query)

            if session_wrapper is not None:
                session_wrapper.store_response(response)

            result = response.json()
        elif not result['ok']:
            raise MetadataOperationError(result['error'])

        return self._create_iter_data(result), int(result.get('total_data_points', 0)), int(result.get('total_size', 0))

    def _query(self, sql_vars, select_fields, where, **kwargs):
        raise NotImplementedError(self._query)

    def get_all_data(self, sha):
        raise NotImplementedError(self.get_all_data)

    def end_commit(self):
        raise NotImplementedError(self.end_commit)

    def begin_commit(self, commit_sha, tree_id, ts):
        raise NotImplementedError(self.begin_commit)
