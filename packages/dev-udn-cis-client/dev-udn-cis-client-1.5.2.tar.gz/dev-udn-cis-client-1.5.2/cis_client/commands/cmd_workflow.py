from __future__ import unicode_literals

import click

from cis_client import cli
from cis_client.commands import utils
from cis_client.lib.cis_north import workflow_client
from cis_client.commands import printer


@click.group()
def workflow_cli():
    pass


@workflow_cli.command('list', context_settings=utils.CONTEXT_SETTINGS, help='Lists workflows.')
@click.option('--wrap-table', default=False, type=click.BOOL,
              help='Wrap result table to fit with screen.')
@utils.add_host_options
@utils.add_credentials_options
@cli.pass_context
@utils.handle_exceptions
@utils.check_cis_version
def list_(ctx, **kwargs):
    worklows = workflow_client.get_workflows(
        kwargs.pop('north_host'), **kwargs)
    worklows = [{'workflow': workflow}for workflow in worklows]
    printer.print_json_as_table(
        worklows,
        header_field_map={
            'workflow': 'Workflow'
        },
        inner_row_border=False
    )
