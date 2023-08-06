import unittest
import yaml
import binascii
import json
from recordskeeper_python_lib import blockchain
from recordskeeper_python_lib.blockchain import Blockchain

import sys

with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

net = blockchain.network

class BlockchainTest(unittest.TestCase):

    def test_getchaininfo(self):
        
        chainname = Blockchain.getChainInfo(self)
        chain_name = json.loads(chainname)
        chainName = chain_name['chain-name']
        self.assertEqual(chainName, net['chain'])

    def test_getnodeinfo(self):

        info = Blockchain.getNodeInfo(self)
        chain_info = json.loads(info)
        chaininfo = chain_info['synced blocks']
        self.assertGreater(info, '60')


    def test_permissions(self):

        permissions = Blockchain.permissions(self)
        self.assertListEqual(permissions, ['mine', 'admin', 'activate', 'connect', 'send', 'receive', 'issue', 'create'])


    def test_getpendingtransactions(self):

        pendingtx = Blockchain.getpendingTransactions(self)
        pending_tx = json.loads(pendingtx)
        pendingtxcount = pending_tx['tx_count']
        self.assertListEqual(pendingtx, "Currently, No Pending Transactions")

    def test_checknodebalance(self):

        balance = Blockchain.checkNodeBalance(self)
        self.assertGreater(balance, 0)


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BlockchainTest)
    unittest.TextTestRunner(verbosity=2).run(suite)