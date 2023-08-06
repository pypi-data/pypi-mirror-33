import json
import requests

import urllib3

from cis_client.lib.cis_north import base_client


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class IngestPointClient(base_client.BaseClient):
    def __init__(self, north_host, insecure=False):
        super(IngestPointClient, self)
        self.north_host = north_host
        self.insecure = insecure

    def get_ingest_point(self, auth_token, ingest_point, **kwargs):
        endpoint = self.get_endpoint(ingest_point)
        response = requests.get(
            endpoint,
            verify=(not self.insecure),
            headers={"X-Auth-Token": auth_token},
            params=self.get_auth_params(**kwargs)
        )
        response.raise_for_status()
        return json.loads(response.content)

    def get_endpoint(self, ingest_point):
        endpoint = '{north_host}/ingest_points/{ingest_point}'.format(
            north_host=self.north_host,
            ingest_point=ingest_point
        )
        return endpoint
