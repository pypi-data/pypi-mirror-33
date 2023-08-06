# -*- coding: utf8 -*-
import click
from .utilities.default_params import org_with_default, option_with_default_factory
from .legit.context import Expando
from .cloud.aws import AwsContext
import botocore
import logging
from click import exceptions
from functools import wraps


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
@handle_aws_errors
def init_auth(ctx, **kwargs):
    aws = AwsContext(ctx, kwargs)

    aws.encrypt_and_send_connector()
    aws.setup_vpc_if_needed()
    aws.setup_s3_if_needed()
    print(aws.auth_state)
