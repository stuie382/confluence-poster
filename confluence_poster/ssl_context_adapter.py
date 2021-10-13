"""SSL Context Adapter

Handle the creation of custom SSL context required to run in the development environment.
"""
import ssl
import requests.adapters


class SSLContextAdapter(requests.adapters.HTTPAdapter):
    """
    A class to uses the Windows default CA store for SSL.
    """

    def init_poolmanager(self, *args, **kwargs):
        """
        Override the default implementation to manipulate the SSL Context
        :param args:
        :param kwargs:
        :return: The custom context adapter
        """
        context = ssl.create_default_context()
        kwargs['ssl_context'] = context
        context.load_default_certs()
        return super(SSLContextAdapter, self).init_poolmanager(*args, **kwargs)
   