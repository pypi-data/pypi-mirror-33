from web3.middleware import geth_poa_middleware
from web3 import Web3, HTTPProvider
from web3.eth import Eth

CHAIN_ID = 4 # Rinkeby ID
GAS = 500000
GAS_PRICE = 20 # 20 gwei
VALUE = 0

POA_NETWORK = "rinkeby"
INFURA_URL = 'https://rinkeby.infura.io'

infura_provider = HTTPProvider(INFURA_URL)
web3 = Web3(infura_provider)
eth = Eth(web3);

# If the network is POA(Proof of authority) we need this middleware injected
if INFURA_URL.find(POA_NETWORK):
    web3.middleware_stack.inject(geth_poa_middleware, layer=0)