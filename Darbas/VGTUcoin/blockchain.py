import hashlib
import json
from textwrap import dedent
from uuid import uuid4
import jsonpickle
from flask import Flask
from urllib.parse import urlparse
from Crypto.PublicKey import RSA
from Crypto.Signature import *
from time import time
from datetime import datetime
import requests


class Blockchain (object):
    def __init__(self):
        self.chain = [self.addGenesisBlock()]
        self.pendingTransactions = []
        self.difficulty = 4
        self.minerRewards = 200
        self.blockSize = 10
        self.nodes = set()

    def register_node(self, address):
        parsedUrl = urlparse(address)
        self.nodes.add(parsedUrl.netloc)

    def resolveConflicts(self):
        neighbors = self.nodes
        newChain = None

        maxLength = len(self.chain)

        for node in neighbors:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                if length > maxLength and self.isValidChain():
                    maxLength = length
                    newChain = chain

        if newChain:
            self.chain = self.chainJSONdecode(newChain)
            print(self.chain)
            return True

        return False

    def minePendingTransactions(self, miner):

        lenPT = len(self.pendingTransactions)
        if(lenPT <= 1):
            print("Per mažai operacijų eilėje (Turi būti > 1)")
            return False
        else:
            for i in range(0, lenPT, self.blockSize):

                end = i + self.blockSize
                if i >= lenPT:
                    end = lenPT
                
                transactionSlice = self.pendingTransactions[i:end]

                newBlock = Block(transactionSlice, datetime.now().strftime(
                    "%m/%d/%Y, %H:%M:%S"), len(self.chain))

                hashVal = self.getLastBlock().hash
                newBlock.prev = hashVal
                newBlock.mineBlock(self.difficulty)
                self.chain.append(newBlock)
            print("Tranzakcija pavyko")

            payMiner = Transaction("Kasytojo atlygis", miner, self.minerRewards)
            self.pendingTransactions = [payMiner]
        return True

    def buy(self, buyer, amt):

        if not buyer or not amt:
            print("Tranzakcija nesekminga")
            return False
        
        print("Pavyko")
        return True

    def addTransaction(self, sender, reciever, amt, keyString, senderKey):
        keyByte = keyString.encode("ASCII")
        senderKeyByte = senderKey.encode("ASCII")
        key = RSA.import_key(keyByte)
        senderKey = RSA.import_key(senderKeyByte)

        if not sender or not reciever or not amt:
            print("Klaida 1")
            return False

        transaction = Transaction(sender, reciever, amt)

        transaction.signTransaction(key, senderKey)

        if not transaction.isValidTransaction():
            print("Klaida 2")
            return False
        self.pendingTransactions.append(transaction)
        return len(self.chain) + 1

    def getLastBlock(self):
        return self.chain[-1]

    def addGenesisBlock(self):
        tArr = []
        tArr.append(Transaction("me", "you", 100))
        genesis = Block(tArr, datetime.now().strftime("%m/%d/%Y, %H:%M:%S"), 0)
        genesis.prev = "Nėra"
        return genesis

    def isValidChain(self):
        for i in range(1, len(self.chain)):
            b1 = self.chain[i-1]
            b2 = self.chain[i]

            if not b2.hasValidTransactions():
                return False

            if b2.hash != b2.calculateHash():
                return False

            if b2.prev != b1.hash:
                return False
        return True

    def generateKeys(self):
        key = RSA.generate(2048)
        private_key = key.export_key()
        file_out = open("private.pem", "wb")
        file_out.write(private_key)

        public_key = key.publickey().export_key()
        file_out = open("public.pem", "wb")
        file_out.write(public_key)

        print(public_key.decode('ASCII'))
        return key.publickey().export_key().decode('ASCII')

    def chainJSONencode(self):

        blockArrJSON = []
        for block in self.chain:
            blockJSON = {}
            blockJSON['hash'] = block.hash
            blockJSON['index'] = block.index
            blockJSON['prev'] = block.prev
            blockJSON['time'] = block.time
            blockJSON['nonse'] = block.nonce
            blockJSON['vgtu'] = block.vgtu

            transactionsJSON = []
            tJSON = {}
            for transaction in block.transactions:
                tJSON['time'] = transaction.time
                tJSON['sender'] = transaction.sender
                tJSON['reciever'] = transaction.reciever
                tJSON['amt'] = transaction.amt
                tJSON['hash'] = transaction.hash
                transactionsJSON.append(tJSON)

            blockJSON['transactions'] = transactionsJSON

            blockArrJSON.append(blockJSON)

        return blockArrJSON


    def chainJSONdecode(self, chainJSON):
        chain = []
        for blockJSON in chainJSON:

            tArr = []
            for tJSON in blockJSON['transactions']:
                transaction = Transaction(
                    tJSON['sender'], tJSON['reciever'], tJSON['amt'])
                transaction.time = tJSON['time']
                transaction.hash = tJSON['hash']
                tArr.append(transaction)

            block = Block(tArr, blockJSON['time'], blockJSON['index'])
            block.hash = blockJSON['hash']
            block.prev = blockJSON['prev']
            block.nonce = blockJSON['nonse']
            block.vgtu = blockJSON['vgtu']

            chain.append(block)
        return chain

    def getBalance(self, person):
        balance = 0
        for i in range(1, len(self.chain)):
            block = self.chain[i]
            try:
                for j in range(0, len(block.transactions)):
                    transaction = block.transactions[j]
                    if(transaction.sender == person):
                        balance -= transaction.amt
                    if(transaction.reciever == person):
                        balance += transaction.amt
            except AttributeError:
                print("Nėra operacijų")
        return balance + 10000


class Block (object):
    def __init__(self, transactions, time, index):
        self.index = index #bloko numeris
        self.transactions = transactions #info apie tranzakcija
        self.time = time
        self.prev = '' # prev hash
        self.nonce = 0
        self.vgtu = self.calculateVGTU()
        self.hash = self.calculateHash() #hash

    def calculateVGTU(self):
        return "VGTU IS DE BEST"

    def calculateHash(self):

        hashTransactions = ""

        for transaction in self.transactions:
            hashTransactions += transaction.hash
        hashString = str(self.time) + hashTransactions + \
            self.vgtu + self.prev + str(self.nonce)
        hashEncoded = json.dumps(hashString, sort_keys=True).encode()
        return hashlib.sha256(hashEncoded).hexdigest()


    def mineBlock(self, difficulty):
        arr = []
        for i in range(0, difficulty):
            arr.append(i)

        # daryt iki 0123...
        arrStr = map(str, arr)
        hashPuzzle = ''.join(arrStr)
        while self.hash[0:difficulty] != hashPuzzle:
            self.nonce += 1
            self.hash = self.calculateHash()
        print("Kasyba sėkmingai atlikta.")
        return True

    def hasValidTransactions(self):
        for i in range(0, len(self.transactions)):
            transaction = self.transactions[i]
            if not transaction.isValidTransaction():
                return False
            return True

    def JSONencode(self):
        return jsonpickle.encode(self)


class Transaction (object):
    def __init__(self, sender, reciever, amt):
        self.sender = sender
        self.reciever = reciever
        self.amt = amt
        self.time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")  # change to current date
        self.hash = self.calculateHash()

    def calculateHash(self):
        hashString = self.sender + self.reciever + \
            str(self.amt) + str(self.time)
        hashEncoded = json.dumps(hashString, sort_keys=True).encode()
        return hashlib.sha256(hashEncoded).hexdigest()

    def isValidTransaction(self):
        if(self.hash != self.calculateHash()):
            return False
        if(self.sender == self.reciever):
            return False
        if(self.sender == "Kasytojo atlygis"):
            return True
        if not self.signature or len(self.signature) == 0:
            print("Nėra parašo")
            return False
        return True

    def signTransaction(self, key, senderKey):
        if(self.hash != self.calculateHash()):
            print("operacijos klaida")
            return False
        if(str(key.publickey().export_key()) != str(senderKey.publickey().export_key())):
            print("Negalima atlikti operacija kito vartotojo paskyroje")
            return False

        pkcs1_15.new(key)

        self.signature = "made"
        print("Pavyko")
        return True
