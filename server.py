from fastapi import FastAPI, Request
import uvicorn
from ucenikoin import Transaction, Block, Blockchain
import json
import requests

app = FastAPI()

head: Block = Block("0")
head.mine()
blockchain = Blockchain(head)

transaction_queue: list[Transaction] = []
blockchains: list[Blockchain] = [blockchain]
blockpool: list[Block] = [head]

def add_created_block_to_blockchains(block):
    for blockchain in blockchains:
        block.prev_hash = blockchain.head.hash
        blockchain.head = block

    blockpool.append(block)

def create_block() -> Block:
    global head, transaction_queue

    block = Block(head.hash)
    block.add_transactions(transaction_queue)
    block.mine()

    transaction_queue = []
    return block

def broadcast(block: Block) -> None:
    json = block.to_dict()

    requests.post("http://localhost:6662/block", json=json)

@app.post("/tx")
async def receive_transaction(request: Request) -> None:
    tx_json = await request.json()
    transaction = Transaction().from_JSON(tx_json)
    transaction_queue.append(transaction)

    if len(transaction_queue) == 5:
        block = create_block()
        add_created_block_to_blockchains(block)
        broadcast(block)

@app.post("/block")
async def receive_block(request: Request) -> None:
    block_json = await request.json()
    block = Block("0").from_JSON(block_json)

    blockpool.append(block)

    for blockchain in blockchains:
        if blockchain.head.hash == block.prev_hash:
            blockchain.head = block
            return

    blockchain = Blockchain(block)
    blockchains.append(blockchain)
    transaction_queue = []

@app.get("/blockchains")
async def send_blockchains():
    global blockchains, blockpool
    blockchains_dicts_list = [blockchain.to_dict() for blockchain in blockchains]
    blockpool_dict = [block.to_dict() for block in blockpool]

    return { 'blockpool': blockpool_dict, 'blockchains': blockchains_dicts_list }

uvicorn.run(app, host="localhost", port=6661)
