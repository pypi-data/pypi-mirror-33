import unittest
import yaml
import binascii
import json
from recordskeeper_python_lib import stream
from recordskeeper_python_lib.stream import Stream

import sys

with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

net = stream.network

class StreamTest(unittest.TestCase):


    def test_publish(self):
        
        txid = Stream.publish(self, net['miningaddress'], net['stream'], net['testdata'], "This is test data")
        tx_size = sys.getsizeof(txid)
        self.assertEqual(tx_size, 113)

    def test_retrieve_with_txid(self):

        result = Stream.retrieve(self, net['stream'], "eef0c0c191e663409169db0972cc75ff91e577a072289ee02511b410bc304d90")
        self.assertEqual(result,"testdata")


    def test_retrieve_with_id_address(self):

        result = Stream.retrieveWithAddress(self, net['stream'], net['miningaddress'], 20)
        address = json.loads(result)
        publisher_key = address['key'][0]
        self.assertEqual(publisher_key, "key1")
    
    def test_retrieve_with_key(self):

        result = Stream.retrieveWithKey(self, net['stream'], net['testdata'], 20)
        key = json.loads(result)
        publisher_data = key['data'][0]
        self.assertEqual(publisher_data, "This is test data")

    def test_verifyData(self):

        result = Stream.verifyData(self, net['stream'], net['testdata'], 5)
        self.assertEqual(result, "Data is successfully verified.")

    def test_retrieveItems(self):
        
        result = Stream.retrieveItems(self, net['stream'], 5)
        items = json.loads(result)
        published_items = items['data'][0]
        self.assertEqual(published_items, "Test data")
        

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(StreamTest)
    unittest.TextTestRunner(verbosity=2).run(suite)