import rsa
import json
import hashlib
import copy
import requests
from uuid import uuid4
from datetime import datetime as dt

MAX_BLOCK_TXS = 5

class Transaction:
    uuid: str
    payer_signature: str
    payer_pk: str
    payee_pk: str
    amount: int

    def to_dict(self) -> dict:
        return vars(self)

    def to_JSON(self) -> str:
        return json.dumps(self.to_dict())

    def from_JSON(self, json):
        self.uuid = json["uuid"]
        self.payer_signature = json["payer_signature"]
        self.payer_pk = json["payer_pk"]
        self.payee_pk = json["payee_pk"]
        self.amount = json["amount"]

        return self

    def __init__(self, payer_pk: str = "0", payer_sk: str = None, payee_pk: str = "0", amount: int = 0):
        if payer_sk is None:
            return

        self.uuid = uuid4().hex
        self.payer_pk = payer_pk
        self.payee_pk = payee_pk
        self.amount = amount

        rsa_payer_sk = rsa.PrivateKey.load_pkcs1(payer_sk)
        transaction_json = self.to_JSON().encode('utf-8')
        self.payer_signature = rsa.sign(transaction_json, rsa_payer_sk, hash_method="SHA-256").hex()


class Block:
    nonce: int
    timestamp: float
    prev_hash: str
    hash: str
    transactions: list[Transaction]

    def __init__(self, prev_hash):
        self.nonce = 0
        self.timestamp = dt.now().timestamp()
        self.prev_hash = prev_hash
        self.transactions = []

    def to_dict(self):
        #import pdb; pdb.set_trace()
        transactions_dicts = [transaction.to_dict() for transaction in self.transactions]
        self_copy = copy.deepcopy(self)
        self_copy_vars = vars(self_copy)
        self_copy_vars["transactions"] = transactions_dicts

        return self_copy_vars

    def from_JSON(self, block_json):
        self.nonce = block_json["nonce"]
        self.timestamp = block_json["timestamp"]
        self.prev_hash = block_json["prev_hash"]
        self.hash = block_json["hash"]
        self.transactions = block_json["transactions"]

        return self
 
    def to_JSON(self):
        return json.dumps(self.to_dict())

    def add_transaction(self, transaction: Transaction):
        assert len(self.transactions) < MAX_BLOCK_TXS, f"Too many blocks."
        self.transactions.append(transaction)

    def add_transactions(self, transactions: list[Transaction]):
        for transaction in transactions:
            self.add_transaction(transaction)

    def mine(self):
        #import pdb; pdb.set_trace()
        while True:
            block_json = self.to_JSON().encode('utf-8')
            hash = hashlib.sha256(block_json).hexdigest()

            if hash.startswith("00"):
                self.hash = hash
                return hash
            else: 
                self.nonce += 1

class Blockchain:
    head: Block

    def __init__(self, head: Block): 
        self.head = head

    def to_dict(self):
        self_copy = copy.deepcopy(self)
        self_copy.head = self_copy.head.to_dict()
        return vars(self_copy)

def broadcast(transaction: Transaction):
    json = transaction.to_dict()
    requests.post("http://localhost:6661/tx", json=json)

class Wallet:
    pk: str
    sk: str

    def __init__(self, keypair_name):
        with open(f"{keypair_name}_pk.pem", "r") as fpk, open(f"{keypair_name}_sk.pem", "r") as fsk:
            self.pk, self.sk = (fpk.read(), fsk.read())

    def send(self, payee_pk: str, amount: int):
        transaction = Transaction(self.pk, self.sk, payee_pk, amount)
        broadcast(transaction)
