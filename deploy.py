from solcx import compile_standard
import os
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()
    

# Compile Our Solidity

compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol": {"content": simple_storage_file}},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi", "metadata", "evm.bytecode", "evm.sourceMap"]
                }
            }
        },
    }, 
    solc_version="0.6.0",
)

with open("compiled_code.json", "w") as file:
    json.dump(compiled_sol, file)
    
#get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

#get abi
abi = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

#for connecting to ganache
#for connecting to rinkeby
w3 = Web3(Web3.HTTPProvider("https://rinkeby.infura.io/v3/798e5a6f54894902a6c24c171bd95d55"))
chain_id = 4
my_address = "0x3d2772531E766285e267074123AfD0aAF7Ee72b2"
private_key = os.getenv("PRIVATE_KEY")

#Create the contract in python
SimpleStorage = w3.eth.contract(abi = abi, bytecode = bytecode)

#Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)

#1. Build a transaction
#2. Sign a transaction
#3. Send a transaction

transaction = SimpleStorage.constructor().buildTransaction({"gasPrice": w3.eth.gas_price ,"chainId": chain_id, "from": my_address, "nonce": nonce})

signed_txn = w3.eth.account.sign_transaction(transaction, private_key = private_key)
print("Deploying Contract!")

# Send this signed transaction
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Done! Contract deployed to {tx_receipt.contractAddress}")


# Working with the contract, you always need
# Contract Address
# Contract ABI

simple_storage = w3.eth.contract(address = tx_receipt.contractAddress, abi = abi)

# Two ways of interacting with the Blockchain
# Call -> Simulate making the call and getting a return value
# Transaction -> Actually make a state change.
 
print(simple_storage.functions.retrieve().call())

print("Updating Contract...")
store_transaction = simple_storage.functions.store(15).buildTransaction({
    "gasPrice": w3.eth.gas_price ,"chainId": chain_id, "from": my_address, "nonce": nonce + 1
})

signed_store_txn = w3.eth.account.sign_transaction(store_transaction, private_key = private_key)

send_store_tx = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(send_store_tx)
print("Updated!")

print(simple_storage.functions.retrieve().call())
