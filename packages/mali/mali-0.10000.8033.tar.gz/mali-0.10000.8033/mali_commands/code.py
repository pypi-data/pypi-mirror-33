# -*- coding: utf8 -*-
import click
from .commons import output_result
from .utilities import source_tracking


@click.group('code', help='Repository tracking allows you to quickly see, compare and clone snapshots, including'
                          ' unpushed, uncommited and unstaged files of your source code for every experiment.'
                          ' In order to use this feature, you must first create setup tracking repository - empty git repository'
                          ' in the same organization as your tracked (source) repository, and then call "track"'
                          ' This feature relays on the same git authentication mechanism as your source repository'
                          ' So please make sure that the ssh key used for fetching your git code has fetch/push permissions'
                          ' on the tracking repository')
def code_commands():
    pass


def _validate_repos_validity(source_repository, tracking_repository):
    if source_tracking.remote_url_obj(source_repository) is None:
        raise click.BadOptionUsage("Source repository: {} is invalid".format(source_repository))

    if source_tracking.remote_url_obj(tracking_repository) is None:
        raise click.BadOptionUsage("Tracking repository: {} is invalid".format(tracking_repository))

    if source_tracking.validate_diff_urls(source_repository, tracking_repository):
        raise click.BadOptionUsage("The repository repository can't be the same as the source one")


def _validate_code_params(source_repository, tracking_repository):
    _validate_repos_validity(source_repository, tracking_repository)

    if not source_tracking.validate_remote_urls_org(source_repository, tracking_repository):
        raise click.BadOptionUsage("The tracking repository must belong to the same organization as the source ({})".format(source_tracking.get_org_from_remote_url(source_repository)))


def _get_source_tracking_remote_url(ctx, param, value):
    if value is None:
        value = source_tracking.get_remote_url()

    if value is None:
        raise click.MissingParameter('--source-repository')

    return value


@code_commands.command('track', help='Sets up tracking for given source repository. When setting up tracking from mali, both source and target repositories must sit under the same organization. For more information please refer to our documentation.')
@click.option('--org', required=True, help="Organization/Workspace. Repository tracking is available to all users that have permission to access the Organization/Workspace")
@click.option('--source-repository', required=False, callback=_get_source_tracking_remote_url, help='Source repository url. Defaults to the first remote of the repository of the current path')
@click.option('--tracking-repository', required=True,
              help='Target repository. When setting up tracking using mali, this repository must be under the same organization as teh source repository (i.e. if the source repo is https://github.com/my_org/my_repo, the tracking repository must be in the https://github.com/my_org organization')
@click.pass_context
def track_add(ctx, org, source_repository, tracking_repository):
    _validate_code_params(source_repository, tracking_repository)

    data = {
        'target': tracking_repository
    }
    target_url = '{org}/code/track?src={src_repo}'.format(org=org, src_repo=source_tracking.remote_to_template(source_repository))
    result = ctx.obj.handle_api(ctx.obj, ctx.obj.session, 'get', target_url, data)
    output_result(ctx, result, ['ok'])
