# Copyright (c) 2018 Hugo Rodrigues
"""
Odoo Authentication for Radicale 2
"""

from xmlrpc.client import ServerProxy
from radicale.auth import BaseAuth

XMLRPC_BASE_ENDPOINT = "/xmlrpc/2/"


class Auth(BaseAuth):
    """Radicale Authentication"""

    def is_authenticated(self, user, password):
        """
        Authenticate using Odoo via XMLRPC

        First, we login using into Odoo using webservices. If the user and
        password matches, we then check if the user belongs to the configured
        group. If it belongs to the group or the group isn't set, the
        authentication is complete.
        """

        server = self.configuration.get("auth", "odoo_url")
        database = self.configuration.get("auth", "odoo_database")
        group = self.configuration.has_option("auth", "odoo_group") and \
                self.configuration.get("auth", "odoo_group")
        # Remove trailing /
        if server[-1:] == "/":
            server = server[:-1]

        with ServerProxy("{0}{1}common".format(server,
                                               XMLRPC_BASE_ENDPOINT)) as proxy:

            odoo_uid = proxy.authenticate(database, user, password, {})
        if not odoo_uid:
            self.logger.error("Invalid Odoo login for user %s", user)
            return False
        self.logger.info("Found valid Odoo login for user %s", user)
        if not group:
            return True

        with ServerProxy("{0}{1}object".format(server,
                                               XMLRPC_BASE_ENDPOINT)) as proxy:
            in_group = proxy.execute_kw(database, odoo_uid, password,
                                        'res.users', 'has_group', [group], {})
        if in_group:
            self.logger.info("User %s belongs to group %s", user, group)
            return True
        else:
            self.logger.error("User %s doesn't belong to group %s",
                              user, group)
            return False
