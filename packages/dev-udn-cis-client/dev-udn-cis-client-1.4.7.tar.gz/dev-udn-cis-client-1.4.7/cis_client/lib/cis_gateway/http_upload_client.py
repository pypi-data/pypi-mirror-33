import requests
import os.path

from cis_client.lib.cis_north import access_key_client
from cis_client.lib import chunk_upload


class ContentClient(object):
    api_version = 'v1'

    def __init__(self, hostname, port, schema='http', insecure=False):
        super(ContentClient, self).__init__()
        self.schema = schema
        self.hostname = hostname
        self.port = port
        self.insecure = insecure

    def get_endpoint(self, dest_path):
        endpoint = "{schema}://{hostname}:{port}/{api_version}/{dest_path}".format(
            schema=self.schema,
            hostname=self.hostname,
            port=self.port,
            api_version=self.api_version,
            dest_path=dest_path)
        return endpoint

    def upload(self, access_key, path, dest_path, progress_callback=None):
        uploader = chunk_upload.UploadChunks(path, progress_callback=progress_callback)
        response = requests.post(
            self.get_endpoint(dest_path),
            verify=(not self.insecure),
            headers={"X-Auth-Token": access_key},
            data=chunk_upload.IterableToFileAdapter(uploader))
        response.raise_for_status()
        return response


def http_upload(aaa_host, username, password, north_host,
                ingest_point, path, destination_path=None,
                progress_callback=None, **kwargs):
    """HTTP upload"""

    if destination_path is None:
        destination_path = os.path.basename(path)

    ingest_point_info, access_key = access_key_client.get_access_key(
        aaa_host, username, password, north_host, ingest_point, **kwargs)

    gateway_hostname = ingest_point_info['gateway']['hostname']
    gateway_port = ingest_point_info['gateway']['protocols']['http']['port']
    content_client = ContentClient(gateway_hostname, gateway_port, insecure=kwargs['insecure'])
    return content_client.upload(access_key, path, destination_path, progress_callback)
