from http import HTTPStatus
import os

import requests

from . import exceptions
from .player import Player
from .settings import Region


__connection_exceptions__ = (
    requests.exceptions.Timeout,
    requests.exceptions.ConnectTimeout,
    requests.exceptions.ConnectionError,
)


class PubgClient:
    _token = None
    _region = None

    _base_api = 'https://api.playbattlegrounds.com/shards/{region}/'
    _retries = 5
    _headers = {
        'Accept': 'application/json',
    }

    def __init__(self, token: str = None, region: Region = None):
        if token:
            self._token = token
            
        else:
            self._token = os.getenv('PUBG_TOKEN')
            
        if not  self._token:
            raise exceptions.TokenNotDefined()

        self._region = region or Region.PC_SA

        if not self._region:
            raise exceptions.RegionNotDefined()

    @property
    def api_url(self):
        return self._base_api.format(
            region=self._region.value,
        )

    @property
    def headers(self):
        self._headers.update({
            'Authorization': f'Bearer {self._token}'
        })

        return self._headers

    @staticmethod
    def _dict_to_params(params: dict) -> str:
        params_list = []
        for key, value in params.items():
            params_list.append(f'{key}={value}')
        return '&'.join(params_list)

    def get(self, url: str, headers: dict = None, params: dict = None) -> dict:
        if not headers:
            headers = {}

        self._headers.update(headers)

        if params:
            params = self._dict_to_params(params)

        for i in range(self._retries):
            try:
                response = requests.get(
                    url=url,
                    headers=self.headers,
                    params=params,
                )

                if response.status_code == HTTPStatus.OK:
                    return response.json()

                if response.status_code == HTTPStatus.UNAUTHORIZED:
                    raise exceptions.Unauthorized

                if response.status_code == HTTPStatus.NOT_FOUND:
                    raise exceptions.NotFound

                if response.status_code == HTTPStatus.UNSUPPORTED_MEDIA_TYPE:
                    raise exceptions.UnsupportedMediaType

                if response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
                    raise exceptions.TooManyRequests

            except __connection_exceptions__:
                pass

        raise exceptions.ApiConnectionError

    def players(self):
        return Player(self)
