"""Library to work with RecordsKeeper address class.

   You can generate new address, check all addresses, check address validity, check address permissions, check address balance
   by using Address class. You just have to pass parameters to invoke the pre-defined functions."""

""" import requests, json, HTTPBasicAuth, yaml, sys and binascii packages"""

import requests
import json
from requests.auth import HTTPBasicAuth
import yaml
import sys
import binascii

""" Entry point for accessing Address class resources.

	Import values from config file."""

with open("config.yaml", 'r') as ymlfile:
   cfg = yaml.load(ymlfile)
   
   network = cfg['network']

   url = network['url']
   user = network['rkuser']
   password = network['passwd']
   chain = network['chain']

#Address class to access address related functions
class Address:
   		
   	"""function to generate new address on the node's wallet"""

   	def getAddress(self):

   		headers = { 'content-type': 'application/json'}

   		payload = [{ "method": "getnewaddress", "params": [], "jsonrpc": "2.0", "id": "curltext", "chain_name": chain }]
   		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
   		response_json = response.json()

   		address = response_json[0]['result']
   		return address;									#returns new address

   	#newAddress = getAddress()							#getAddress() function call

   	"""function to generate a new multisignature address"""

   	def getMultisigAddress(self, nrequired, key):		#getMultisigAddress() function definition

   		self.nrequired = nrequired
   		self.key = key 

   		key_list = key.split(",")

   		self.key_list = key_list

   		headers = { 'content-type': 'application/json'}

   		payload = [{ "method": "createmultisig", "params": [self.nrequired, self.key_list], "jsonrpc": "2.0", "id": "curltext", "chain_name": chain}]

   		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
   		response_json = response.json()

   		address = response_json[0]['result']

   		if address is None:

   			res = response_json[0]['error']['message']

   		else:

   			res = response_json[0]['result']['address']

   		return res;										#returns new multisig address

   	#newAddress = getMultisigAddress(nrequired, key)	#getMultisigAddress() function call

   	"""function to generate a new multisignature address on the node's wallet"""

   	def getMultisigWalletAddress(self, nrequired, key):

   		self.nrequired = nrequired
   		self.key = key

   		key_list = key.split(",")
   		self.key_list = key_list

   		headers = { 'content-type': 'application/json'}

   		payload = [ { "method": "addmultisigaddress", "params": [self.nrequired, self.key_list], "jsonrpc": "2.0", "id": "curltext", "chain_name": chain }]
   		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
   		response_json = response.json()

   		address = response_json[0]['result']

   		if address is None:

   			res = response_json[0]['error']['message']

   		else:

   			res = response_json[0]['result']

   		return res;									#returns new multisig address

   	#newAddress = getMultisigWalletAddress(nrequired, key)	#getMultisigWalletAddress() function call

   	"""function to list all addresses and no of addresses on the node's wallet"""
   	
   	def retrieveAddresses(self):						#retrieveAddresses() function call\

         headers = { 'content-type': 'application/json'}

         payload = [ { "method": "getaddresses", "params": [], "jsonrpc": "2.0", "id": "curltext", "chain_name": chain }]

         response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)

         response_json = response.json()

         address_count = len(response_json[0]['result'])

         address = []

         for i in range(0, address_count):

            address.append(response_json[0]['result'][i])

         address_response = {"address": address, "address count": address_count}

         addresses = json.dumps(address_response)

         return addresses;					#returns allAddresses and address count

   	#allAddresses, address_count = retrieveAddresses()	#retrieveAddresses() function call

   	"""function to check if given address is valid or not"""

   	def checkifValid(self, address):						#checkifValid() function definition
   		
   		self.address = address

   		headers = { 'content-type': 'application/json'}

   		payload = [ { "method": "validateaddress", "params": [self.address], "jsonrpc": "2.0", "id": "curltext", "chain_name": chain}]
   		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
   		response_json = response.json()

   		validity = response_json[0]['result']['isvalid']

   		if validity is True:

   			addressCheck = "Address is valid"		#print if address is valid

   		else:

   			addressCheck= "Address is invalid"		#print if address is invalid	

   		return addressCheck;						#returns validity of address

   	#addressC = checkifValid('self', 'wGUjFtakjkZRNF1sYnDtd5Now6zEWUGcC')
	
   	"""function to check if given address has mining permission or not"""

   	def checkifMineAllowed(self, address):				#checkifMineAllowed() function definition

         self.address = address

         headers = { 'content-type': 'application/json'}

         payload = [ { "method": "validateaddress", "params": [self.address], "jsonrpc": "2.0", "id": "curltext", "chain_name": chain }]

         response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)

         response_json = response.json()

         check = response_json[0]['result']['isvalid']

         if (check == True):

            permission = response_json[0]['result']['ismine']

            if permission is True:

               permissionCheck = "Address has mining permission"	#print if address has mining permission

            else:

               permissionCheck = "Address has not given mining permission"	#print if address does not have mining permission	

         else:

            permissionCheck = "Invalid address, please check for valid address"

         return permissionCheck;							#returns mining permission

   	#permissionCheck = checkifMineAllowed(address)	#checkifMineAllowed() function call

   	"""function to check node address balance on RecordsKeeper Blockchain"""

   	def checkBalance(self, address):					#checkBalance() function definition

   		self.address = address

   		headers = { 'content-type': 'application/json'}

   		payload = [ { "method": "getaddressbalances", "params": [self.address], "jsonrpc": "2.0", "id": "curltext", "chain_name": chain}]
   		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)

   		response_json = response.json()

   		balance = response_json[0]['result'][0]['qty']

   		return balance;							#returns balance of a particular node address

   	#address_balance = checkBalance(address)	#checkBalance() function call

   	"""function to import address on RecordsKeeper Blockchain"""

   	def importAddress(self, public_address):				#importAddress() function call

   		self.public_address = public_address 

   		headers = { 'content-type': 'application/json'}
   		payload = [{ "method": "importaddress", "params": [self.public_address, " ", False], "jsonrpc": "2.0", "id": "curltext", "chain_name": chain}]
   		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
   		response_json = response.json()

   		result = response_json[0]['result']

   		error = response_json[0]['error']

   		if result is None and error is None:

   			resp = "Address successfully imported"

   		elif (result is None and error != None):

   			resp = response_json[0]['error']['message']			#returns new multisig address

   		else:

   			resp = 0

   		return resp;

	#import_address = importAddress(address)	#importAddress() function call