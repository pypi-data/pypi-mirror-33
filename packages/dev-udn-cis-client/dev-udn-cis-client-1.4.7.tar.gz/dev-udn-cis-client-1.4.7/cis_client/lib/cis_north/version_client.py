import json
import requests
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def get_cis_version(north_host, **kwargs):
    """Gets CIS version

    :param north_host:
    :param kwargs: can contains
        - insecure: True if SSL verification must be skipped
    :return: string CIS version
    """

    version_endpoint_url = "{}/version".format(north_host)
    response = requests.get(
        version_endpoint_url,
        verify=True if not kwargs.get('insecure') else False)
    response.raise_for_status()
    return json.loads(response.content)
