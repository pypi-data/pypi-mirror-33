import unittest
import yaml
import binascii
import json
from recordskeeper_python_lib3 import assets
from recordskeeper_python_lib3.assets import Assets

import sys

with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

net = assets.network

class AssetsTest(unittest.TestCase):


    def test_createasset(self):
        
        txid = Assets.createAsset(self, net['validaddress'], "xyz", 100)
        self.assertEqual(txid, "This wallet doesn't have keys with issue permission")

    def test_sendasset(self):
        
        txid = Assets.createAsset(self, net['validaddress'], "xyz", 100)
        self.assertEqual(txid, "This wallet doesn't have keys with issue permission")

    def test_retrieveassets(self):

        name = Assets.retrieveAssets(self)
        asset = json.loads(name)
        asset1 = asset['name']
        self.assertListEqual(asset1, [])

    def test_retrieveassets1(self):

        txid = Assets.retrieveAssets(self)
        tx_id = json.loads(txid)
        txid1 = tx_id['id']
        self.assertListEqual(txid1, [])


    def test_retrieveassets2(self):

        qty = Assets.retrieveAssets(self)
        qty1 = json.loads(qty)
        qty2 = qty1['qty']
        self.assertListEqual(qty2, [])


if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(AssetsTest)
    unittest.TextTestRunner(verbosity=2).run(suite)