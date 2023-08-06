import unittest
import yaml
import binascii
import sys
import json
from recordskeeper_python_lib import transaction
from recordskeeper_python_lib.transaction import Transaction

with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

net = transaction.network

class TransactionTest(unittest.TestCase):


    def test_sendtransaction(self):
        
        txid = Transaction.sendTransaction(self, net['miningaddress'], net['validaddress'], "hello", 0.2)
        tx_size = sys.getsizeof(txid)
        self.assertEqual(tx_size, 113)

    def test_sendrawtransaction(self):

        txid = Transaction.sendRawTransaction(self, net['dumpsignedtxhex'])
        tx_size = sys.getsizeof(txid)
        self.assertEqual(tx_size, 113)

    def test_signrawtransaction(self):

        txhex = Transaction.signRawTransaction(self, net['dumptxhex'], net['privatekey'])               #call to function signRawTransaction
        tx_size = sys.getsizeof(txhex)
        self.assertEqual(tx_size, 501)

    def test_createrawtransaction(self):

        txhex = Transaction.createRawTransaction(self, net['miningaddress'], net['validaddress'], net['amount'], net['testdata'])
        tx_size = sys.getsizeof(txhex)
        self.assertEqual(tx_size, 317)

    def test_sendsignedtransaction(self):

        txid = Transaction.sendSignedTransaction(self, net['miningaddress'], net['validaddress'] , net['amount'], net['privatekey'],net['testdata'])
        tx_size = sys.getsizeof(txid)
        self.assertEqual(tx_size, 113)


    def test_retrievetransaction(self):

        sentdata = Transaction.retrieveTransaction(self, net['dumptxid'])
        sent_data = json.loads(sentdata)
        data = sent_data['sent data']
        self.assertEqual(data, "hellodata")

    
    def test_getfee(self):

        fees = Transaction.getFee(self, net['miningaddress'], "4b1fbf9fb1e5c93cfee2d37ddc5fef444da0a05cc9354a834dc7155ff861a5e0")
        self.assertEqual(fees, 0.0269)



if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(TransactionTest)
    unittest.TextTestRunner(verbosity=2).run(suite)
