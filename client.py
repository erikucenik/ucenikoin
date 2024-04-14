from ucenikoin import Transaction, Block, Wallet
import requests

alice_wallet = Wallet("./keys/alice")
erik_wallet = Wallet("./keys/erik")

for i in range(5):
    alice_wallet.send(erik_wallet.pk, 20)

blockchains = requests.get("http://localhost:6661/blockchains").json()
