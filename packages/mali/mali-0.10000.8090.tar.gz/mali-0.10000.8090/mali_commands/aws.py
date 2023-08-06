# -*- coding: utf8 -*-
import logging
from collections import defaultdict
from functools import wraps
from pprint import pformat
import six
import botocore
import click
from click import exceptions
from colorama import Fore, Style

from .cloud.aws import AwsContext, BackendContext
from .commons import output_result
from .legit.context import Expando
from .utilities.default_params import org_with_default, option_with_default_factory


@click.group('aws')
@click.pass_context
@option_with_default_factory('--region', envvar="ML_AWS_REGION", help='AWS region to use', default_key='aws_region', required=False)
def aws_commands(ctx, **kwargs):
    ctx.obj.aws = Expando()
    ctx.obj.aws.region = kwargs.pop('region', None)


def handle_aws_errors(fn):
    @wraps(fn)
    def try_call(*args, **kwargs):
        try:
            return fn(*args, **kwargs)

        except botocore.exceptions.NoCredentialsError as ex:
            logging.info('Failed to validate authentication', exc_info=1)
            raise exceptions.ClickException('AWS configuration is incomplete. Please run `aws configure`. Error: %s' % str(ex))

    return try_call


@aws_commands.command('init')
@click.pass_context
@org_with_default()
@click.option('--ssh-key-path', default=None, help='SSH Key to use in for git clone commands, and connecting to virtual machines')
@handle_aws_errors
def init_auth(ctx, **kwargs):
    aws = AwsContext(ctx, kwargs)

    aws.encrypt_and_send_connector()
    aws.setup_vpc_if_needed()
    aws.setup_s3_if_needed()
    print(aws.auth_state)


def _trim_value(value, max_chars=30):
    if len(value) > max_chars:
        return value[:max_chars - 4] + ' ...'

    return value


def _with_format(text, fore='', style=''):
    return Style.RESET_ALL + fore + style + text + Style.RESET_ALL


class ArgRow:
    show_score = {
        'std': 1000,
        'adv': 500,
        'internal': 100
    }
    readonly_score = {
        False: 0,
        True: 50
    }
    configured_score = {
        False: 0,
        True: 5000
    }

    @classmethod
    def _values_to_str(cls, v):
        if isinstance(v, six.string_types):
            return v

        return '\n'.join(v if v is not None else '')

    def _active_value(self):
        return self.value if self.configured or self.read_only else self.default_value

    def __eq__(self, other):
        return self.name == other.name and self.arg == other.arg

    def __init__(self, name, arg):
        self.name = name
        self.arg = arg
        self.read_only = self.arg.get('read_only', False)
        self.configured = 'configured' in self.arg and not self.read_only
        self.show_level = self.arg.get('show_level', self.arg.get('edit_level', 'internal'))
        self.score = self.show_score[self.show_level] + self.configured_score[self.configured] + self.readonly_score[self.read_only]

        self.value = self._values_to_str(self.arg.get('configured'))
        self.default_value = self._values_to_str(self.arg.get('default'))
        self.active_value = self._active_value()

    color_legend = '  |  '.join(['Color Legend:', _with_format('read only', Fore.BLUE), _with_format('configured', Fore.GREEN), _with_format('default value', Fore.RESET)])
    param_filed = _with_format('Parameter', Fore.WHITE, Style.BRIGHT)
    value_field = _with_format('Value', Fore.WHITE, Style.BRIGHT)
    default_field = _with_format('Default', Fore.WHITE, Style.DIM)
    description_field = _with_format('Description', Fore.WHITE, Style.DIM)

    def configured_name(self):
        return _with_format(self.name, Fore.GREEN, Style.BRIGHT)

    def default_name(self):
        return _with_format(self.name, Fore.RESET, Style.BRIGHT)

    def row_name(self):
        return self.configured_name() if self.configured else self.default_name()

    def read_only_value(self):
        return _with_format(self.active_value, Fore.BLUE, Style.NORMAL)

    def configured_value(self):
        return _with_format(self.active_value, Fore.GREEN, Style.BRIGHT)

    def un_configured_value(self):
        return _with_format(self.active_value, Fore.RESET, Style.DIM)

    def configured_default_value(self):
        return _with_format(self.default_value, Fore.GREEN, Style.BRIGHT)

    def un_configured_default_value(self):
        return _with_format(self.default_value, Fore.RESET, Style.DIM)

    def row_value(self):
        if self.read_only:
            return self.read_only_value()

        if self.configured:
            return self.configured_value()

        return self.un_configured_value()

    def description_all(self):
        return _with_format(_trim_value(self.arg.get('description'), 60), Style.DIM)

    def row_description(self):
        return self.description_all()

    def row_default(self):
        if self.read_only:
            return ''

        if self.configured:
            return self.un_configured_default_value()

        return self.configured_default_value()

    def to_row(self):
        return {
            self.param_filed: self.row_name(),
            self.value_field: self.row_value(),
            self.default_field: self.row_default(),
            self.description_field: self.row_description(),
        }

    def displayed(self, target_show_levels, configured_only):
        if self.configured:
            return True

        shown = self.show_level in target_show_levels
        return shown and not configured_only

    @classmethod
    def import_and_filter(cls, data, target_show_levels, configured_only):
        res = []
        for k, v in data.items():
            ob = cls(k, v)
            if ob.displayed(target_show_levels, configured_only):
                res.append(ob)

        return res

    @classmethod
    def table_fields(cls, kwargs):
        show_defaults = kwargs.get('show_defaults', False)
        show_description = kwargs.get('show_description', False)

        fields = [cls.param_filed, cls.value_field]
        if show_defaults:
            fields.append(cls.default_field)
        if show_description:
            fields.append(cls.description_field)

        return fields

    @classmethod
    def print_table(cls, ctx, kwargs, data):
        table = [x.to_row() for x in sorted(data, key=lambda x: x.score, reverse=True)]
        fields = cls.table_fields(kwargs)
        click.echo(cls.color_legend)
        click.echo()
        output_result(ctx, table, fields=fields)

    @classmethod
    def parse_user_input(cls, tuples):
        res = defaultdict(list)
        for tup in tuples:
            res[tup[0]].append(tup[1])
            if 'None' in res[tup[0]]:
                res[tup[0]] = ['None']
        return dict(res)


@aws_commands.command('resource_group')
@click.pass_context
@org_with_default()
@click.argument('group', required=True, nargs=1)
@click.option('--json', required=False, default=False, help="output data in json format")
@click.option('--advanced', required=False, default=False, help="show advanced configuration parameters as well")
@click.option('--show-defaults/--no-defaults', required=False, default=False, help="also show default values")
@click.option('--create/--update', required=False, default=False, help="create new group or update existing")
@click.option('--show-description/--no-description', required=False, default=False, help="also show parameter descriptions")
@click.option('--configured-only/--configured-and-defaults', required=False, default=False, help="show only parameters with configured values")
@click.option('--set', required=False, default=None, type=(str, str), multiple=True, help="Change parameter value. Some parameters can be specified multiple times for arrays and you can remove configured option by setting it to `None`")
def aws_resource_group(ctx, **kwargs):
    group_id = kwargs.pop('group')

    json = kwargs.get('json', False)

    configured_only = kwargs.get('configured_only', False)
    target_show_levels = ['std']

    if kwargs['advanced']:
        target_show_levels = ['std', 'adv']
    aws = BackendContext(ctx, kwargs)

    new_values = ArgRow.parse_user_input(kwargs['set'])
    if new_values:
        response = aws.put_resource_group_parameters(group_id, new_values, new_group=kwargs.pop('create'))
    else:
        response = aws.resource_group_description(group_id)
    data = ArgRow.import_and_filter(response, target_show_levels, configured_only)
    if json:
        click.echo(pformat({v.name: v.arg for v in data}))
    else:
        ArgRow.print_table(ctx, kwargs, data)
