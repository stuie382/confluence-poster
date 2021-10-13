"""Configuration

Configuration is a wrapper around all the user provided configuration options.
"""
import collections

Configuration = collections.namedtuple('Configuration', 'confluence_url user_name user_pass ssl_key ssl_cert files '
                                                        'space space_key')
