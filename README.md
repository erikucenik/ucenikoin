# UceniKoin

My own cryptocurrency based on the [Bitcoin whitepaper](https://bitcoin.org/bitcoin.pdf).

Each client (`client.py`) makes and broadcasts transactions to each node running `server.py` and each node uses them to create blocks. Clients can request nodes for their blockchains and blockpools and determine through `client.py` their own balances or other people's.

Don't actually use it, it's not safe at all, it's just an example for [this explainer](https://erikucenik.com/articles/ucenikoin).
