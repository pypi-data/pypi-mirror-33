class Player:
    name = None
    pid = None
    matches = []
    data = None

    def __init__(self, client):
        self.client = client

    def _parse_data(self, data: dict):
        self.data = data
        if data.get('data'):
            self.name = data['data']['attributes']['name']
            self.pid = data['data']['id']
            self.matches = data['data']['relationships']['matches']['data']
        else:
            self.name = data['attributes']['name']
            self.pid = data['id']
            self.matches = data['relationships']['matches']['data']

    def list_by_names(self, names: list) -> dict:

        url = f'{self.client.api_url}players'
        return self.client.get(
            url=url,
            params={
                'filter[playerNames]': ','.join(names),
            }
        )['data']

    def by_id(self, pid: str):
        self._parse_data(self.client.get(url=f'{self.client.api_url}players/{pid}'))
        return self
