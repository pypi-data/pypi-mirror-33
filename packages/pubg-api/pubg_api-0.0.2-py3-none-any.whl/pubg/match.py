class Match:
    mid = None

    def __init__(self, client):
        self.client = client

    def _parse_data(self, data: dict):
        self.mid = data['data']['id']

    def get(self, mid: str):
        return self.client.get(url=f'{self.client.api_url}matches/{mid}')
