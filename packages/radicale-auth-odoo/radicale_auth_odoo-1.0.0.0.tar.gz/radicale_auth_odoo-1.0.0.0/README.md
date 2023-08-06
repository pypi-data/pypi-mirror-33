# radicale_auth_odoo

Use Odoo as a Radicale authentication method

# How To
Install this package along side with Radicale 2.0, and on the configuration
file add the following settings

```
[auth]
type = radicale_odoo_auth
odoo_url = <your Odoo instance url like: https://example.com>
odoo_database = <database where users live>
odoo_group = <optional: only accept logins from users that are inside the group>
```

Make sure that XMLRPC is available on Odoo
