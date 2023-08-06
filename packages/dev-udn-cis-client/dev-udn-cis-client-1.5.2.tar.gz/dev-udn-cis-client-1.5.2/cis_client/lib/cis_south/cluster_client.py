import json
import requests
import urllib3

from cis_client.lib import base_http_client


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ClusterClient(object):
    def __init__(self, south_host, insecure=False):
        super(ClusterClient, self)
        self.south_host = south_host
        self.insecure = insecure

    def list(self, auth_token):
        endpoint = self.get_endpoint()
        response = requests.get(
            endpoint,
            verify=(not self.insecure),
            headers={"X-Auth-Token": auth_token},
            params={'filter': 'enabled'}
        )
        response.raise_for_status()
        return json.loads(response.content)

    def get_endpoint(self):
        endpoint = '{south_host}/clusters'.format(south_host=self.south_host)
        return endpoint


@base_http_client.with_auth
def list_clusters(south_host, insecure=False, **kwargs):
    """Gets clusters

    :param south_host:
    :param insecure: True if SSL verification must be skipped
    :param kwargs:
        - aaa_host: AAA host, optional
        - username: username, optional
        - password: password, optional
        - token: auth token, must be specified if aaa_host,
                 username and password is not specified
    :return: list of clusters
    """
    cluster_client = ClusterClient(south_host, insecure=insecure)
    clusters = cluster_client.list(kwargs['token'])
    return clusters
