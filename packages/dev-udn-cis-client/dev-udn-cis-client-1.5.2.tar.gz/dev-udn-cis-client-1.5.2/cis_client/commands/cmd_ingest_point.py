from __future__ import unicode_literals

import collections
import json

import click

from cis_client import cli
from cis_client.commands import utils
from cis_client.lib.cis_north import ingest_point_client
from cis_client.commands import printer


@click.group()
def ingest_point_cli():
    pass


@ingest_point_cli.command('list', context_settings=utils.CONTEXT_SETTINGS, help='Lists ingest points.')
@click.option('--page-size', type=click.INT, default=1000,
              help='Max size of data that will be returned in response.')
@click.option('--offset', type=click.INT,
              help='Begin result set at this index.')
@utils.add_host_options
@utils.add_auth_options
@utils.add_credentials_options
@cli.pass_context
@utils.handle_exceptions
@utils.check_cis_version
def list_(ctx, **kwargs):
    ingest_points = ingest_point_client.list_ingest_points(kwargs.pop('north_host'), **kwargs)
    ingest_points = [{'ingest_point': ingest_point} for ingest_point in ingest_points]
    printer.print_json_as_table(
        ingest_points,
        header_field_map={
            'ingest_point': 'Ingest point'
        },
        inner_row_border=False
    )


@ingest_point_cli.command('show', context_settings=utils.CONTEXT_SETTINGS, help='Shows ingest point info.')
@click.option('--ingest-point', required=True, type=click.STRING, help='Ingest point')
@click.option('--wrap-table', default=True, type=click.BOOL,
              help='Wrap result table to fit with screen.')
@utils.add_host_options
@utils.add_auth_options
@utils.add_credentials_options
@cli.pass_context
@utils.handle_exceptions
@utils.check_cis_version
def show(ctx, **kwargs):
    ingest_point = ingest_point_client.get_ingest_point(
        kwargs.pop('north_host'), kwargs.pop('ingest_point'), **kwargs)

    # remove redundant info
    if ingest_point.get('workflow', {}).get('profiles'):
        del ingest_point['workflow']['profiles']
    for key in ('auth_info', 'storage_desc', 'is_system', 'document_type'):
        if key in ingest_point:
            ingest_point.pop(key)
    # pretty print json inside value
    for key in ingest_point.keys():
        ingest_point[key] = json.dumps(ingest_point[key], indent=2, separators=(', ', ': '))
    # order keys
    ingest_ordered_dict = collections.OrderedDict()
    ingest_ordered_dict['ingest_point_id'] = ingest_point.pop('ingest_point_id')
    ingest_ordered_dict['clusters'] = ingest_point.pop('clusters')
    ingest_ordered_dict['gateway'] = ingest_point.pop('gateway')
    ingest_ordered_dict.update(ingest_point)

    ingest_point_table = [{'key': key, 'value': value} for key, value in ingest_ordered_dict.items()]
    printer.print_json_as_table(
        ingest_point_table,
        not_print_header=True,
        order_fields=('key', 'value'),
        wrap_text=kwargs['wrap_table']
    )


@ingest_point_cli.command('add', context_settings=utils.CONTEXT_SETTINGS, help='Adds ingest point.')
@click.option('--ingest-point', required=True, type=click.STRING, help='Ingest point')
@click.option('--clusters', required=True, type=click.STRING, help='Comma separated list of clusters.')
@click.option('--workflow-id', required=True, type=click.STRING, help='Workflow ID. For example "abr" or "ism_only".')
@click.option('--profile-ids', type=click.STRING, help='Comma separated list of profile IDs.')
@click.option('--estimated-usage', type=click.INT, help='Estimated usage.')
@utils.add_host_options
@utils.add_auth_options
@utils.add_credentials_options
@cli.pass_context
@utils.handle_exceptions
@utils.check_cis_version
def add(ctx, **kwargs):
    clusters = kwargs.pop('clusters').split(',')
    workflow_id = kwargs.pop('workflow_id')
    if 'profile_ids' in kwargs:
        kwargs['profile_ids'] = kwargs.pop('profile_ids').split(',')
    ingest_point_client.add_ingest_point(
        kwargs.pop('north_host'), kwargs.pop('ingest_point'), clusters, workflow_id, **kwargs)
    utils.display('Ingest point was successfully created.')


@ingest_point_cli.command('delete', context_settings=utils.CONTEXT_SETTINGS, help='Deletes ingest point.')
@click.option('--ingest-point', required=True, type=click.STRING, help='Ingest point')
@utils.add_host_options
@utils.add_auth_options
@utils.add_credentials_options
@cli.pass_context
@utils.handle_exceptions
@utils.check_cis_version
def delete(ctx, **kwargs):
    ingest_point_client.remove_ingest_point(
        kwargs.pop('north_host'), kwargs.pop('ingest_point'), **kwargs)
    utils.display('Ingest point was successfully deleted.')
