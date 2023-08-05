from past.builtins import basestring


class Token(object):

    BrandAttrName = "brand_id"
    AccountAttrName = "account_id"
    GroupAttrName = "group_id"
    UsernameAttrName = "username"
    ClientCtxAttrName = "client_context"
    ServicesAttrName = "services"
    PermissionsAttrName = "permissions"
    ResourcesAttrName = "resources"

    SuperAdminFlag = "is_super_admin"
    BrandUserFlag = "is_brand_user"
    AccountUserFlag = "is_account_user"
    GroupUserFlag = "is_group_user"

    AuthIdAttrs = [BrandAttrName, AccountAttrName, GroupAttrName] # NOTE: make sure the list is sorted as now. DON'T REORDER ITEMS

    Header = "X-Auth-Token"
    ServiceName = "CIS"

    @property
    def key(self):
        return self._token_key

    @property
    def brand(self):
        return self.brand_id

    @property
    def brand_id(self):
        return str(self._token_ctx[self.BrandAttrName])

    @property
    def account(self):
        return self.account_id

    @property
    def account_id(self):
        return str(self._token_ctx[self.AccountAttrName])

    @property
    def group(self):
        return self.group_id

    @property
    def group_id(self):
        # CIS has a policy that the first group in a list is used
        group_id = self._token_ctx[self.GroupAttrName]
        return str(group_id[0] if isinstance(group_id, list) and len(group_id) != 0 else group_id)

    @property
    def username(self):
        return self._token_ctx[self.UsernameAttrName]

    @property
    def is_super_admin(self):
        return self._token_ctx[self.SuperAdminFlag]

    @property
    def is_brand_user(self):
        return self._token_ctx[self.BrandUserFlag]

    @property
    def is_account_user(self):
        return self._token_ctx[self.AccountUserFlag]

    @property
    def is_group_user(self):
        return self._token_ctx[self.GroupUserFlag]

    @property
    def client_context(self):
        return self._token_ctx.get(self.ClientCtxAttrName, None)

    @property
    def permissions(self):
        return self._token_ctx[self.ServicesAttrName][self.ServiceName][self.PermissionsAttrName][self.ResourcesAttrName]

    @property
    def json(self):
        return dict(self._token_ctx)

    @property
    def header(self):
        return {self.Header: self.key}

    @staticmethod
    def auth_header(token):
        return {Token.Header: token}

    @property
    def level(self):
        try:
            return self._level
        except AttributeError: # just performance improvement
            # It's important to keep this switch in the current order, since AAA is so consistent that it can return both account_user + super_admin flags, as well as more then 1 group)))
            if self.is_group_user:
                self._level = 3
            elif self.is_account_user:
                self._level = 2
            elif self.is_brand_user:
                self._level = 1
            elif self.is_super_admin:
                self._level = 0
            else:
                raise KeyError("Inconsistent token has been discovered {}".format(token))
            return self._level

    @property
    def required_auth_ids(self):
        return self.AuthIdAttrs[:self.level]

    def __contains__(self, key):
        return bool(self._token_ctx.get(key))

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except AttributeError:
            raise KeyError(key)

    def __eq__(self, other):
        if not isinstance(other, Token):
            raise TypeError("A right operand must be Token type: {}".format(other))

        return self.key == other.key and self.brand == other.brand and self.account == other.account and \
                                         self.group == other.group and self.username == other.username

    def __init__(self, token_key, token_ctx, service_name=None):

        # NOTE: that CIS North and CIS Storage/Gateways are represented in AAA as a single 'CIS' service
        # defined by Token.ServiceName, but 'CIS-south' is a different Service in AAA.
        # That's the first use-case why ServiceName becomes parametrizeable
        if service_name: # override what is defined in the class by default
            self.ServiceName = service_name

        if not isinstance(token_key, basestring):
            raise TypeError("Token key must be a string type !!!")
        if not isinstance(token_ctx, dict):
            raise TypeError("Token context must be an object of dict class !!!")

        if self.ServiceName not in token_ctx[self.ServicesAttrName] or \
                self.PermissionsAttrName not in token_ctx[self.ServicesAttrName][self.ServiceName]:
            raise ValueError("Missing permissions in the given token context {}".format(token_ctx))

        self._token_key = token_key
        self._token_ctx = token_ctx

