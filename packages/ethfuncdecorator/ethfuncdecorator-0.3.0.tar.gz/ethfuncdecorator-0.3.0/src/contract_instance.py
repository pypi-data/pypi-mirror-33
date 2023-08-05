from util import retrieve_abi_from_file, checksum_address
from web3.contract import ContractFunction
from config import CHAIN_ID, GAS, GAS_PRICE, VALUE

class ContractInstance:

    def __init__(self, contract_json, contract_address, eth, web3):
        contract_abi = retrieve_abi_from_file(contract_json)
        check_summed_address = checksum_address(contract_address)
        
        self.eth = eth
        self.web3 = web3
        self.chain_id = CHAIN_ID
        self.gas_price = GAS_PRICE
        self.address = contract_address

        self.__append_contract_functions(check_summed_address, contract_abi)
       

    def __append_contract_functions(self, contract_address, contract_abi):
        self.__contract_functions = self.__filter_by_type('function', contract_abi)

        for funcName in self.__contract_functions.keys():
            setattr(
                self,
                funcName,
                self.__decorateContractFunctions(
                    ContractFunction.factory(
                        funcName,
                        web3=self.web3,
                        contract_abi=contract_abi,
                        address=contract_address,
                        function_identifier=funcName
                ))
            )
    
    def __getattr__(self, function_name):
        if function_name not in self.__dict__:
            raise Exception("The function '{}' was not found in this contract's abi. ".format(function_name))
        else:
            return super().__getattribute__(function_name)

    def __filter_by_type(self, _type, contract_abi):
        return {abi['name']: abi['constant'] for abi in contract_abi if abi['type'] == _type }

    def __decorateContractFunctions(self, func):

        def _constant_function(*args):
            return self.__invokeConstantFunction(func, args)
        
        def _nonconstant_funcation(*args, **kwargs):
            return  self.__invokeNonConstantFunction(func, args, kwargs)
                
        if self.__isConstantFunction(func):
            return _constant_function
        else:
            return  _nonconstant_funcation

    def __isConstantFunction(self, func):
        return self.__contract_functions[func.__name__]

    def __invokeConstantFunction(self, func, funcParams):
        result = func(*funcParams).call()
        return result

    def __invokeNonConstantFunction(self, func, funcParams, transactionTags):
        self.__require_private_key(transactionTags)

        tags = self.__retrieve_transaction_tags(transactionTags)

        signer = self.eth.account.privateKeyToAccount(tags['private_key'])
        build_information = self.__get_build_information(signer.address, tags)
        
        contract_tx = func(*funcParams).buildTransaction(
            build_information
        )
       
        signed_txn = self.eth.account.signTransaction(contract_tx, private_key=tags['private_key'])
        result = self.eth.sendRawTransaction(signed_txn.rawTransaction)
        
        return self.web3.toHex(result)

    def __require_private_key(self, func_transaction_tags):
        if 'private_key' not in func_transaction_tags:
            raise Exception(
                "The function is not constant.",
                "Require private key"
            )

    def __retrieve_transaction_tags(self, transactionTags):
        tags = {
            'private_key': transactionTags['private_key']
        }
        
        if 'value' in  transactionTags:
            tags['value'] = transactionTags['value']
        else:
            tags['value'] = VALUE

        if 'gas' in transactionTags:
            tags['gas'] = transactionTags['gas']
        else:
            tags['gas'] = GAS

        return tags

    def __get_build_information(self, signer_address, tags):
        check_summed_address = checksum_address(signer_address)
        nonce = self.eth.getTransactionCount(check_summed_address, block_identifier='latest')

        result = {
            'value': tags['value'],
            'chainId': self.chain_id,
            'nonce': nonce,
            'gasPrice': self.web3.toWei(self.gas_price, 'gwei'),
            'gas': tags['gas']
        }

        return result

    def set_network_parameters(self, chain, tx_gas_price):
        self.gas_price = tx_gas_price
        self.chain_id = chain 