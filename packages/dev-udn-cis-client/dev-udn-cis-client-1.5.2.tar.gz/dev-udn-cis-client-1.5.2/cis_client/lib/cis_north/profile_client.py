import json
import requests

import urllib3

from cis_client.lib import base_http_client
from cis_client.lib.aaa import auth_client


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ProfileClient(base_http_client.BaseClient):
    def __init__(self, north_host, insecure=False):
        super(ProfileClient, self)
        self.north_host = north_host
        self.insecure = insecure

    def list(self, auth_token, workflow, **kwargs):
        endpoint = self.get_endpoint(workflow)
        response = requests.get(
            endpoint,
            verify=(not self.insecure),
            headers={"X-Auth-Token": auth_token},
            params=self.get_auth_params(**kwargs)
        )
        response.raise_for_status()
        return json.loads(response.content)

    def get_endpoint(self, workflow):
        endpoint = '{north_host}/workflows/{workflow}/profiles'.format(
            north_host=self.north_host,
            workflow=workflow
        )
        return endpoint


@base_http_client.with_auth
def get_profiles(north_host, workflow, **kwargs):
    """Gets profiles

    :param north_host:
    :param kwargs: can contains
        - insecure: True if SSL verification must be skipped
        - group_id: group ID
        - aaa_host: AAA host, optional
        - username: username, optional
        - password: password, optional
        - token: auth token, must be specified if aaa_host,
                 username and password is not specified
    :return: list of profiles
    """
    profile_client = ProfileClient(north_host, insecure=kwargs['insecure'])
    params = {}
    if 'group_id' in kwargs:
        params['group_id'] = kwargs['group_id']
    profiles = profile_client.list(kwargs['token'], workflow, **params)
    return profiles
