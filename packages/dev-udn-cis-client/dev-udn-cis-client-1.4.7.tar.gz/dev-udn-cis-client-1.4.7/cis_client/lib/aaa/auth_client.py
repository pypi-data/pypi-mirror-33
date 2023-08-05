import requests
import json
import os
import urllib

from cis_client.lib.aaa.token import Token


class AuthClient(object):

    _token_cls = Token
    restapi_version = "v2"
    token_endpoint = "tokens"
    auth_header = "X-Auth-Token"

    @staticmethod
    def _compose_endpoint_url(token_endpoint_url, token, params):
        endpoint_url = os.path.join(token_endpoint_url, token)
        if params:
            query_string = urllib.urlencode(params)
            endpoint_url = ''.join([endpoint_url, '?', query_string])
        return endpoint_url

    def validate_token(self, token, user_token=None, params=None):
        endpoint_url = self._compose_endpoint_url(
            self._auth_server.token_endpoint_url, token, params)
        token_response = requests.get(
            endpoint_url,
            verify=(not self._insecure),
            headers = self.get_auth_header(user_token or token))
        token_response.raise_for_status()

        try:
            token_ctx = json.loads(token_response.content)
            token_obj = self._token_cls(token, token_ctx, service_name=self._service_name)
        except ValueError:
            raise
        except Exception as token_key_ctx_err:
            raise Exception("Invalid token context: {}".format(token_key_ctx_err))

        return token_obj

    def __init__(self, aaa_hostname, service_name=None, insecure=False):
        self._service_name = service_name
        self._token_endpoint_url = "{}/{}/{}".format(
            aaa_hostname, self.restapi_version, self.token_endpoint)
        self._insecure = insecure

    def get_auth_header(self, token):
        return {self.auth_header: token}

    def get_token_with_context(self, token, context):
        post_token_response = requests.post(self._token_endpoint_url,
                                            headers=self.get_auth_header(token),
                                            verify=(not self._insecure),
                                            json={"token": token,
                                                  Token.ClientCtxAttrName: context})
        post_token_response.raise_for_status()
        return json.loads(post_token_response.content)

    def get_token(self, username, password):
        post_token_response = requests.post(self._token_endpoint_url,
                                            verify=(not self._insecure),
                                            json={"username": username, "password": password})
        post_token_response.raise_for_status()
        return json.loads(post_token_response.content)

    def delete_token(self, token, user_token):
        del_token_response = requests.delete(os.path.join(self._auth_server.token_endpoint_url, token),
                                             headers=self.get_auth_header(user_token),
                                             verify=(not self._insecure))
        del_token_response.raise_for_status()
