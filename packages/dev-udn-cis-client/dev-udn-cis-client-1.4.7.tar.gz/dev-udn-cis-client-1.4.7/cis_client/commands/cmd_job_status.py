import click

from cis_client import cli
from cis_client.commands import utils
from cis_client.lib.cis_north import jobs_client
from cis_client import exception
from cis_client.commands import printer


@click.command('job_status', context_settings=utils.CONTEXT_SETTINGS, help='Gets status of jobs.')
@click.option('--ingest-point', type=click.STRING,
              help='Ingest point')
@click.option('--path-list-file', type=click.Path(resolve_path=True),
              help='Path to file that contains list of full paths to content separated by new line symbol.')
@click.option('--path-list', type=click.STRING,
              help='Comma separated list of full paths to content.')
@click.option('--job-type', type=click.STRING,
              help='Job type like "abr" or "http-push" or "abr,http-push" or other')
@click.option('--state', type=click.STRING,
              help='an integer representation of composited states: pending, ready, scheduling, starting, '
                   'running, suspending, pausing, resuming, cancelling, completed, suspended, paused, failed, '
                   'cancelled, done. General purpose - for debugging.')
@click.option('--state-simple', type=click.STRING,
              help='Human readable status. Can contain values: "pending", "running", "cancelling", '
                   '"paused", "completed", "failed" in job query response.')
@click.option('--aggregated-status', type=click.STRING,
              help='Aggregated status. Can contain values: "uploading", "processing", "local_done", '
                   '"global_done", "failed".')
@click.option('--latest', type=click.BOOL, default=False,
              help='Boolean. If true shows only the latest job related to specific filename and type of job.')
@click.option('--fields', type=click.STRING, default='id,filename,progress,state,name',
              help='Comma separated list of fields that will be in response')
@click.option('--root-only', type=click.BOOL, default=True,
              help='Boolean. Shows root only or all jobs.')
@click.option('--page-size', type=click.INT, default=1000,
              help='Max size of data that will be returned in response.')
@click.option('--offset', type=click.INT,
              help='Begin result set at this index.')
@click.option('--wrap-table', default=True, type=click.BOOL,
              help='Wrap result table to fit with screen.')
@utils.add_host_options
@utils.add_auth_options
@utils.add_credentials_options
@cli.pass_context
@utils.handle_exceptions
@utils.check_cis_version
def cli(ctx, **kwargs):
    split_values = lambda comma_separated_values: list(map(str.strip, map(str, comma_separated_values.split(','))))
    if kwargs.get('job_type') is not None:
        kwargs['job_type'] = split_values(kwargs['job_type'])
    if kwargs.get('path_list_file') is not None and kwargs.get('path_list') is not None:
        raise exception.OptionException("Please specify only one option --path-list-file or --path-list")
    if kwargs.get('path_list_file') is not None:
        with open(kwargs['path_list_file']) as f:
            file_content = f.read()
        path = map(str.strip, file_content.strip().split('\n'))
        kwargs['path'] = list(path)
    if kwargs.get('path_list') is not None:
        kwargs['path'] = split_values(kwargs['path_list'])
    if kwargs.get('state') is not None:
        kwargs['state'] = split_values(kwargs['state'])
    if kwargs.get('state_simple') is not None:
        kwargs['state_simple'] = split_values(kwargs['state_simple'])
    if kwargs.get('fields') is not None:
        kwargs['fields'] = split_values(kwargs['fields'])
    kwargs['with_children'] = True
    jobs = jobs_client.get_jobs(
        kwargs.pop('aaa_host'), kwargs.pop('username'), kwargs.pop('password'), kwargs.pop('north_host'), **kwargs)
    for job_data in jobs['data']:
        if 'progress' in job_data:
            try:
                job_data['progress'] = float(job_data['progress']) * 100
            except (ValueError, TypeError):
                job_data['progress'] = ''
        if 'children_jobs' in job_data and kwargs.get('path'):
            job_data['subjobs progress'] = ''
            if job_data.get('state_simple') == 'completed':
                # do not show subjobs progress for completed tasks
                continue
            for subjob in job_data['children_jobs']:
                job_data['subjobs progress'] += '"{}" has status "{}"\n'.format(
                    subjob.get('name'), subjob.get('simple_state') or subjob.get('state'))
        if 'data' in job_data and job_data['data'] and 'aggregated_status' in job_data['data']:
            job_data['data.aggregated_status'] = job_data.get('data', {}).get('aggregated_status', '')
    table_fields = kwargs.get('fields')
    if table_fields and kwargs.get('path'):
        table_fields.append('subjobs progress')
    if ('state' in table_fields and
            jobs['data'] and jobs['data'][0].get('state_simple')):  # try to do it independently from CIS version
        table_fields = list(map(lambda field: 'state_simple' if field == 'state' else field, table_fields))
    printer.print_json_as_table(
        jobs['data'],
        header_field_map={
            'state_simple': 'state', 'data.aggregated_status': 'aggregated status'},
        order_fields=table_fields,
        wrap_text=kwargs['wrap_table'])
