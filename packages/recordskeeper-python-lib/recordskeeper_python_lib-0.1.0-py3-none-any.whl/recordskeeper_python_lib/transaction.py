"""Library to work with RecordsKeeper transactions.

   You can send transaction, create raw transaction, sign raw transaction, send raw transaction, send signed transaction,
   retrieve transaction information and calculate transaction's fees by using transaction class. You just have to pass
   parameters to invoke the pre-defined functions."""

""" import requests, json, HTTPBasicAuth, yaml, sys and binascii packages"""

import requests
import json
from requests.auth import HTTPBasicAuth
import yaml
import sys
import binascii
import codecs


""" Entry point for accessing Transaction class resources.

	Import values from config file."""

with open("config.yaml", 'r') as ymlfile:
   cfg = yaml.load(ymlfile)
   
   network = cfg['network']

   url = network['url']
   user = network['rkuser']
   password = network['passwd']
   chain = network['chain']
	

#Transaction class to access transaction related functions
class Transaction:
	 
	"""function to send transaction on RecordsKeeper Blockchain"""

	def sendTransaction(self, sender_address, reciever_address, data, amount):		#sendTransaction function definition
	
		
		data_hex = binascii.hexlify(data)

		self.sender_address = sender_address
		self.reciever_address = reciever_address
		self.amount = amount
		self.data_hex = data_hex
		
		headers = { 'content-type': 'application/json'}
		payload = [
		         { "method": "createrawsendfrom",
		          "params": [self.sender_address, {self.reciever_address : self.amount}, [self.data_hex], "send"],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()

		txid = response_json[0]['result']

		return txid;								#return transaction id


	#txid = sendTransaction(sender_address, reciever_address, data, amount)	#call to function sendTransaction


	"""function to create transaction hex on RecordsKeeper Blockchain"""

	def createRawTransaction(self, sender_address, reciever_address, amount, data):		#createRawTransaction() function definition

		datahex = binascii.hexlify(data)
		self.sender_address = sender_address
		self.reciever_address = reciever_address
		self.amount = amount
		self.datahex = datahex

		headers = { 'content-type': 'application/json'}
		payload = [
		         { "method": "createrawsendfrom",
		          "params": [self.sender_address, {self.reciever_address : self.amount}, [self.datahex], ''],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]
		
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()

		txhex = response_json[0]['result']
		
		return txhex;						# return transaction hex of raw transaction


	#tx_hex = createRawTransaction(sender_address, reciever_address, amount, data)	#call to function createRawTransaction


	"""function to sign transaction on RecordsKeeper Blockchain"""

	def signRawTransaction(self, txHex, private_key):							#signRawTransaction() function definition		

		priv_key = []

		priv_key.append(private_key)

		self.txHex = txHex
		self.priv_key = priv_key

		headers = { 'content-type': 'application/json'}
		
		payload = [
		         { "method": "signrawtransaction",
		          "params": [self.txHex, [], self.priv_key],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()

		signedHex = response_json[0]['result']['hex']
		
		return signedHex;

	#signed_hex = signRawTransaction(txHex, private_key)				#call to function signRawTransaction()


	"""function to send raw transaction on RecordsKeeper Blockchain"""

	def sendRawTransaction(self, signed_txHex):				#sendRawTransaction function definition

		self.signed_txHex = signed_txHex

		headers = { 'content-type': 'application/json'}

		payload = [
		         { "method": "sendrawtransaction",
		          "params": [self.signed_txHex],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
		
		txn = response_json[0]['result']	
		
		if txn is None:

			txid = response_json[0]['error']['message']
		
		else:

			txid = txn
		
		return txid;

	#result = sendRawTransaction(signed_txHex)					#call to function sendRawTransaction

	"""function to send signed transaction on RecordsKeeper Blockchain"""

	def sendSignedTransaction(self, sender_address, reciever_address, amount, private_key, data):									#sendSignedTransaction function definition

		datahex = binascii.hexlify(data)

		self.sender_address = sender_address
		self.reciever_address = reciever_address
		self.amount = amount
		self.private_key = private_key
		self.datahex = datahex

		def createRawTransaction(sender_address, reciever_address, amount, datahex):

			headers = { 'content-type': 'application/json'}

			payload = [
			         { "method": "createrawsendfrom",
			          "params": [self.sender_address, {self.reciever_address : self.amount}, [self.datahex], ""],
			          "jsonrpc": "2.0",
			          "id": "curltext",
			          "chain_name": chain
			          }]
			
			response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
			response_json = response.json()
		
			return response_json[0]['result']				

		
		txHex = createRawTransaction(sender_address, reciever_address, float(amount), datahex)	
		

		def signRawTransaction(txHex, private_key):

			headers = { 'content-type': 'application/json'}

			payload = [
			         { "method": "signrawtransaction",
			          "params": [txHex, [], [self.private_key]],
			          "jsonrpc": "2.0",
			          "id": "curltext",
			          "chain_name": chain
			          }]

			response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
			response_json = response.json()
			
			return response_json[0]['result']['hex']

		signed_tx_hex = signRawTransaction(txHex, private_key)	
		

		def sendRawTransaction(signed_tx_hex):							

			headers = { 'content-type': 'application/json'}

			payload = [
			         { "method": "sendrawtransaction",
			          "params": [signed_tx_hex],
			          "jsonrpc": "2.0",
			          "id": "curltext",
			          "chain_name": chain
			          }]

			response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
			response_json = response.json()

			return response_json[0]['result']	

		tx_id = sendRawTransaction(signed_tx_hex)						

		return tx_id;												

	#transaction_id = sendSignedTransaction(sender_address, reciever_address, amount, private_key, data)	#call to sendSigned Transaction


	"""function to retrieve transaction on RecordsKeeper Blockchain"""

	def retrieveTransaction(self, tx_id):						#retrieveTransaction function definition
		
		self.tx_id = tx_id

		headers = { 'content-type': 'application/json'}


		payload = [
		         { "method": "getrawtransaction",
		          "params": [self.tx_id, 1],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()

		
		sent_hex_data = response_json[0]['result']['data'][0]
		
		sent_data = binascii.unhexlify(sent_hex_data).decode('utf-8')

		sent_amount = response_json[0]['result']['vout'][0]['value']

		transaction_info = {"sent amount": sent_amount, "sent data": sent_data}
		transactioninfo = json.dumps(transaction_info)

		return transactioninfo;	#returns data from retrieved transaction

	#sentdata, sentamount = retrieveTransaction(tx_id)	#call to function retrieveTransaction()
	
	"""function to calculate transaction's fee on RecordsKeeper Blockchain"""

	def getFee(self, address, tx_id):					#getFee() function definition

		self.address = address
		self.tx_id = tx_id

		headers = { 'content-type': 'application/json'}

		payload = [

		         { "method": "getaddresstransaction",
		          "params": [self.address, self.tx_id, True],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
		
		sent_amount = response_json[0]['result']['vout'][0]['amount']

		balance_amount = response_json[0]['result']['balance']['amount']

		fees = (abs(balance_amount) - sent_amount)
		
		return fees;				#returns fees

	
	#Fees = getFee(address, tx_id)	#call to function getFee()
