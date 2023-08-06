from __future__ import unicode_literals

import click

from cis_client import cli
from cis_client.commands import utils
from cis_client.lib.cis_south import cluster_client
from cis_client.commands import printer


@click.group()
def cluster_cli():
    pass


@cluster_cli.command('list', context_settings=utils.CONTEXT_SETTINGS, help='Lists clusters.')
@click.option('--south-host', required=True, type=click.STRING, help='CIS South hostname.')
@utils.add_host_options
@utils.add_credentials_options
@cli.pass_context
@utils.handle_exceptions
@utils.check_cis_version
def list_(ctx, **kwargs):
    clusters = cluster_client.list_clusters(kwargs.pop('south_host'), **kwargs)
    clusters = [{'cluster': cluster}for cluster in clusters]
    printer.print_json_as_table(
        clusters,
        header_field_map={
            'cluster': 'Cluster'
        },
        inner_row_border=False
    )
