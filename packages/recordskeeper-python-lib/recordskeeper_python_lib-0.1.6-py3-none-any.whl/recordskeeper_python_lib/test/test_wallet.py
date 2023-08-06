import unittest
import yaml
import binascii
import sys
import json
from recordskeeper_python_lib import wallet
from recordskeeper_python_lib.wallet import Wallet

with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

net = wallet.network

class WalletTest(unittest.TestCase):

    def test_createwallet(self):
        
        address = Wallet.createWallet(self)
        add = json.loads(address)
        add1 = add['public address']
        address_size = sys.getsizeof(add1)
        self.assertEqual(address_size, 83)

    def test_getprivkey(self):

        checkprivkey = Wallet.getPrivateKey(self, net['miningaddress'])
        self.assertEqual(checkprivkey, net['privatekey'])

    def test_retrievewalletinfo(self):

        wallet_balance = Wallet.retrieveWalletinfo(self)
        balance = json.loads(wallet_balance)
        walletbalance = balance['balance']
        self.assertGreaterEqual(wallet_balance, '0')

    def test_signmessage(self):

        signedMessage = Wallet.signMessage(self, net['privatekey'], net['testdata'])
        self.assertEqual(signedMessage, net['signedtestdata'])

    def test_verifymessage(self):

        validity = Wallet.verifyMessage(self, net['miningaddress'], net['signedtestdata'], net['testdata'])
        self.assertEqual(validity, 'Yes, message is verified')

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(WalletTest)
    unittest.TextTestRunner(verbosity=2).run(suite)