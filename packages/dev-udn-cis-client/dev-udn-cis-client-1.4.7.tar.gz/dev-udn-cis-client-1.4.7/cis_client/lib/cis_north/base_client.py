class BaseClient(object):
    def get_auth_params(self, **kwargs):
        auth_params = {
            key: value
            for key, value in kwargs.items()
            if key in ('brand_id', 'account_id', 'group_id')
        }
        return auth_params
