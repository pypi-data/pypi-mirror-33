import json
import requests

import urllib3

from cis_client.lib import base_http_client


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class WorkflowClient(base_http_client.BaseClient):
    def __init__(self, north_host, insecure=False):
        super(WorkflowClient, self)
        self.north_host = north_host
        self.insecure = insecure

    def list(self, auth_token):
        endpoint = self.get_endpoint()
        response = requests.get(
            endpoint,
            verify=(not self.insecure),
            headers={"X-Auth-Token": auth_token}
        )
        response.raise_for_status()
        return json.loads(response.content)

    def get_endpoint(self):
        endpoint = '{north_host}/workflows'.format(north_host=self.north_host)
        return endpoint


@base_http_client.with_auth
def get_workflows(north_host, **kwargs):
    """Gets workflows

    :param north_host:
    :param kwargs: can contains
        - insecure: True if SSL verification must be skipped
        - aaa_host: AAA host, optional
        - username: username, optional
        - password: password, optional
        - token: auth token, must be specified if aaa_host,
                 username and password is not specified
    :return: list of workflows
    """
    workflow_client = WorkflowClient(north_host, insecure=kwargs['insecure'])
    workflows = workflow_client.list(kwargs['token'])
    return workflows
