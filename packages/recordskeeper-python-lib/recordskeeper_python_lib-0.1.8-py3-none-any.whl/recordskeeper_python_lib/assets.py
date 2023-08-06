"""Library to work with assets.

   You can issue assets or retrieve assets information by using asset class.
   You just have to pass parameters to invoke the pre-defined functions."""

""" import requests, json and HTTPBasicAuth packages"""
	
import requests
import json
from requests.auth import HTTPBasicAuth
import yaml
import binascii
import sys

""" Entry point for accessing Stream class resources.

	Import values from config file."""

with open("config.yaml", 'r') as ymlfile:
   cfg = yaml.load(ymlfile)
   
   network = cfg['network']

   url = network['url']
   user = network['rkuser']
   password = network['passwd']
   chain = network['chain']
	
	
"""Assets class to access asset related functions"""

class Assets:
	
	"""function to create or issue an asset"""

	def createAsset(self, address, asset_name, asset_qty):		#createAsset() function definition
		
		self.address = address
		self.asset_name = asset_name
		self.asset_qty = asset_qty

		headers = { 'content-type': 'application/json'}

		payload = [
		         { "method": "issue",
		          "params": [self.address, self.asset_name, self.asset_qty],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]

		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()

		txid = response_json[0]['result']

		if (txid is None):

			txid = response_json[0]['error']['message']
		
		return txid;										#variable to store issue transaction id
	
	#txid = createAsset(address, asset_name, asset_qty)		#createAsset() function call	

	
	"""function to send assets to a particular address"""

	def sendAsset(self, address, assetname, qty):			#sendAsset() function definition

		self.address = address
		self.assetname = assetname
		self.qty = qty

		headers = { 'content-type': 'application/json'}

		payload = [
		         { "method": "sendasset",
		          "params": [self.address, self.assetname, self.qty],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()

		txid = response_json[0]['result']
		
		return txid;										#variable to store transaction id

	#  address, assetname, qty = sendAsset(self, address, assetname, qty) #call to invoke sendAsset() function

	"""function to retrieve assets information"""

	def retrieveAssets(self):								#retrieveAssets() function definition

		asset_name = []
		issue_id = []
		issue_qty = []

		headers = { 'content-type': 'application/json'}

		payload = [
		         { "method": "listassets",
		          "params": [],
		          "jsonrpc": "2.0",
		          "id": "curltext",
		          "chain_name": chain
		          }]
		response = requests.get(url, auth=HTTPBasicAuth(user, password), data = json.dumps(payload), headers=headers)
		response_json = response.json()

		asset_count = len(response_json[0]['result'])					#returns assets count

		for i in range(0, asset_count):

			asset_name.append(response_json[0]['result'][i]['name'])		#returns asset name
			issue_id.append (response_json[0]['result'][i]['issuetxid'])	#returns issue id
			issue_qty.append(response_json[0]['result'][i]['issueraw'])		#returns issue quantity

		asset_list = {'name':asset_name, 'id':issue_id, 'qty':issue_qty, "asset count":asset_count}
		assets = json.dumps(asset_list)
		
		return assets;

	# assetname, issueid, issueqty, assetcount = retrieveAssets()	#call to invoke retrieveAssets() function
	

	