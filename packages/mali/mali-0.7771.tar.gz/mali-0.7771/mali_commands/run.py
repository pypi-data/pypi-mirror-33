# -*- coding: utf8 -*-
import json
import logging
import os
import uuid
from traceback import format_exception_only
import six
import click
import yaml
from click import exceptions

from mali_commands.commons import output_result
from .utilities import source_tracking


@click.group('run', help='runs an experiment on a cluster. By defaults run on a local cluster ')
def run_commands():
    pass


def _load_recipe(r_path):
    if not os.path.isfile(r_path):
        return {}
    else:
        print('loading defaults from recipe: %s' % r_path)
        with open(r_path) as f:
            return yaml.safe_load(f)


DEFAULT_RECIPE_PATH = '.ml_recipe.yml'


def _source_tracking_data(path_=None):
    if path_ is None:
        path_ = os.getcwd()
    repo_obj = None
    src_data = {}
    try:
        repo_obj = source_tracking.get_repo(path_)
        src_data = _export_repo_state(repo_obj, mode='local')
    # noinspection PyBroadException
    except Exception as ex:
        src_data['error'] = export_exception(ex)
    return src_data, repo_obj


def export_exception(ex):
    return ('\n'.join(format_exception_only(ex.__class__, ex))).strip()


def _export_repo_state(repo_obj, mode=None):
    mode = mode or 'local'
    src_data = {}
    try:
        src_data['branch'] = repo_obj.branch.name
        src_data['remote'] = repo_obj.remote_url
        src_data['sha_local'] = repo_obj.head_sha
        src_data['sha_local_url'] = repo_obj.head_sha_url
        src_data['is_dirty'] = not repo_obj.is_clean
        src_data['mode'] = mode
        if repo_obj.has_head:
            commit_data = repo_obj.export_commit(repo_obj.repo.head.commit)
        if commit_data is not None:
            src_data.update(commit_data)
    # noinspection PyBroadException
    except Exception as ex:
        src_data['error'] = export_exception(ex)
    logging.debug('_export_repo_state: %s', src_data)
    return src_data


def get_tracking_repo(repo_obj):
    repo_path = os.path.join(repo_obj.repo.working_dir, '.ml_tracking_repo')
    if os.path.isfile(repo_path):
        with open(repo_path) as f:
            tracking_repo = f.read().strip()
            logging.info('{} is tracked by {}'.format(repo_obj.repo.working_dir, tracking_repo))
            return tracking_repo
    # TODO: ADD QUERY to track server
    # return "git@github.com:missinglinkai/sim-test-remote-run.git"
    return None


def _validate_tracking_target(repo_obj, shadow_repo):
    if shadow_repo is None:
        return {'error': 'no tracking repository found.'}
    if shadow_repo.startswith('http'):
        return {'error': 'HTTP[S] git repositories are not supported. Please use the git/ssh version of {}'.format(shadow_repo)}
    return {'tracking_repository_url': shadow_repo}


def _sync_working_dir_if_needed(repo_obj, invocation_id):
    try:
        src_data = _validate_tracking_target(repo_obj, get_tracking_repo(repo_obj))
        if 'tracking_repository_url' in src_data:
            tracking_repository_url = src_data['tracking_repository_url']
            logging.info('Repository tracking is enabled. Tracking to repository: {}'.format(tracking_repository_url))
            source_tracking_repo = source_tracking.GitRepoSyncer.clone_tracking_repo(tracking_repository_url)
            commit_tag = source_tracking.GitRepoSyncer.merge_src_to_tracking_repository(repo_obj.repo, source_tracking_repo, br_tag=invocation_id)
            shadow_repo_obj = source_tracking.get_repo(repo=source_tracking_repo)
            cur_br = source_tracking_repo.active_branch
            source_tracking_repo.git.checkout(commit_tag)
            shadow_repo_obj.refresh()
            src_data = _export_repo_state(shadow_repo_obj, mode='shadow')
            source_tracking_repo.git.checkout(cur_br)

        if 'error' not in src_data:
            logging.info('Tracking repository sync completed. This experiment source code is available here: {}'.format(src_data['sha_local_url']))
        else:
            logging.info('Tracking repository sync Failed. The Error was: {}'.format(src_data['error']))
        return src_data

    except Exception as ex:
        ex_txt = export_exception(ex)
        logging.exception("Failed to init repository tracking. This experiment may not be tracked")
        return {'error': ex_txt}


def parse_env_array_to_dict(env_array):
    if env_array is None:
        return {}
    res = {}
    for env_tuple in env_array:
        key, value = env_tuple.split('=')
        key = key.strip()
        value = value.strip()

        if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
            value = value[1:-1]
        res[key] = value
    return res


def _read_input_data_and_load_recipe(kwargs):
    recipe = kwargs.pop('recipe', None)
    env = kwargs.pop('env', [])
    persistent_path = kwargs.pop('persistent_path', [])

    # try:
    persistent_paths = None
    if len(persistent_path) > 0:
        persistent_paths = []
        for host_path, mount_path in persistent_path:
            persistent_paths.append(dict(host_path=host_path, mount_path=mount_path))

    input_data = {
        'org': kwargs.pop('org', None), 'project': kwargs.pop('project', None),
        'image': kwargs.pop('image', None),
        'git_repo': kwargs.pop('git_repo', None), 'git_tag': kwargs.pop('git_tag', None),
        'source_dir': kwargs.pop('source_dir', None),
        'command': kwargs.pop('command', None),
        'data_query': kwargs.pop('data_query', None), 'data_volume': kwargs.pop('data_volume', None),
        'data_use_iterator': kwargs.pop('data_iterator', False), 'data_dest_folder': kwargs.pop('data_dest', None),
        'output_paths': kwargs.pop('output_paths', []), 'persistent_paths': persistent_paths,
        'gpu': kwargs.pop('gpu', False), 'env': parse_env_array_to_dict(env)
    }
    input_data['env'] = json.dumps(input_data.get('env', {}))

    # Data test must reside inside /data as it will reside inside the data folder, until is configurable
    if input_data.get('data_dest_folder') is not None and not input_data['data_dest_folder'].startswith('/data'):
        raise click.BadOptionUsage('`--data_dest` must begin with /data')

    # Load Recipe
    recipe_data = _load_recipe(recipe or DEFAULT_RECIPE_PATH)
    for k, v in recipe_data.items():
        if k in input_data and input_data[k] is None:
            input_data[k] = v

    # Apply Defaults
    input_data['gpu'] = False if input_data['gpu'] is None else input_data['gpu']
    input_data['data_use_iterator'] = False if input_data['data_use_iterator'] is None else input_data['data_use_iterator']

    default_image = 'gw000/keras:1.2.2-cpu' if not input_data.get('gpu') else 'gw000/keras:1.2.2-gpu'
    input_data['image'] = input_data.get('image') or default_image

    if input_data.get('image') is None and input_data.get('command') is None:
        raise exceptions.BadOptionUsage('No command nor image provided')

    if input_data.get('project') is None:
        raise exceptions.BadOptionUsage('Please provide `project`')
    return input_data


def _has_valid_git_pointer(input_data):
    logging.debug('is valid git pointer? %s', input_data)
    is_valid = input_data.get('git_repo') is not None
    if is_valid:
        input_data['git_mode'] = input_data.get('git_mode', 'external')
    return is_valid


def _build_src_pointer(input_data):
    if not _has_valid_git_pointer(input_data):
        exp_id = uuid.uuid4().hex[:5]
        src_repo, x = _source_tracking_data(input_data.get('source_dir'))
        sync_res = _sync_working_dir_if_needed(x, exp_id)
        if 'error' in sync_res:
            logging.error(sync_res['error'])
        else:
            input_data['git_repo'] = sync_res['remote']
            input_data['git_tag'] = sync_res['branch']
            input_data['git_mode'] = sync_res['mode']
        if not _has_valid_git_pointer(input_data):  # still
            logging.warning('Failed to obtain git point. input was %s', input_data)
            raise exceptions.BadOptionUsage('Failed to obtain git point to use fo the experiment. please provide --git-repo, or --source-dir if you have shadow repository tracking enabled')
            # todo: find the current git path and get tracing path from the server if we don't have git point
            # todo better handling of ignoring
        return input_data


def _save_recipe(input_data, save_recipe):
    with open(save_recipe, 'w') as f:
        save_data = {}
        for k, v in input_data.items():
            if v is not None:
                save_data[k] = v
        yaml.safe_dump(save_data, f, default_flow_style=False)
        click.echo('Recipe saved to {}'.format(save_recipe))
    return True


@run_commands.command('xp')
@click.pass_context
@click.option('--org', type=str, help='organization to use')
@click.option('--project', type=int if six.PY3 else long, help='Project ID to hold the experiments started by the job')
@click.option('--image', type=str, required=False, help='Docker image to use, defaults to keras 1.2.2 (gw000)')
@click.option('--git-repo', type=str, required=False, help='Git repository to pull the code from')
@click.option('--git-tag', type=str, required=False, help='Git branch/tag for the git repository. defaults to master. The cloned code will be available under `/code`')
@click.option('--source-dir', type=str, required=False, help='source directory for the experiment.')
@click.option('--command', type=str, required=False, help='command to execute')
@click.option('--gpu/--cpu', required=False, default=None, help='Use GPU for this instance. Your image will need to support this as well. Defaults to --cpu')
@click.option('--data-volume', type=str, required=False, help='data volume to clone data from')
@click.option('--data-query', type=str, required=False, help='query to execute on the data volume')
@click.option('--data-dest', type=str, required=False, help='destination folder and format for cloning data. If provided, must begin with /data')
@click.option('--data-iterator', type=bool, required=False, help='When set to True, data will not be cloned before the experiment and the quarry will be available for the SDK iterator')
@click.option('--recipe', '-r', type=click.Path(exists=True), required=False, help='recipe file. recipe file is yaml file with the `flag: value` that allows you to specify default values for all params for this function')
@click.option('--save-recipe', type=str, required=False, help='Saves a recipe for this call to the target file and quits. Note the default values are not encoded into the recipe')
@click.option('--env', multiple=True, required=False, help='Environment variables to pass for the invocation in key=value format. You can use this flag multiple times')
@click.option('--output-paths', multiple=True, required=False, help='Paths that will be exported to the Data management at the end of the invocation job. The paths will be available to the the running code under `/path_name` by defaults to `/output`')
@click.option('--persistent-path', multiple=True, type=(str, str), required=False,
              help='` --persistent-path /mnt/data /my_data` \n'
                   'Maps a the `/mnt/data` path (or docker volume name) on the hosting server to the `/my_data` folder of the experiment. \n '
                   'Can be specified more than once.\n'
                   'Persistent mappings are given r/w permission.\n'
                   'USE WITH CAUTION!')
@click.option('--times', type=int, required=False, default=1)
def run_experiment(ctx, **kwargs):
    save_recipe = kwargs.pop('save_recipe', False)
    times = kwargs.pop('times', 1)
    input_data = _read_input_data_and_load_recipe(kwargs)

    _build_src_pointer(input_data)
    click.echo()
    click.echo('Job parameters:')
    for k, v in input_data.items():
        if v:
            click.echo('{:<20}: {}'.format(k, json.dumps(v)))
    click.echo()

    if save_recipe is not None:
        _save_recipe(input_data, save_recipe)
        return

    org = input_data.pop('org')
    project = input_data.pop('project')
    for i in range(times):
        result = ctx.obj.handle_api(ctx.obj, ctx.obj.session, 'put', '{}/{}/invoke'.format(org, project), input_data)
        output_result(ctx, result, ['ok', 'invocation'])
