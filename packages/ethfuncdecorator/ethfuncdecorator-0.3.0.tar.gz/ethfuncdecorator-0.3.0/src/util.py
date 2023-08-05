import json
from config import web3

def retrieve_abi_from_file(json_file_path):
    with open(json_file_path) as contract_json:
        contract = json.load(contract_json)

    return contract["abi"]

def checksum_address(address):
    return web3.toChecksumAddress(address)