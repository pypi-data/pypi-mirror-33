"""1Forge REST API Class Wrapper"""

import os
import requests


class OneForge(object):
    """1Forge REST API Class Wrapper"""

    ONEFORGE_URL = 'https://forex.1forge.com/1.0.3'

    def __init__(self, api_key=None):
        """Wrapper for 1Forge REST API

        Keyword Arguments:
            api_key {str} -- 1Forge api key.  (default: {ONEFORGE_API_KEY environment variable})

        Raises:
            RuntimeError -- If the api key is not provided via parameter or environemnt variable.
        """

        if api_key is None:
            api_key = os.getenv('ONEFORGE_API_KEY')
        if api_key is None:
            raise RuntimeError('Invalid API KEY. Either provide the api key as a parameter set ONEFORGE_API_KEY environment variable')
        self.api_key = api_key

    def _simple_request(self, resource):
        url = f'{self.ONEFORGE_URL}/{resource}'
        payload = {'api_key': self.api_key}
        res = requests.get(url, params=payload)
        res.raise_for_status()
        return res.json()

    def convert(self, src, dst, qty=1):
        """Convert from one currency to another"""
        url = f'{self.ONEFORGE_URL}/convert'
        payload = {'from': src, 'to': dst, 'quantity': qty, 'api_key': self.api_key}
        res = requests.get(url, params=payload)
        res.raise_for_status()
        return res.json()

    def market_status(self):
        """Check if the market is open"""
        return self._simple_request('market_status')

    def quota(self):
        """Check your current usage and remaining quota"""
        return self._simple_request('quota')

    def quotes(self, pairs):
        """Get quotes for specific currency pair(s)"""
        url = f'{self.ONEFORGE_URL}/quotes'
        payload = {'pairs': ','.join(pairs), 'api_key': self.api_key}
        res = requests.get(url, params=payload)
        res.raise_for_status()
        return res.json()

    def symbols(self):
        """Get a list of symbols"""
        return self._simple_request('symbols')
