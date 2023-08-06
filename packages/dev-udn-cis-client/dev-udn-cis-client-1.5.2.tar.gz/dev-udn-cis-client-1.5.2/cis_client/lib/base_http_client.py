import functools

from cis_client.lib.aaa import auth_client


class BaseClient(object):
    def get_auth_params(self, **kwargs):
        auth_params = {
            key: value
            for key, value in kwargs.items()
            if key in ('brand_id', 'account_id', 'group_id')
        }
        return auth_params


def with_auth(func):
    def decorator(*args, **kwargs):
        if 'token' not in kwargs:
            aaa_host = kwargs.get('aaa_host')
            username = kwargs.get('username')
            password = kwargs.get('password')
            insecure = kwargs.get('insecure', False)
            if not aaa_host or not username or not password:
                raise ValueError('Login requires following kwargs: "aaa_host", "username", "password".')
            token = auth_client.get_token(aaa_host, username, password, insecure=insecure)
            kwargs['token'] = token
        if kwargs.get('context') is not None:
            kwargs['context']['token'] = kwargs['token']
        return func(*args, **kwargs)

    return decorator
