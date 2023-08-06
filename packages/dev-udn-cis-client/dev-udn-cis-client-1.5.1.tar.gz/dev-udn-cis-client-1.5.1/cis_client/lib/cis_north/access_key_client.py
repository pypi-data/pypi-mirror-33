import json
import requests
import urllib3

from cis_client.lib import base_http_client
from cis_client.lib.cis_north.ingest_point_client import IngestPointClient


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class AccessKeyClient(base_http_client.BaseClient):
    def __init__(self, north_host, insecure=False):
        self.north_host = north_host
        self.insecure = insecure

    def get_endpoint(self, ingest_point):
        endpoint = '{north_host}/ingest_points/{ingest_point}/access_keys'.format(
            north_host=self.north_host,
            ingest_point=ingest_point
        )
        return endpoint

    def create_access_key(self, auth_token, ingest_point, **kwargs):
        endpoint = self.get_endpoint(ingest_point)
        response = requests.post(
            endpoint,
            verify=(not self.insecure),
            headers={"X-Auth-Token": auth_token},
            params=self.get_auth_params(**kwargs)
        )
        response.raise_for_status()
        return json.loads(response.content)


@base_http_client.with_auth
def get_access_key(north_host, ingest_point, **kwargs):
    ingest_point_client = IngestPointClient(north_host, insecure=kwargs['insecure'])
    ingest_point_info = ingest_point_client.get(kwargs['token'], ingest_point, **kwargs)

    access_key_client = AccessKeyClient(north_host, insecure=kwargs['insecure'])
    access_key = access_key_client.create_access_key(kwargs['token'], ingest_point, **kwargs)
    return ingest_point_info, access_key
