
contract_instance (main file) is used for building ethereum contract functions in an easy way
ContractInstance class is a decorator for web3 contract functions

You can call sign-functions without signing them manually

# It is only functions-decorator. 

# Note => Call back function is not included

Usage:
    contract = ContractInstance('contract_json_file', contract_address, eth, web3)
    
    # Usage of constant function:
    
        # Empty-params
        result = contract.getSmth();
        print(result) => smth

        # Non empty-params 
        result = contract.calcSum(1, 2);
        print(result) => sum

    # Usage of sing-function:
    
        # Empty-params
        result = contract.addData(data, private_key="your private key");
        print(result) => transaction hash

       

    # Note => private key is required for sing-functions
    
        If you want to specify a certain gas or your function is payable, add: 
        
            contract.addData(data, private_key="your private key", value=your value, gas=your gas);

        If you do not specify a tag, the default values are:
            Gas = 500000
            Value = 0

    # The default network properties are:
        Chain id = 4 (Rinkeby)
        Gas_price = 20gwei

        1) If you want to change them at instance level, you could do:
            contract.set_network_parameters(yourChainId, yourGasPrice)

        2) If you want to change them at global level (each contract instance to have than on init), you could go in config.py and change them there