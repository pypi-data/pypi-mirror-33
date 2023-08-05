from mali_commands.resources import cloud_connector_defaults, pop_key_or_prompt_if, get_ssh_path, encrypt_string_with_boto_kms, ssh_load_key
from six.moves.urllib import parse
from mali_commands.commons import output_result
import uuid
from mali_commands.utilities.ssh_key import SshKey
import logging
import click
from .sts import Sts
from .cloud_formation import Cf
from .iam import Iam
from click import exceptions
from .base_aws import AwsBase


class AwsContext:
    def __init__(self, ctx, kwargs):
        self.org = kwargs['org']
        self.ctx = ctx

        self.sts = Sts(ctx.obj.aws, self.org)
        self.whoami = self.sts.whoami()
        self.account_id = self.whoami['Account']
        self.region = self.ctx.obj.aws.region
        logging.debug('Org: %s, AWS account id: %s', self.org, self.account_id)
        self.auth_state = None
        self.refresh_auth_state()
        self.kwargs = kwargs
        self.cf = Cf(self.ctx.obj.aws, self.org)

    def _handle_api_call(self, method, url, data=None):
        return self.ctx.obj.handle_api(self.ctx.obj, self.ctx.obj.session, method, url, data)

    def refresh_auth_state(self):
        self.auth_state = self._handle_api_call('get', '{}/aws/authorisation_status/{}'.format(self.org, self.account_id))
        logging.info('AWS auth status', self.auth_state)
        if self.auth_state.get('auth_region') != self.ctx.obj.aws.region:
            self.region = self.auth_state.get('auth_region')
            self.ctx.obj.aws.region = self.region
            logging.info('AWS region changed to %s', self.region)
        return self.auth_state

    def encrypt_and_send_connector(self):
        if self._authorised_and_configured():
            return

        self._prompt_for_ssh_if_needed()
        self._authorise_if_needed()
        kms_arn = self.auth_state.pop('encryption_key', None)
        if not kms_arn:
            raise click.exceptions.ClickException('You are authorised but have no KMS key configured. Please contact MissingLinkAi')

        self._init_prepare_connector_message(kms_arn, set_ssh=not self.auth_state['ssh_present'], set_mali=not self.auth_state['mali_config'])

        self.refresh_auth_state()

    def _authorised_and_configured(self):
        return self.auth_state['authorised'] and self.auth_state['ssh_present'] and self.auth_state['mali_config']

    def _prompt_for_ssh_if_needed(self):
        if self.auth_state['authorised'] and self.auth_state['ssh_present']:
            return

        self._pre_apply_default_ssh_key()
        has_key = False
        while not has_key:
            has_key = self._try_read_key()

    def _pre_apply_default_ssh_key(self):
        if 'ssh_key_path' not in self.kwargs:
            self.kwargs['ssh_key_path'] = get_ssh_path()
            logging.info('Using %s as default ssh path', self.kwargs['ssh_key_path'])

    def _try_read_key(self):
        try:
            self.kwargs['ssh_key_path'] = pop_key_or_prompt_if(self.kwargs, 'ssh_key_path', text='SSH key path [--ssh-key-path]', default=get_ssh_path())
            self.kwargs['ssh_key'] = SshKey(self.kwargs['ssh_key_path'])
            self.kwargs['ssh_private'] = self.kwargs['ssh_key'].private_key()
            self.kwargs['ssh_public'] = self.kwargs['ssh_key'].public_key()
            return True

        except Exception as e:
            click.echo('Failed to read ssh key from %s. Please check the path and try again. %s' % (self.kwargs['ssh_key_path'], str(e)))

        return False

    def _authorise_if_needed(self):
        if not self.auth_state['authorised']:
            self._ensure_role_absent()
            return self._get_submit_and_register_template('authorise_cf', 'ML-AUTH', parameters={'SshPublicKey': self.kwargs['ssh_public']})

    def _ensure_role_absent(self):
        iam = Iam(self.ctx.obj.aws, self.org)
        ml_role_name = 'MissingLinkResourceManager-{org}'.format(org=self.org)
        cur_role = iam.get_role(ml_role_name)
        if cur_role is not None:
            logging.info('_has_auth_stack: stack present %s', cur_role)
            raise exceptions.ClickException('Role %s already exists in your AWS account. Role ID: %s. Please contact MissingLinkAi' % (ml_role_name, cur_role['Role']['RoleId']))

    def _get_submit_and_register_template(self, cf_command, stack_name, parameters=None):
        stack_name = '{}-{}'.format(stack_name, self.org)
        self._ensure_stack_absent(stack_name)

        result = self._handle_api_call('get', '{}/aws/{}/{}'.format(self.org, cf_command, self.account_id))
        logging.debug(result)
        tags = AwsBase.tuple_array_do_dict(result['tags'], key='key', value='value')
        template = result['template']
        offer_id = result['offering_id']
        cf_response = self.cf.create(stack_name, stack_data=template, tags=tags, parameters=parameters)
        stack_id = cf_response['StackId']
        result = self._handle_api_call('put', '{}/aws/register_cf_stack/{}/{}?{}'.format(self.org, self.account_id, offer_id, parse.urlencode({'stack': stack_id})), {})
        self._wait_stack_for_complete(stack_name)
        self.refresh_auth_state()

    def _ensure_stack_absent(self, stack_name):
        cur_stack = self.cf.get(stack_name)
        if cur_stack is not None:
            logging.info('_has_stack_name: stack present %s', cur_stack)
            raise exceptions.ClickException('%s stack already exists in your AWS account with State: %s. Please contact MissingLinkAi' % (stack_name, cur_stack['status']))

    def _wait_stack_for_complete(self, stack):
        from time import sleep

        cur_stack = self.cf.get(stack)
        while not cur_stack['status'].lower().endswith('complete'):
            click.echo('%s: %s' % (stack, cur_stack['status']))
            resources = self.cf.resources(stack)
            output_result(self.ctx, resources)
            sleep(5)
            click.echo(chr(27) + "[2J")
            cur_stack = self.cf.get(stack)

        return self.cf.get(stack)

    def _init_prepare_connector_message(self, kms_key_arn, set_ssh, set_mali):
        template, config_data = cloud_connector_defaults(self.ctx, cloud_type='aws', kwargs=dict(connector=self.account_id))
        if set_ssh:
            ssh_key_path = pop_key_or_prompt_if(self.kwargs, 'ssh_key_path', text='SSH key path [--ssh-key-path]', default=get_ssh_path())
            ssh_key = ssh_load_key(ssh_key_path)
            ssh = encrypt_string_with_boto_kms(ssh_key, kms_key_arn)
            template['ssh'] = ssh
        if set_mali:
            mali = encrypt_string_with_boto_kms(config_data, kms_key_arn)
            template['mali'] = mali

        template['cloud_data'] = {}
        url = '{org}/cloud_connector/{name}'.format(org=self.org, name=template['name'])
        response = self._handle_api_call('post', url, template)
        print(response)

    def setup_vpc_if_needed(self):

        if self._is_vpc_active():
            return

        self._get_submit_and_register_template('new_vpc_cf', 'ML-VPC')

    def _is_vpc_active(self):
        if not self.region:
            return len(self.auth_state.get('vpc_regions', [])) > 0

        return self.region is not None and self.region in self.auth_state.get('vpc_regions', [])

    def setup_s3_if_needed(self, force=False):

        if not force and int(self.auth_state.get('s3_count') or 0) > 0:
            return

        return self._get_submit_and_register_template('new_s3_cf', 'ML-S3-{}'.format(uuid.uuid4().hex[:3].lower()))
