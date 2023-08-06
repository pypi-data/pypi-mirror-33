"""Library to work with RecordsKeeper Blockchain.

   You can retrieve blockchain information, node's information, node's balance, node's permissions, pending transaction details
   by using Blockchain class.
   You just have to pass parameters to invoke the pre-defined functions."""

""" import requests, json, HTTPBasicAuth, yaml, sys and binascii packages"""

import requests
import json
from requests.auth import HTTPBasicAuth
import yaml
import sys
import binascii

""" Entry point for accessing Blockchain class resources.

	Import values from config file."""

with open("config.yaml", 'r') as ymlfile:
   cfg = yaml.load(ymlfile)
   
   network = cfg['network']

   url = network['url']
   user = network['rkuser']
   password = network['passwd']
   chain = network['chain']
	

#Blockchain class to access blockchain related functions
class Blockchain:

	"""function to retrieve RecordsKeeper Blockchain parameters"""

	def getChainInfo(self):								#getChainInfo() function definition
		
		headers = { 'content-type': 'application/json'}

		payload = [
		         { "method": "getblockchainparams",
		          "params": [],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		result = response_json[0]['result']

		chain_protocol = result['chain-protocol']
		chain_description = result['chain-description']
		root_stream = result['root-stream-name']
		max_blocksize = result['maximum-block-size']
		default_networkport = result['default-network-port']
		default_rpcport = result['default-rpc-port']
		mining_diversity = result['mining-diversity']
		chain_name = result['chain-name']

		chaininfo_response = {"chain-description": chain_description, "chain-protocol": chain_protocol, "root-stream-name":root_stream, "maximum-blocksize": max_blocksize, "default-network-port": default_networkport, "default-rpc-port": default_rpcport, "mining-diversity": mining_diversity, "chain-name": chain_name}
		chaininfo = json.dumps(chaininfo_response)

		return chaininfo;										#returns chain parameters

	#chain = getChainInfo()				 			#call to function getChainInfo()	


	"""function to retrieve node's information on RecordsKeeper Blockchain"""

	def getNodeInfo(self):								#getNodeInfo() function definition

		headers = { 'content-type': 'application/json'}

		payload = [

		 	{ "method": "getinfo",
		      "params": [],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		node_balance = response_json[0]['result']['balance']
		synced_blocks = response_json[0]['result']['blocks']
		node_address = response_json[0]['result']['nodeaddress']
		difficulty = response_json[0]['result']['difficulty']

		node_info = {"node balance": node_balance, "synced blocks": synced_blocks, "node address": node_address, "difficulty": difficulty}
		nodeinfo = json.dumps(node_info)

		return nodeinfo;	#returns node details

	#node = getNodeInfo(public_address)	#getNodeInfo() function call


	"""function to retrieve node's permissions on RecordsKeeper Blockchain"""

	def permissions(self):							#permissions() function definition

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "listpermissions",
		      "params": [],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
		
		pms_count = len(response_json[0]['result'])
		
		permissions = []

		for i in range(0, pms_count):
			permissions.append(response_json[0]['result'][i]['type'])

		return permissions;							#returns list of permissions

	#result = permissions()							#permissions() function call


	"""function to retrieve pending transactions information on RecordsKeeper Blockchain"""

	def getpendingTransactions(self):						#getpendingTransactions() function call

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "getmempoolinfo",
		      "params": [],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		tx_count = response_json[0]['result']['size']		#store pending tx count

		if (tx_count != 0):

			headers = { 'content-type': 'application/json'}

			payload = [
		 	{ "method": "getrawmempool",
		      "params": [],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]

			response2 = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
			response_json2 = response2.json()
			
			tx = []

			for i in range(0, tx_count):
				tx.append(response_json2[0]['result'])

		else:

			tx = "Currently, No Pending Transactions"
		
		pending_transactions = {"tx_count": tx_count, "tx": tx}
		pendingresult = json.dumps(pending_transactions)

		return pendingresult;	#returns pending tx and tx count

	#pendingtx, pendingtxcount = getpendingTransactions()		#getpendingTransactions() function call


	"""function to check node's total balance """

	def checkNodeBalance(self):							#checkNodeBalance() function definition

		headers = { 'content-type': 'application/json'}

		payload = [
		 	{ "method": "getmultibalances",
		      "params": [],
		      "jsonrpc": "2.0",
		      "id": "curltext",
		      "chain_name": chain
		    }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()
			
		balance = response_json[0]['result']['total'][0]['qty']

		return balance;							#returns balance of complete node

	#node_balance = checkNodeBalance()		#checkNodeBalance() function call

	
	

