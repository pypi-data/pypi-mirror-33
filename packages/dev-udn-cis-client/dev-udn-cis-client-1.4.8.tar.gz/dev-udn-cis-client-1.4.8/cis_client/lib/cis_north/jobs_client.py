import json
import requests
import urllib3

from cis_client.lib.aaa.auth_client import AuthClient

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class JobsClient(object):
    jobs_endpoint = 'jobs'

    def __init__(self, north_host, token, insecure=False):
        super(JobsClient, self).__init__()
        self.jobs_endpoint_url = "{}/{}".format(north_host, self.jobs_endpoint)
        self.token = token
        self.insecure = insecure

    def get_auth_header(self):
        return {AuthClient.auth_header: self.token}

    def list(self, **kwargs):
        query_jobs_url = self.compose_query_jobs_url(**kwargs)
        get_jobs_response = requests.get(
            query_jobs_url,
            verify=(not self.insecure),
            headers=self.get_auth_header())
        get_jobs_response.raise_for_status()
        return json.loads(get_jobs_response.content)

    def compose_query_jobs_url(self, **kwargs):
        join_values = lambda list_values: ','.join(list_values)
        query_params = []
        if kwargs.get('job_type') is not None:
            query_params.append('type=%s' % join_values(kwargs['job_type']))
        if kwargs.get('path') is not None:
            query_params.append('filename=%s' % join_values(kwargs['path']))
        if kwargs.get('file_basename') is not None:
            query_params.append(
                'filter_by=file_basename&filter_value=%s' % kwargs['file_basename'])
        if kwargs.get('case_sensitive_file_basename') is not None:
            query_params.append('filter_case_sensitive=%s' % 'true' if kwargs['filter_case_sensitive'] else 'false')
        if kwargs.get('state') is not None:
            query_params.append('state=%s' % join_values(kwargs['state']))
        if kwargs.get('state_simple') is not None:
            query_params.append('state_simple=%s' % join_values(kwargs['state_simple']))
        if kwargs.get('aggregated_status') is not None:
            query_params.append('aggregated_status={}'.format(kwargs['aggregated_status']))
        if kwargs.get('fields') is not None:
            query_params.append('fields=%s' % join_values(kwargs['fields']))
        if kwargs.get('with_children') is not None:
            query_params.append('with_children=%s' % 'true' if kwargs['with_children'] else 'false')
        if kwargs.get('ingest_point') is not None:
            query_params.append('ingest_point=%s' % kwargs['ingest_point'])
        if kwargs.get('root_only') is not None:
            query_params.append('root_only=%s' % 'true' if kwargs['root_only'] else 'false')
        if kwargs.get('sort_by') is not None:
            query_params.append('sort_by=%s' % kwargs['sort_by'])
        if kwargs.get('sort_order') is not None:
            query_params.append('sort_order=%s' % kwargs['sort_order'])
        if kwargs.get('offset') is not None:
            query_params.append('offset=%s' % str(kwargs['offset']))
        if kwargs.get('page_size') is not None:
            query_params.append('page_size=%s' % str(kwargs['page_size']))
        if kwargs.get('brand_id') is not None:
            query_params.append('brand_id=%s' % str(kwargs['brand_id']))
        if kwargs.get('account_id') is not None:
            query_params.append('account_id=%s' % str(kwargs['account_id']))
        if kwargs.get('group_id') is not None:
            query_params.append('group_id=%s' % str(kwargs['group_id']))
        if kwargs.get('latest') is not None and kwargs['latest']:
            query_params.append('latest=%s' % str(kwargs['latest']))
        url = '{jobs_endpoint_url}?{params}'.format(
            jobs_endpoint_url=self.jobs_endpoint_url,
            params='&'.join(query_params)
        )
        return url


def get_jobs(aaa_host, username, password, north_host, **kwargs):
    """Gets jobs

    :param aaa_host:
    :param username:
    :param password:
    :param north_host:
    :param kwargs: can contains
        - brand_id: Brand ID
        - account_id: account ID
        - group_id: group ID
        - job_type: list of job types like ['abr'] or ['http-push'] or ['abr', 'http-push'] or other
        - path: list of exact paths like ['root_dir/sub_dir/vid.mp4']
        - file_basename: partial match of filename.
            Filtering by filename allows to specify the beginning of filename only.
        - case_sensitive_file_basename: True if filtering is case sensitive.
        - state: list of allowed states. Allowed states are:
            pending
            running
            cancelling
            paused
            completed
            failed
        - aggregated_status: aggregated status. Allowed states are:
            uploading
            processing
            local_done
            global_done
            failed
        - fields: list of fields in response like ['id', 'filename'].
        - with_children: if True will return whole job tree which contains information
            about children and children of children
        - ingest_point: ingest point id
        - root_only: returns root jobs only
        - sort_by: field name to sort by
        - sort_order: can be 'asc' or 'desc'
        - offset: offset
        - page_size: size of page, -1 means all rows
        - insecure: True if SSL verification must be skipped

    :return: list of jobs
    """
    auth_client = AuthClient(aaa_host, insecure=kwargs['insecure'])
    token = auth_client.get_token(username, password)
    jobs_client = JobsClient(north_host, token, insecure=kwargs['insecure'])
    return jobs_client.list(**kwargs)
