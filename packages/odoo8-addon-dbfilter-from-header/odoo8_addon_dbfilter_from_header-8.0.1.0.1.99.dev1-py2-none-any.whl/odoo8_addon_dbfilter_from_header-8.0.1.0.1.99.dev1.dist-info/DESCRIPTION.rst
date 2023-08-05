This addon lets you pass a dbfilter as a HTTP header.

This is interesting for setups where database names can't be mapped to
proxied host names.

In nginx, use one of
proxy_set_header X-OpenERP-dbfilter [your filter];
proxy_set_header X-Odoo-dbfilter [your filter];

The addon has to be loaded as server-wide module.


