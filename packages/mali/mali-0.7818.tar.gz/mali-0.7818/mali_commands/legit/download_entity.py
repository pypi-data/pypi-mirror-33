# -*- coding: utf8 -*-
import json
import threading
from contextlib import closing
import requests
import importlib
from .config import Config
from .data_volume import with_repo
from .eprint import eprint
from .exceptions import AccessDenied, NotFound


class DownloadEntity(object):
    local_data = threading.local()

    @classmethod
    def __object_from_data(cls, data, creator):
        data_key = json.dumps(data, sort_keys=True)

        try:
            return cls.local_data.__data_sync_objects[data_key]
        except KeyError:
            cls.local_data.__data_sync_objects[data_key] = creator(data)
        except AttributeError:
            cls.local_data.__data_sync_objects = {data_key: creator(data)}

        return cls.local_data.__data_sync_objects[data_key]

    @classmethod
    def _import_storage(cls, storage_class):
        module_name, class_name = storage_class.rsplit('.', 1)
        m = importlib.import_module(module_name)
        return getattr(m, class_name)

    @classmethod
    def _get_storage(cls, current_data):
        return cls._import_storage(current_data['class']).init_from_config(**current_data)

    @classmethod
    def _get_config(cls, current_data):
        return Config(**current_data)

    @classmethod
    def _get_item_data(cls, repo, storage, metadata):
        if storage.has_item(metadata):
            return

        try:
            _, current_data = repo.object_store.get_raw(metadata)
            return current_data
        except (AccessDenied, NotFound) as ex:
            eprint(ex)
            return
        except requests.exceptions.HTTPError as ex:
            if ex.response.status_code == 404:
                return

            raise

    @classmethod
    def download(cls, config_init_dict, volume_id, metadata, headers):
        config = cls.__object_from_data(config_init_dict, cls._get_config)

        storage_config = config.items('storage')

        storage = cls.__object_from_data(storage_config, cls._get_storage)

        session = requests.session()
        session.headers.update(headers)

        with with_repo(config, volume_id, read_only=True, session=session) as repo:
            with closing(storage):
                data = cls._get_item_data(repo, storage, metadata)
                if data is not None:
                    storage.add_item(metadata, data)
