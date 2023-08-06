RecordsKeeper-python-lib3 
=========================


It is an infrastructure to build RecordsKeeper blockchain-based applications, products and is used to work around applications that are built on top of this blockchain platform.

**Note:** If you're looking for the RecordsKeeper Python Library please see: [RecordsKeeper Python Library](https://github.com/RecordsKeeper/recordskeeper-python-sdk/tree/python-3.0)


## Getting Started

Before you begin you'll need to have python v3 installed. There are several options for installation for python depending on the operating system you are using.


```bash
pip install -g recordskeeper_python_lib3
```

Import these python libraries first to get started with the library classes and functions.


```bash
    import requests
    import json
    from requests.auth import HTTPBasicAuth
    import yaml
    import sys
    import binascii
```


Creating Connection
-------------------

Entry point for accessing Address class resources.

Config file to import config parameters:

```bash
    
    with open("config.yaml", 'r') as ymlfile:
        cfg = yaml.load(ymlfile)
```
   
Importing chain url and chain name from config file:

* URL: Url to connect to the chain ([RPC Host]:[RPC Port])
* Chain-name: chain name

```bash

    url = network['url']
    chain = network['chain']

```   

Node Authentication
-------------------

Importing user name and password values from config file to authenticate the node:

* User name: The rpc user is used to call the APIs.
* Password: The rpc password is used to authenticate the APIs.

```bash
    
    user = network['rkuser']
    password = network['passwd']

```

## Libraries

- [Addresses](https://github.com/RecordsKeeper/recordskeeper-python-sdk/blob/python-3.0/recordskeeper_python_lib3/address.py) Library to work with RecordsKeeper addresses. You can generate new address, check all addresses, check address validity, check address permissions, check address balance by using Address class. You just have to pass parameters to invoke the pre-defined functions.

- [Assets](https://github.com/RecordsKeeper/recordskeeper-python-sdk/blob/python-3.0/recordskeeper_python_lib3/assets.py) Library to work with RecordsKeeper assets. You can create new assets and list all assets by using Assets class. You just have to pass parameters to invoke the pre-defined functions.

- [Block]((https://github.com/RecordsKeeper/recordskeeper-python-sdk/blob/python-3.0/recordskeeper_python_lib3/block.py) Library to work with RecordsKeeper block informaion. You can collect block information by using block class. You just have to pass parameters to invoke the pre-defined functions.

- [Blockchain]((https://github.com/RecordsKeeper/recordskeeper-python-sdk/blob/python-3.0/recordskeeper_python_lib3/blockchain.py) Library to work with RecordsKeeper block informaion. You can collect block information by using block class. You just have to pass parameters to invoke the pre-defined functions.

- [Permissions]((https://github.com/RecordsKeeper/recordskeeper-python-sdk/blob/python-3.0/recordskeeper_python_lib3/permissions.py) Library to work with RecordsKeeper permissions. You can grant and revoke permissions like connect, send, receive, create, issue, mine, activate, admin by using Assets class. You just have to pass parameters to invoke the pre-defined functions.

- [Stream]((https://github.com/RecordsKeeper/recordskeeper-python-sdk/blob/python-3.0/recordskeeper_python_lib3/stream.py) Library to work with RecordsKeeper streams. You can publish, retrieve and verify stream data by using stream class. You just have to pass parameters to invoke the pre-defined functions.

- [Transaction]((https://github.com/RecordsKeeper/recordskeeper-python-sdk/blob/python-3.0/recordskeeper_python_lib3/transaction.py) Library to work with RecordsKeeper transactions. You can send transaction, create raw transaction, sign raw transaction, send raw transaction, send signed transaction, retrieve transaction information and calculate transaction's fees by using transaction class. You just have to pass parameters to invoke the pre-defined functions.

- [Wallet]((https://github.com/RecordsKeeper/recordskeeper-python-sdk/blob/python-3.0/recordskeeper_python_lib3/wallet.py) Library to work with RecordsKeeper wallet functionalities. You can create wallet, dump wallet into a file, backup wallet into a file, import wallet from a file, lock wallet, unlock wallet, change wallet's password, retrieve private key, retrieve wallet's information, sign and verify message by using wallet class. You just have to pass parameters to invoke the pre-defined functions.

## Unit Tests

Under recordskeeper_python_lib3/test using test data from config.yaml file. 

- To run all the test cases:

```bash
python -m unittest discover -v
```

- To run a particular test case:

```bash
python -m unittest testname
```

- To run test cases with **green**:

```bash
green testname
```


## Documentation

The complete docs are here: [RecordsKeeper python library documentation](https://github.com/RecordsKeeper/recordskeeper-python-sdk/tree/python-3.0/docs/source).

- [Read for python version 3 or greater](https://github.com/RecordsKeeper/recordskeeper-python-sdk/tree/python-3.0/docs/source)
- [Read for python version 2](https://github.com/RecordsKeeper/recordskeeper-python-sdk/tree/master/docs/source)


## License

Copyright (c) 2016-2018 Recordskeeper 
License: GNU General Public License version 3, see COPYING

Portions copyright (c) 2014-2017 Coin Sciences Ltd
Portions copyright (c) 2009-2016 The Bitcoin Core developers
Portions copyright many others - see individual files