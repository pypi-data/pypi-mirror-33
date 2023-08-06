# PUBG Api Client

## How to use?

Install the pubg-client package
```
pip install pubg-client
```

## Example snippet
```
import os

from pubg import PubgClient

YOUR_TOKEN = 'your pubg token'

pubg = PubgClient(token=YOUR_TOKEN)


_names = [
    'Cafeteira'
]

players = pubg.players().list_by_names(names=_names)

```