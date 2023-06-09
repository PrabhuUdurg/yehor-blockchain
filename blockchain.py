import hashlib
import json 
from textwrap import dedent
from time import time 
from uuid import uuid4 

from flask import Flask, jsonify, request 

class Blockchain(object): 
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Create genesis block 
        self.new_block(previous_hash='0', proof=1)

    
    def new_block(self, proof, previous_hash=None):
            block = {
                'index' : len(self.chain) + 1, 
                'timestamp' : time(),
                'transactions' : self.current_transactions,
                'proof' : proof, 
                'previous_hash' : previous_hash or self.hash(self.chain[-1]),
            }
     # Reset the current list of transactions
            self.current_transactions = []

            self.chain.append(block)
            return block




    def new_transaction(self, sender, recipient, amount):
        self.current_transactions.append({
            'sender' : sender,
            'recipient' : recipient, 
            'amount' : amount, 
        })
        
        return self.last_block['index'] + 1 


    # Proof of work 
    def proof_of_work(self, last_proof):
        new_proof = 1
        check_proof = False

        while check_proof is False:
            hash_operation = hashlib.sha256(
                str(new_proof**2 - last_proof**2).encode()).hexdigest()
            if hash_operation[:5] == '00000':
                check_proof = True
            else:
                new_proof += 1
 
        return new_proof
 
    

    @staticmethod 
    def hash(block):
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()


    def valid_proof(last_proof, proof): 
        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"


    
    @property
    def last_block(self): 
        return self.chain[-1]


#Instantiate node 

app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

# Flask Setup  
@app.route('/mine', methods=['GET'])
def mine():
    # We run the proof of work algorithm 
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = { 
        'message' : 'New Block Forged', 
        'index' : block['index'], 
        'transactions' : block['transactions'], 
        'proof' : block['proof'],
        'previous_hash' : block['previous_hash']
    }
    return jsonify(response), 200


#@app.route('/transactions/new', methods=['POST'])
#def new_transaction():
 #   return "We'll add a new transaction"


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain),
    }
    return jsonify(response), 200


@app.route('/transactions/new', methods=['POST'])
def new_transactions():
    values = request.get_json()

     # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], 
    values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

    
