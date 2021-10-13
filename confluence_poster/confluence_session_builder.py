"""Confluence session builder.

This file will create an appropriate session for connecting to the Confluence server, based on the Configuration
provided.
"""
import logging
from urllib.parse import urlparse
import requests
import requests.adapters
from atlassian import Confluence

from confluence_poster import configuration
from confluence_poster import ssl_context_adapter


log = logging.getLogger(__name__)


class ConfluenceSessionBuilder:
    """
    Create a custom Confluence session.
    """

    def build(self, config: configuration.Configuration) -> Confluence:
        """ Create a Confluence session based on the configuration provided. Either the username and password pair
        need to be provided, or the SSL key and cert pair need to be provided. If any information is missing, then
        and error is logged and raised.

        :param config: The user provided configuration
        :return: The new Confluence session
        :raises: Will raise an error if the user/pass or key/cert information is missing
        """
        if config.user_name is not None and config.user_pass is not None:
            return self._create_username_password_session(config)
        elif config.ssl_key is not None and config.ssl_cert is not None:
            return self._create_key_cert_session(config)
        else:
            log.error(f"Could not work out what type of session to create based on the config provided.\n"
                      f"{config}")
            raise ValueError("Invalid arguments provided")

    def _create_key_cert_session(self, config: configuration.Configuration) -> Confluence:
        """ Create a Confluence session with the custom SSL Context Adapter using the key and certificate.

        :param config: The user provided configuration
        :return: The configured Confluence session
        """
        session = requests.Session()
        domain = self._get_domain_url_from_confluence_url(config.confluence_url)
        session.mount(domain, ssl_context_adapter.SSLContextAdapter())
        confluence = Confluence(url=config.confluence_url,
                                key=config.ssl_key,
                                cert=config.ssl_cert,
                                session=session)
        return confluence

    def _create_username_password_session(self, config: configuration.Configuration) -> Confluence:
        """ Create a Confluence session with the custom SSL Context Adapter based on the configuration provided.

        :param config: The user provided configuration
        :return: The configured Confluence session
        """
        session = requests.Session()
        domain = self._get_domain_url_from_confluence_url(config.confluence_url)
        session.mount(domain, ssl_context_adapter.SSLContextAdapter())
        confluence = Confluence(url=config.confluence_url,
                                username=config.user_name,
                                password=config.user_pass,
                                session=session)
        return confluence

    @staticmethod
    def _get_domain_url_from_confluence_url(confluence_url: str) -> str:
        parsed_url = urlparse(confluence_url)
        return "{0.scheme}://{0.netloc}".format(parsed_url)
