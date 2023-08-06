import click
import os
import json
import logging
from .os_utils import mkdir_recursive


def _config_folder_path():
    return os.path.join(os.path.expanduser('~'), '.MissingLinkAI')


def _defaults_path():
    return os.path.join(_config_folder_path(), 'defaults.json')


def get_defaults():
    if os.path.isfile(_defaults_path()):
        try:
            with open(_defaults_path(), 'r') as f:
                return json.load(f)
        except Exception:
            logging.warning('Defaults file at %s is corrupted', _defaults_path(), exc_info=1)
    return {}


def _set_defaults(data):
    mkdir_recursive(_config_folder_path())
    with open(_defaults_path(), 'w') as f:
        json.dump(data, f)


def set_default(key, value):
    new_doc = get_defaults()
    new_doc[str(key)] = str(value)
    try:
        _set_defaults(new_doc)
    except Exception:
        logging.exception('Failed to save defaults to %s', _defaults_path())


def del_default(key):
    new_doc = get_defaults()
    val = new_doc.pop(key, None)
    if val is not None:
        logging.debug('Removing %s default value %s', key, val)
    try:
        _set_defaults(new_doc)
    except Exception:
        logging.exception('Failed to save defaults to %s', _defaults_path())


def get_default(val):
    return get_defaults().get(val)


def option_with_default_factory(param_name, **kwargs):
    default_key = kwargs.pop('default_key', None)
    if default_key is not None:
        kwargs['default'] = get_default(default_key)
    return click.option(param_name, **kwargs)


def org_with_default(**kwargs):
    defaults = dict(type=str, envvar='ML_ORG', default_key='org', required=True, help='Organisation')
    defaults.update(kwargs)
    return option_with_default_factory('--org', **defaults)


def project_with_default(**kwargs):
    defaults = dict(type=str, envvar='ML_PROJECT', default_key='project', required=True, help='Project')
    defaults.update(kwargs)
    return option_with_default_factory('--project', **defaults)
