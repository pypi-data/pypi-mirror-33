import errno
import os.path
import paramiko

from cis_client.lib.cis_north import access_key_client
from cis_client import exception


def sftp_file_exist(sftp_client, destination_path):
    try:
        sftp_client.stat(destination_path)
    except IOError as e:
        if e.errno == errno.ENOENT:
            return False
        raise
    return True


def sftp_upload(aaa_host, username, password, north_host,
                ingest_point, path, destination_path=None,
                progress_callback=None, **kwargs):
    """SFTP upload"""

    if destination_path is None:
        destination_path = os.path.basename(path)

    ingest_point_info, access_key = access_key_client.get_access_key(
        aaa_host, username, password, north_host, ingest_point, **kwargs)

    gateway_hostname = ingest_point_info['gateway']['hostname']
    gateway_port = ingest_point_info['gateway']['protocols']['sftp']['port']

    with paramiko.Transport((gateway_hostname, gateway_port)) as transport:
        transport.connect(username=username, password=access_key)
        with paramiko.SFTPClient.from_transport(transport) as sftp_client:
            if sftp_file_exist(sftp_client, destination_path):
                raise exception.UploadConflictException(destination_path)
            sftp_client.put(path, destination_path, callback=progress_callback)
