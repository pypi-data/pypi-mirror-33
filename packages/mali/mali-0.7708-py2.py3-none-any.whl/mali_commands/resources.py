# -*- coding: utf8 -*-
import base64
import logging
import os
import click
import six

from .commons import output_result


def get_home_path():
    if six.PY2:
        from os.path import expanduser, join
        home = expanduser("~")
    else:
        from pathlib import Path
        home = str(Path.home())
    return home


def get_ssh_path():
    from os.path import join
    return join(get_home_path(), '.ssh', 'id_rsa')


def make_data_dir(data_dir_path):
    if six.PY2:
        import errno
        try:
            os.makedirs(data_dir_path)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
    else:
        os.makedirs(data_dir_path, exist_ok=True)


def try_import_docker_and_crypto():
    try:
        # noinspection PyUnresolvedReferences
        import docker
        # noinspection PyUnresolvedReferences
        import cryptography
        return docker, cryptography
    except ImportError as ex:
        raise click.BadOptionUsage('Docker deps are missing. Please run pip install mali[docker], %s' % (ex,))


def ssh_load_key(ssh_key_path):
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives import serialization
    with open(ssh_key_path, 'rb') as f:
        ssh_key_data = f.read()
    private_key = serialization.load_pem_private_key(ssh_key_data, password=None, backend=default_backend())
    key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption()).decode('utf-8')
    logging.info('ssh key loaded from %s', ssh_key_path)
    return key_bytes


DOCKER_IMAGE = 'docker:latest'


def pull_image_from_image(client, image):
    import docker
    ADMIN_VOLUME = {'/var/run/docker.sock': {'bind': '/var/run/docker.sock'}}

    try:
        client.images.get(DOCKER_IMAGE)
    except docker.errors.NotFound:
        click.echo('Pulling docker image')
        client.images.pull(DOCKER_IMAGE)
    cmd = 'docker pull {}'.format(image)
    cont = client.containers.run(DOCKER_IMAGE, command=cmd, auto_remove=True, volumes=ADMIN_VOLUME, environment={'ML_RM_MANAGER': '1'}, detach=True)
    logger_handler = cont.logs(stdout=True, stderr=True, stream=True)
    for log in logger_handler:
        logging.info(log)
    return client.images.get(image)


def auth_resource(ctx, org):
    result = ctx.obj.handle_api(ctx.obj, ctx.obj.session, 'get', '{org}/resource/authorise'.format(org=org))
    return result.get('token')


def validate_and_get_docker_client():
    import docker
    import requests
    client = docker.from_env()
    try:
        client.ping()
    except docker.errors.DockerException as ex:
        raise click.BadArgumentUsage('Failed to connect to docker host %s' % (str(ex)))
    except requests.exceptions.ConnectionError as ex:
        raise click.BadArgumentUsage('Failed to connect to docker host %s' % (str(ex)))
    logging.info('Docker host verified')
    return client


def pull_ml_image(config, docker_client):
    click.echo('Getting/updating MissingLinks Resource Manager image')
    img = pull_image_from_image(docker_client, config.rm_manager_image)
    return img


def _get_combined_volume_path(*args):
    res = {}
    for a in args:
        res.update(a)
    return res


def _docker_present(command, *args, **kwargs):
    import docker
    try:
        return command(*args, **kwargs) or True  # we are looking only for exceptions here
    except docker.errors.NotFound:
        return False


def _pad_str_to_len(s, pad_len=32):
    return s + (pad_len - len(s) % pad_len) * ' '


def b64_encode_to_utf8(s):
    if six.PY3 and not isinstance(s, bytes):
        s = s.encode('utf-8')
    return base64.b64encode(s).decode('utf-8')


def b64_decode_from_utf8(s):
    if six.PY3 and not isinstance(s, bytes):
        s = s.encode('utf-8')
    return base64.b64decode(s)


def get_boto_client(client_type, region_name=None):
    import boto3
    my_session = boto3.session.Session()
    return boto3.client(client_type, region_name=region_name or my_session.region_name)


def encrypt_string_with_boto_kms(input_str, arn):
    from Crypto.Cipher import AES
    kms_client = get_boto_client('kms')

    data_key = kms_client.generate_data_key(KeyId=arn, KeySpec='AES_256')
    ciphertext_blob = data_key.get('CiphertextBlob')
    plaintext_key = data_key.get('Plaintext')
    iv = kms_client.generate_random(NumberOfBytes=16)['Plaintext']
    encryption_suite = AES.new(plaintext_key, AES.MODE_CBC, iv)
    cipher_text = encryption_suite.encrypt(_pad_str_to_len(input_str))
    return dict(iv=b64_encode_to_utf8(iv), key=b64_encode_to_utf8(ciphertext_blob), data=b64_encode_to_utf8(cipher_text))


def decrypt_string_with_boto_kms(input_data, region):
    from Crypto.Cipher import AES

    iv, key, data = [b64_decode_from_utf8(x) for x in input_data]

    kms_client = get_boto_client('kms', region_name=region)

    decrypted_key = kms_client.decrypt(CiphertextBlob=key).get('Plaintext')
    cypher = AES.new(decrypted_key, AES.MODE_CBC, iv)
    return cypher.decrypt(data).decode('utf-8').rstrip()


def validate_running_resource_manager(config, docker_client, force):
    currnet_rm = _docker_present(docker_client.containers.get, config.rm_container_name)
    if not currnet_rm:
        return

    if not force:
        raise click.BadOptionUsage('Can not install resource manger while one is running. run `docker kill {}` do stop and reuse config or re-run with `--force` flag to clear all configuration'.format(currnet_rm.name))

    click.echo('Killing current Resource Manger (%s) due to --force flag' % currnet_rm.id)
    if currnet_rm.status == 'running':
        currnet_rm.kill()
    currnet_rm.remove(force=True)


def get_config_prefix_and_file(config):
    with open(config.config.config_file_abs_path, 'rb') as f:
        config_data = f.read()
    config_data = b64_encode_to_utf8(config_data)
    prefix = None
    if config.config.config_prefix is not None:
        prefix = config.config.config_prefix
    return prefix, config_data


ADMIN_VOLUME = {'/var/run/docker.sock': {'bind': '/var/run/docker.sock'}}


def _apply_config_to_volume(config, docker_client, ssh_key, token, prefix=None, config_data=None):
    if token is None and ssh_key is None:
        return

    config_volume = {config.rm_config_volume: {'bind': '/config'}}
    conf_mounts = _get_combined_volume_path(ADMIN_VOLUME, config_volume)

    ws_server = config.rm_socket_server

    if prefix is None and config_data is None:
        id_token = config.id_token
        if id_token is None:
            # TODO: make backend data commands support resource token
            raise click.BadOptionUsage('Please call mali auth init first')
        prefix, config_data = get_config_prefix_and_file(config)

    command = ['config', '--ml-server', ws_server, '--ml-config-file', config_data]
    if prefix is not None:
        command.extend(['--ml-config-prefix', prefix])
    if token is not None:
        command.append('--ml-token')
        command.append(token)

    if ssh_key is not None:
        command.append('--ssh-private-key')
        command.append(ssh_key)

    cont = docker_client.containers.run(config.rm_manager_image, command=command, volumes=conf_mounts, environment={'ML_RM_MANAGER': '1'}, detach=True)
    exit_code = cont.wait()
    if exit_code != 0:
        click.echo(cont.logs())
    cont.remove()


def _handle_token_and_data_path(ctx, force, org, token=None):
    cur_config = ctx.obj.config.resource_manager_config
    if force:
        click.echo('Current host config is deleted due to `--force` flag')
        cur_config = {}

    new_token = token or cur_config.get('token')

    if new_token is None:
        new_token = auth_resource(ctx, org)
    ctx.obj.config.update_and_save({
        'resource_manager': {
            'token': new_token,
        }
    })
    return new_token


def _validate_apply_config(ctx, docker_client, org, force, ssh_key_path, token):
    config = ctx.obj
    config_volume_name = config.rm_config_volume

    if force and _docker_present(docker_client.volumes.get, config_volume_name):
        click.echo('Deleting config volume (%s) due to --force flag')
        docker_client.volumes.get(config_volume_name).remove(force=True)

    new_image = not _docker_present(docker_client.volumes.get, config_volume_name)

    ssh_key = None
    if new_image:
        docker_client.volumes.create(config_volume_name)
        if ssh_key_path is None:
            ssh_key_path = click.prompt(text='SSH key path (--ssh-key-path)', default=get_ssh_path())

    token = _handle_token_and_data_path(ctx, force, org, token=token)

    if ssh_key_path is not None:
        ssh_key = ssh_load_key(ssh_key_path)

    _apply_config_to_volume(config, docker_client, ssh_key, token)
    return


def _valiadte_config_volume(config, docker_client):
    if not _docker_present(docker_client.volumes.get, config.rm_config_volume):
        raise click.BadArgumentUsage('Configuration volume is missing. Please re-install')


def _run_resource_manager(config, docker_client):
    _valiadte_config_volume(config, docker_client)
    click.echo('Starting Resource Manager')
    config_volume = {config.rm_config_volume: {'bind': '/config'}}
    run_mounts = _get_combined_volume_path(ADMIN_VOLUME, config_volume)
    return docker_client.containers.run(
        config.rm_manager_image,
        command=['run'],
        auto_remove=False,
        restart_policy={"Name": 'always'},
        volumes=run_mounts,
        environment={'ML_RM_MANAGER': '1', 'ML_CONFIG_VOLUME': config.rm_config_volume},
        detach=True,
        network='host',
        name=config.rm_container_name)


def get_selected_fields(client_input, default_fields=None):
    display_fields = default_fields
    if client_input is not None:
        selected_fields = [x.strip() for x in client_input.split(',')]
        if len(selected_fields) == 1 and selected_fields[0] == '*':
            display_fields = None
        else:
            display_fields = selected_fields
    return display_fields


def append_optional_filters_to_url(url, **kwargs):
    filters = ['{}={}'.format(k, v) for k, v in kwargs.items() if v is not None]
    if len(filters) > 0:
        url = '{url}?{filters}'.format(url=url, filters='&'.join(filters))
    return url


@click.group('resources', help='Operations on resource managers')
def resource_commands():
    pass


@click.group('resources', help='Experimental! Resource Management')
def resource_commands():
    pass


@resource_commands.command('state', help="Get the state of the local resource manager")
@click.pass_context
def get_state(ctx):
    try_import_docker_and_crypto()
    docker_client = validate_and_get_docker_client()
    cur_instance = _docker_present(docker_client.containers.get, ctx.obj.rm_container_name)
    if cur_instance:
        click.echo('%s: %s (%s)' % (cur_instance.name, cur_instance.status, cur_instance.short_id))
    else:
        _valiadte_config_volume(ctx.obj, docker_client)
        click.echo('not running')


@resource_commands.command('start', help="Start resource manager")
@click.pass_context
def start_rm(ctx):
    try_import_docker_and_crypto()
    docker_client = validate_and_get_docker_client()
    cur_instance = _docker_present(docker_client.containers.get, ctx.obj.rm_container_name)
    if cur_instance:
        raise click.BadOptionUsage('Already running')

    _run_resource_manager(ctx.obj, docker_client)
    click.echo('The resource manager is configured and running')


@resource_commands.command('watch', help="Start resource manager")
@click.pass_context
def watch_rm(ctx):
    try_import_docker_and_crypto()
    docker_client = validate_and_get_docker_client()
    cur_instance = _docker_present(docker_client.containers.get, ctx.obj.rm_container_name)
    if not cur_instance:
        cur_instance = _run_resource_manager(ctx.obj, docker_client)
    for line in cur_instance.logs(stream=True):
        line = line.strip()
        if not isinstance(line, six.string_types):
            line = line.decode('utf-8')
        click.echo(line)


@resource_commands.command('stop', help="Stop running resource manager")
@click.pass_context
def stop_rm(ctx):
    try_import_docker_and_crypto()
    docker_client = validate_and_get_docker_client()
    cur_instance = _docker_present(docker_client.containers.get, ctx.obj.rm_container_name)
    if not cur_instance:
        raise click.BadOptionUsage('not running')

    click.echo('Stopping ...')
    cur_instance.stop()
    click.echo('Stopped')


@resource_commands.command('kill', help="Kill running resource manager")
@click.pass_context
def kill_rm(ctx):
    try_import_docker_and_crypto()
    docker_client = validate_and_get_docker_client()
    cur_instance = _docker_present(docker_client.containers.get, ctx.obj.rm_container_name)
    if not cur_instance:
        raise click.BadOptionUsage('not running')

    click.echo('Killing ...')
    cur_instance.kill()
    click.echo('Killed')


@resource_commands.command('list', help="Lists resource managers registered for your organization")
@click.pass_context
@click.option('--org', type=str, help='organization to use', required=True)
@click.option('--connected/--disconnected', default=None, required=False, help='Show only connected / disconnected resource managers. by default lists both')
@click.option('--gpu/--cpu', default=None, required=False, help='Show only  resources with / without configured GPU. by default lists both')
@click.option('--fields', default=None, required=False, help='Fields to display, separated by comma, * for all fields')
def list_resources(ctx, org, connected, gpu, fields):
    from mali_commands.commons import output_result
    url = append_optional_filters_to_url('{org}/resources'.format(org=org), connected=connected, gpu=gpu)
    result = ctx.obj.handle_api(ctx.obj, ctx.obj.session, 'get', url)
    display_fields = get_selected_fields(fields, ['id', 'connected', 'has_gpu', 'client_ip', 'state', 'connection_state_since'])
    output_result(ctx, result.get('resources', []), display_fields)


@resource_commands.command('invocations', help="Lists invocations for your organization")
@click.pass_context
@click.option('--org', type=str, help='organization to use', required=True)
@click.option('--resource', default=None, required=False, help='Show invocations assigned to this resource only')
@click.option('--project', default=None, required=False, help='Show invocations assigned to this project only')
@click.option('--user', default=None, required=False, help='Show invocations submitted by this user only')
@click.option('--state', default=None, required=False, help='Show invocations in this state only')
@click.option('--fields', default=None, required=False, help='Fields to display, separated by comma, * for all fields')
@click.option('--gpu/--cpu', default=None, required=False, help='Show only invocations marked  for GPU/CPU invocations . by default lists both')
def list_invocations(ctx, org, resource, project, user, state, fields, gpu):
    from mali_commands.commons import output_result

    url = append_optional_filters_to_url('{org}/invocations'.format(org=org), resource=resource, project=project, user=user, state=state, gpu=gpu)
    result = ctx.obj.handle_api(ctx.obj, ctx.obj.session, 'get', url)
    display_fields = get_selected_fields(fields, ['id', 'state', 'project', 'gpu', 'resource', 'queued_at', 'image', 'command'])
    results = result.get('invocations', [])
    if display_fields is None or 'queued_at' in display_fields:
        results = sorted(results, key=lambda x: x['queued_at'], reverse=True)
    output_result(ctx, results, display_fields)


@resource_commands.command('install')
@click.pass_context
@click.option('--org', type=str, help='organization to use', required=True)
@click.option('--manager-type', type=str, default='docker', help='resource manager type. Currently only `docker` is supported.')
@click.option('--ssh-key-path', type=str, help='Path to the private ssh key to be used by the resource manager', default=None)
@click.option('--force/--no-force', default=False, help='Force installation (stops current resource manager if present')
@click.option('--resource-token', default=None, type=str, help='MissingLink resource token. One will be generated if this instance of MALI is authorized')
def install_rm(ctx, org, manager_type, ssh_key_path, force, resource_token):
    try_import_docker_and_crypto()
    docker_client = validate_and_get_docker_client()
    validate_running_resource_manager(ctx.obj, docker_client, force)

    pull_ml_image(ctx.obj, docker_client)
    _validate_apply_config(ctx, docker_client=docker_client, org=org, force=force, ssh_key_path=ssh_key_path, token=resource_token)
    _run_resource_manager(ctx.obj, docker_client)
    click.echo('The resource manager is configured and running')


def pop_key_or_prompt_if(kws, key, src_default=None, **kwargs):
    cur_val = kws.pop(key, src_default)
    while cur_val == src_default:
        if 'default' in kwargs and kws.get('silent', False):
            click.echo('{}: {} (silent)'.format(kwargs.get('text'), kwargs.get('default')))
            return kwargs['default']
        cur_val = click.prompt(**kwargs)
    return cur_val


def cloud_connector_defaults(ctx, cloud_type, kwargs):
    prefix, config_data = get_config_prefix_and_file(ctx.obj)

    return dict(
        mali_image='missinglinkai/mali:UNSTABLE',
        socket_server=ctx.obj.rm_socket_server,
        config_volume=ctx.obj.rm_config_volume,
        rm_image=ctx.obj.rm_manager_image,
        container_name=ctx.obj.rm_container_name,
        prefix=prefix,
        name=pop_key_or_prompt_if(kwargs, 'connector', text='Connector [--connector]:', default='%s-%s' % (cloud_type, 'default')),
        cloud_type=cloud_type,
    ), config_data


def azure_auth(ctx, kwargs, org):
    from .commons import WaitForHttpResponse
    template, _ = cloud_connector_defaults(ctx, cloud_type='azure', kwargs=kwargs)

    azure_subscription_id = pop_key_or_prompt_if(kwargs, 'azure_subscription_id', text='subscription id [--azure-subscription-id]')
    tenant_id_request_url = '{org}/azure/tenant_id_for/{subscription_id}'.format(org=org, subscription_id=azure_subscription_id)

    tenant_id_response = ctx.obj.handle_api(ctx.obj, ctx.obj.session, 'get', tenant_id_request_url)
    tenant_id = tenant_id_response['tenantId']

    server = WaitForHttpResponse(uri='/console/azure/authorised', port=8002)
    cloud_data = [
        {'key': 'auth_state', 'data': 'pending'},
        {'key': 'auth_return_url', 'data': server.url},
        {'key': 'azure_subscription_id', 'data': azure_subscription_id},
        {'key': 'azure_tenant_id', 'data': tenant_id},
    ]
    template['cloud_data'] = cloud_data
    url = '{org}/cloud_connector/{name}'.format(org=org, name=template['name'])
    ctx.obj.handle_api(ctx.obj, ctx.obj.session, 'post', url, template)

    auth_url = '{org}/azure/authorise_config/{name}'.format(org=org, name=template['name'])
    auth_request = ctx.obj.handle_api(ctx.obj, ctx.obj.session, 'get', auth_url)
    auth_url_path = auth_request['url']
    click.echo(auth_url_path)

    resp = server.run()
    authed_url = '{org}/azure/authorised/{config_id}/code/{code}'.format(
        org=org, config_id=template['name'], code=resp['code'][0])
    authed_request = ctx.obj.handle_api(ctx.obj, ctx.obj.session, 'get', authed_url)
    if authed_request['ok']:
        click.echo('Azure Authorisation for %s completed' % template['name'])
    else:
        click.echo('Azure Authorisation for %s failed' % template['name'])

    return authed_request['result']


@resource_commands.command('setup_ephemeral_template', help="creates, encrypts and stores cloud config used for ephemeral configurations")
@click.pass_context
@click.option('--org', type=str, help='organization to use', required=True)
@click.option('--arn', type=str, help='arn of the KMS encryption key')
@click.option('--ssh-key-path', type=str, help='Path to the private ssh key to be used by the resource manager', default=None)
def setup_ephemeral_template(ctx, org, **kwargs):
    kwargs['dynamic_group'] = True
    create_group(ctx, kwargs, org)


def get_cloud_connector_default_connector_name(available_connectors, cloud_type):
    for connector in available_connectors:
        if connector['default']:
            return connector['name']
    if available_connectors:
        return available_connectors[0]['name']
    return '%s-default' % cloud_type


def _get_cloud_connectors(ctx, org, cloud_type):
    click.echo("Checking for available cloud connectors for %s" % cloud_type)
    url = '{org}/{cloud_type}/cloud_connectors'.format(org=org, cloud_type=cloud_type)
    response = ctx.obj.handle_api(ctx.obj, ctx.obj.session, 'get', url)
    return response.get('result', [])


def get_cloud_connector(ctx, org, kwargs, cloud_type, connect_dict=None):
    if connect_dict is None:
        connect_dict = {
            'azure': lambda: azure_auth(ctx, kwargs, org),
        }

    available_connectors = _get_cloud_connectors(ctx, org, cloud_type)
    default_connector = get_cloud_connector_default_connector_name(available_connectors, cloud_type)
    click.echo('List of %s available connectors for %s' % (cloud_type, org))
    output_result(ctx, available_connectors)
    click.echo('You can use easting connector by specifying its name or create a new one by using a name from the list')
    connector_param = 'connector'
    connector_cli_param = '--connector'
    connector_name = pop_key_or_prompt_if(kwargs, connector_param, text='Connector name [%s] ' % connector_cli_param, default=default_connector)
    for x in available_connectors:
        if connector_name == x['name']:
            click.echo('Reusing `%s` connector' % connector_name)
        return x
    kwargs[connector_param] = connector_name

    return connect_dict[cloud_type]()


def _resource_group_deafults(ctx, kws, connector, cloud_type):
    is_static = not pop_key_or_prompt_if(kws, 'dynamic_group', type=bool, text=' [--dynamic-group]', default=cloud_type == "aws")
    static_hint = 'static' if is_static else 'dynamic'
    group_name = pop_key_or_prompt_if(kws, 'group_name', text='Group name [--group-name]', default='%s-default' % static_hint)
    click.echo('Creating %s group `%s` ' % (static_hint, group_name))

    return {
        'name': group_name,
        'cloud_type': cloud_type,
        'connector': connector,
        'is_static': is_static,
        'config': '{}',  # todo: add cloud data from the connector here?
        'gpu': pop_key_or_prompt_if(kws, 'group_gpu', text='Is this a GPU group [--group-gpu]', default=False, type=bool),
        'terminate_on_stop': pop_key_or_prompt_if(kws, 'terminate_on_stop', text='Terminate instances (should be %s for %s groups) [--group-terminate-on-stop]' % (not is_static, static_hint), default=not is_static, type=bool),
        'priority': pop_key_or_prompt_if(kws, 'priority', text='Priority (higher is better) [--group-priority]', default=100, type=int),
        'idle_timeout': pop_key_or_prompt_if(kws, 'idle_timeout', text='Idle timeout  [--group-idle-timeout]', default=15, type=int),
    }


def create_group(ctx, kws, org):
    cloud_type = pop_key_or_prompt_if(kws, 'cloud_type', text='Cloud Type [--cloud-type]', default='azure')
    connector = get_cloud_connector(ctx, org, kws, cloud_type)
    request = _resource_group_deafults(ctx, kws, connector['name'], connector['cloud_type'])

    if not request['is_static']:
        request['capacity'] = pop_key_or_prompt_if(kws, 'group_capacity', text='Cloud Type [--group-capacity]', default=5, type=int)
    group_name = request['name']
    url = '{org}/resource_group/{name}'.format(org=org, name=group_name)
    response = ctx.obj.handle_api(ctx.obj, ctx.obj.session, 'post', url, request)
    click.echo('Group %s created.' % group_name)
    return response['result']


def select_resource_group(ctx, available_groups, static, kws, org):
    hint_name = '%s-default' % ('dynamic' if not static else 'static')
    available_groups = [x for x in available_groups if x['is_static'] == static]
    if available_groups:
        click.echo('Here is a list of your current groups. You can use one of them or enter a name for new group')
        output_result(ctx, available_groups, fields=['name', 'cloud_type', 'capacity', 'gpu', 'priority'])
        hint_name = available_groups[0]['name']
    group_name = pop_key_or_prompt_if(kws, 'group_name', text='Group name [--group-name]', default=hint_name)
    for group in available_groups:
        if group_name == group['name']:
            click.echo('Selected pre-existing group %s' % group_name)
            return group
    kws['group_name'] = group_name
    kws['dynamic_group'] = False

    return create_group(ctx, kws, org)


def static_resource_groups(ctx, org, kwargs):
    click.echo("Checking for available resource groups for %s" % org)
    url = '{org}/static_resource_groups'.format(org=org)
    response = ctx.obj.handle_api(ctx.obj, ctx.obj.session, 'get', url)
    available_groups = response.get('results', [])
    return select_resource_group(ctx, available_groups, True, kwargs, org)


def get_unmanaged_resources_list(ctx, org, cloud_type, connector):
    url = '{org}/{cloud_type}/unmanaged_machines/{connector}'.format(org=org, cloud_type=cloud_type, connector=connector)
    response = ctx.obj.handle_api(ctx.obj, ctx.obj.session, 'get', url)
    unmanaged_resources = response.get('results', [])
    index = 0
    for res in unmanaged_resources:
        index += 1
        res['index'] = index

    return unmanaged_resources


def select_unmanaged_machine(ctx, org, cloud_type, connector, kws):
    available_resources = get_unmanaged_resources_list(ctx, org, cloud_type, connector)
    max_index = len(available_resources)
    output_result(ctx, available_resources, ['index', 'name', 'region', 'resource_group', 'type'])
    selected = 0
    if max_index == 0:
        return None
    while True:
        selected = pop_key_or_prompt_if(kws, 'machine_index', text='Machine Index', default=1, type=int)
        if 0 < selected <= max_index:
            return available_resources[selected - 1]


def register_static_unmanaged_machine(ctx, org, group, machine_data):
    data = [{'key': key, 'data': str(data)} for key, data in machine_data.items()]
    url = '{org}/resource_group/{name}/register_static'.format(org=org, name=group['name'])
    result = ctx.obj.handle_api(ctx.obj, ctx.obj.session, 'post', url, dict(data=data))
    return result


@resource_commands.command('add_to_static_cloud_group', help="Add exsisting cloud machine to managed resource group")
@click.pass_context
@click.option('--org', type=str, help='organization to use')
@click.option('--name', type=str, help='configuration name')
@click.option('--group-name', type=str, help='Target group name. Specifying non-existing group will create one')
@click.option('--silent/--no-silent', default=False, help='skip prompts with smart defaults')
def setup_static_template(ctx, org, **kwargs):
    group = static_resource_groups(ctx, org, kwargs)
    machine = select_unmanaged_machine(ctx, org, group['cloud_type'], group['cloud_connector'], kwargs)
    if machine is None:
        click.echo('All of your machines are manged.')
        return
    res = register_static_unmanaged_machine(ctx, org, group, machine)
    click.echo(res)


@resource_commands.command('restore_aws_template', help="restores predefined cloud configuration")
@click.pass_context
@click.option('--org', type=str, help='organization to use', required=True)
@click.option('--arn', type=str, help='arn of the KMS encryption key', required=True)
@click.option('--ssh', type=(str, str, str), help='ssh key data', required=True)
@click.option('--mali', type=(str, str, str), help='mali config data', required=True)
@click.option('--prefix', type=str, help='mali prefix type', required=False)
@click.option('--token', type=str, help='mali prefix type', required=True)
@click.option('--rm-socket-server', type=str, help='web socket server', required=True)
@click.option('--rm-manager-image', type=str, required=True)
@click.option('--rm-config-volume', type=str, required=True)
@click.option('--rm-container-name', type=str, required=True)
@click.option('--region', envvar='REGION', type=str, required=True)
def apply_aws_template(ctx, org, arn, ssh, mali, prefix, token, rm_socket_server, rm_manager_image, rm_config_volume, rm_container_name, region):
    from .legit.context import Expando

    if prefix == str(None):
        prefix = None

    click.echo('decrypting data')
    ssh_key = decrypt_string_with_boto_kms(ssh, region)
    mali_data = decrypt_string_with_boto_kms(mali, region)
    try_import_docker_and_crypto()
    docker_client = validate_and_get_docker_client()

    click.echo('building installation config')
    config = Expando()
    config.rm_socket_server = rm_socket_server
    config.rm_manager_image = rm_manager_image
    config.rm_config_volume = rm_config_volume
    config.rm_container_name = rm_container_name

    click.echo('pulling RM')
    pull_ml_image(ctx.obj, docker_client)

    click.echo('killing RM')
    validate_running_resource_manager(config, docker_client, True)

    click.echo('building volume')
    if _docker_present(docker_client.volumes.get, rm_config_volume):
        docker_client.volumes.get(rm_config_volume).remove(force=True)
    docker_client.volumes.create(rm_config_volume)
    _apply_config_to_volume(config, docker_client, ssh_key, token, prefix=prefix, config_data=mali_data)

    click.echo('Clear containers')
    for container in docker_client.containers.list():
        if container.name == rm_container_name:
            click.echo("\t  KILL: %s" % container.id)
            container.kill()

    for container in docker_client.containers.list(all=True):
        if container.name == rm_container_name:
            click.echo("\t  REMOVE: %s" % container.id)
            container.remove(force=True)

    click.echo('Start RM:')
    inst = _run_resource_manager(config, docker_client)
    click.echo('The resource manager is configured and running %s' % inst.id)
    click.echo('for logs run: docker logs -f %s ' % rm_container_name)
