from __future__ import unicode_literals

import click

from cis_client import cli
from cis_client.commands import utils
from cis_client.lib.cis_north import profile_client
from cis_client.commands import printer


@click.group()
def profile_cli():
    pass


@profile_cli.command('list', context_settings=utils.CONTEXT_SETTINGS, help='Lists profiles.')
@click.option('--workflow', required=True, type=click.STRING,
              help='Workflow.')
@utils.add_host_options
@utils.add_auth_options
@utils.add_credentials_options
@cli.pass_context
@utils.handle_exceptions
@utils.check_cis_version
def list_(ctx, **kwargs):
    profiles = profile_client.get_profiles(
        kwargs.pop('north_host'), kwargs.pop('workflow'), **kwargs)
    profiles = [{'id': profile['id'], 'label': profile['label']}for profile in profiles]
    printer.print_json_as_table(profiles, order_fields=['id', 'label'])
