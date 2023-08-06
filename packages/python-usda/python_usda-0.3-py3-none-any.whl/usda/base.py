#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import requests

BASE_URI = 'http://api.data.gov/'


class DataGovApiError(BaseException):
    """Base class for all Data.gov API errors"""
    pass


class DataGovApiRateExceededError(DataGovApiError):
    """Data.gov API rate limit has been exceeded for this key"""

    def __init__(self):
        super().__init__('API rate limit has been exceeded.')


class DataGovInvalidApiKeyError(DataGovApiError):
    """Supplied Data.gov API key is invalid."""

    def __init__(self):
        super().__init__("A invalid Data.gov API key has been supplied. "
                         "Get one at https://api.data.gov/signup")


def api_request(uri, **parameters):
    """Get an API response"""
    r = requests.get(uri, parameters)
    if r.ok:
        return r.json()
    try:
        data = r.json()
    except ValueError:  # Server did not even return a JSON for the error
        r.raise_for_status()
    # The JSON error data when the API rate limit is exceeded is in a
    # different format than on parameter errors. This will handle both.
    if data.get('errors') is not None:
        err = data['errors']['error'][0]
    else:  # API rate limit exceeded error format
        err = data['error']
    if err.get('parameter') is not None:  # Wrong parameter error
        raise ValueError(
            "API responded with an error on parameter '{0}': {1}".format(
                err['parameter'], err['message']))
    elif err['code'] == "OVER_RATE_LIMIT":
        raise DataGovApiRateExceededError()
    elif err['code'] == "API_KEY_INVALID":
        raise DataGovInvalidApiKeyError()
    else:
        raise DataGovApiError("{0}: {1}".format(err['code'], err['message']))


class DataGovClientBase(object):
    """Base class for Data.gov API clients."""

    def __init__(self, uri_part, api, api_key, use_format=True):
        """Instanciate a Data.gov API client.
        Requires an API endpoint and an API key.
        Automatic return format (JSON/XML) adding to URLs can be disabled."""
        self.uri_part = uri_part
        self.api = api
        self.key = api_key
        self.use_format = use_format

    def build_uri(self, uri_action):
        """Build a valid URI for a specific action."""
        return "{0}{1}{2}/{3}".format(
            BASE_URI, self.uri_part, self.api.value, uri_action.value)

    def run_request(self, uri_action, **kwargs):
        """Execute a request and return an API response.
        Can throw HTTPError or any DataGovApiError."""
        kwargs['api_key'] = self.key
        if 'format' not in kwargs and self.use_format:
            kwargs['format'] = 'json'
        return api_request(self.build_uri(uri_action), **kwargs)
