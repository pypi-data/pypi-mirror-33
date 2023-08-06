"""Library to work with RecordsKeeper wallet.

   You can create wallet, create multisignature wallet, retrieve wallet's information, retrieve private key of a particular
   wallet address, sign message verify message, dump wallet file, backup wallet file, import wallet file, encrypt wallet by
   using wallet class. You just have to pass parameters to invoke the pre-defined functions."""

""" import requests, json, HTTPBasicAuth, yaml, sys and binascii packages"""

import requests
import json
from requests.auth import HTTPBasicAuth
import yaml
import sys
import binascii

""" Entry point for accessing Wallet class resources.

	Import values from config file."""

with open("config.yaml", 'r') as ymlfile:
   cfg = yaml.load(ymlfile)
   
   network = cfg['network']

   url = network['url']
   user = network['rkuser']
   password = network['passwd']
   chain = network['chain']
	

#Wallet class to access wallet related functions
class Wallet:

	"""function to create wallet on RecordsKeeper Blockchain"""

	def createWallet(self):										#createWallet() function definition
		
		headers = { 'content-type': 'application/json'}

		payload = [
		         { "method": "createkeypairs",
		          "params": [],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()

		public_address = response_json[0]['result'][0]['address']			# returns public address of the wallet
		private_key = response_json[0]['result'][0]['privkey']				# returns private key of the wallet
		public_key = response_json[0]['result'][0]['pubkey']					# returns public key of the wallet

		def importAddress(public_address):							#importAddress() function call

			headers = { 'content-type': 'application/json'}

			payload = [
		         { "method": "importaddress",
		          "params": [public_address, " ", False],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]
			response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
			response_json = response.json()
			
			result = response_json[0]['result']
			return result;

		import_address = importAddress(public_address)

		walletCredentials = {"public address": public_address, "private key": private_key, "public key": public_key}
		walletCredentialsjson = json.dumps(walletCredentials)
		
		return walletCredentialsjson;			#returns public and private key

	#publicaddress, privatekey, publickey = createWallet()	#call to function createWallet()	


	"""function to retrieve private key of a wallet on RecordsKeeper Blockchain"""

	def getPrivateKey(self, public_address):								#getPrivateKey() function definition

		self.public_address = public_address

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "dumpprivkey",
		      "params": [self.public_address],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
		result = response_json[0]['result']

		if result is None:

			private_key = response_json[0]['error']['message']

		else:
			
			private_key = response_json[0]['result']

		return private_key;							#returns private key

	#privkey = getPrivateKey(public_address)		#getPrivateKey() function call


	"""function to retrieve wallet's information on RecordsKeeper Blockchain"""

	def retrieveWalletinfo(self):							#retrieveWalletinfo() function call

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "getwalletinfo",
		      "params": [],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		balance = response_json[0]['result']['balance']
		tx_count = response_json[0]['result']['txcount']
		unspent_tx = response_json[0]['result']['utxocount']

		wallet_info = {"balance": balance, "tx count": tx_count, "unspent tx": unspent_tx}
		walletinfo = json.dumps(wallet_info)
		
		return walletinfo;	#returns balance, tx count, unspent tx

	#balance, tx_count, unspent_tx = retrieveWalletinfo()	#retrieveWalletinfo() function call


	"""function to create wallet's backup on RecordsKeeper Blockchain"""

	def backupWallet(self, filename):						#backupWallet() function call

		self.filename = filename

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "backupwallet",
		      "params": [self.filename],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		result = response_json[0]['result']

		if result is None:

			res = "Backup successful!"

		else:

			res = response_json[0]['error']['message']

		return res;								#returns result

	#result = backupWallet(filename)			#backupWallet() function call


	"""function to import wallet's backup on RecordsKeeper Blockchain"""

	def importWallet(self, filename):					#importWallet() function call

		self.filename = filename

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "importwallet",
		      "params": [self.filename],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		result = response_json[0]['result']

		if result is None:

			res = "Wallet is successfully imported"

		else:

			res = response_json[0]['error']['message']

		return res;								#returns result


	#result = importWallet(filename)			#importWallet() function call


	"""function to dump wallet on RecordsKeeper Blockchain"""

	def dumpWallet(self, filename):					#dumpWallet() function call

		self.filename = filename

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "dumpwallet",
		      "params": [self.filename],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		result = response_json[0]['result']

		if result is None:

			res = "Wallet is successfully dumped"

		else:

			res = response_json[0]['error']['message']

		return res;								#returns result

	#result = dumpWallet(filename)				#dumpWallet() function call


	"""function to lock wallet on RecordsKeeper Blockchain"""

	def lockWallet(self, password):					#lockWallet() function call

		self.password = password
		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "encryptwallet",
		      "params": [self.password],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		result = response_json[0]['result']

		if result is None:

			res = "Wallet is successfully encrypted."

		else:

			res = response_json[0]['error']['message']

		return res;								#returns result

	#result = lockWallet(password)				#lockWallet() function call

	"""function to unlock wallet on RecordsKeeper Blockchain"""

	def unlockWallet(self, password, unlocktime):				#unlockWallet() function call

		self.password = password
		self.unlocktime = unlocktime

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "walletpassphrase",
		      "params": [self.password, self.unlocktime],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		result = response_json[0]['result']

		if result is None:

			res = "Wallet is successfully unlocked."

		else:

			res = response_json[0]['error']['message']

		return res;								#returns result

	#result = unlockWallet()					#unlockWallet() function call


	"""function to change password for wallet on RecordsKeeper Blockchain"""

	def changeWalletPassword(self, old_password, new_password):		#changeWalletPassword() function call

		self.old_password = old_password
		self.new_password = new_password

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "walletpassphrasechange",
		      "params": [self.old_password, self.new_password],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		result = response_json[0]['result']

		if result is None:

			res = "Password successfully changed!"

		else:

			res = response_json[0]['error']['message']

		return res;								#returns result

	#result = changeWalletPassword(old_password, new_password)			#changeWalletPassword() function call


	"""function to sign message on RecordsKeeper Blockchain"""

	def signMessage(self, private_key, message):						#signMessage() function call

		self.private_key = private_key
		self.message = message

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "signmessage",
		      "params": [self.private_key, self.message],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		signedMessage = response_json[0]['result']

		return signedMessage;										#returns private key

	#signedmessage = signMessage(private_key, message)				#signMessage() function call


	"""function to verify message on RecordsKeeper Blockchain"""

	def verifyMessage(self, address, signedMessage, message):		#verifyMessage() function call

		self.address = address
		self.signedMessage = signedMessage
		self.message = message

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "verifymessage",
		      "params": [self.address, self.signedMessage, self.message],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		verifiedMessage = response_json[0]['result']

		if verifiedMessage is True:

			validity = "Yes, message is verified"
		
		else:

			validity = "No, signedMessage is not correct"

		return validity;										#returns validity

	#validity = verifyMessage(address, signedMessage, message)	#verifyMessage() function call
