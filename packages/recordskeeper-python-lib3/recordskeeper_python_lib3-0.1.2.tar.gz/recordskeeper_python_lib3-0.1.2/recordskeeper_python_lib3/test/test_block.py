import unittest
import yaml
import json
from recordskeeper_python_lib3 import block
from recordskeeper_python_lib3.block import Block

import sys


with open("config.yaml", 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

net = block.network

class BlockTest(unittest.TestCase):

    def test_block_info(self):

        miner = Block.blockinfo(self, "100")
        miner_address = json.loads(miner)
        miner_add = miner_address['miner']  
        self.assertEqual(miner_add, net['mainaddress'])
        
        size = Block.blockinfo(self, "100")
        block_size = json.loads(size)
        blocksize = block_size['size']
        self.assertEqual(blocksize, 300)

        nonce = Block.blockinfo(self, "100")
        block_nonce = json.loads(nonce)
        blocknonce = block_nonce['nonce']
        self.assertEqual(blocknonce, 260863)

        merkleroot = Block.blockinfo(self, "100")
        merkle_root = json.loads(merkleroot)
        block_merkleroot = merkle_root['merkleroot']
        self.assertEqual(block_merkleroot, 'c6d339bf75cb969baa4c65e1ffd7fade562a191fa90aac9dd495b764f2c1b429')


    def test_retrieveBlocks(self):

        miner = Block.retrieveBlocks(self, "10-20")
        miner_address = json.loads(miner)
        mineraddress = miner_address['miner'][0]
        self.assertEqual(mineraddress, net['mainaddress'])

        txcount = Block.retrieveBlocks(self, "10-20")
        tx_count = json.loads(txcount)
        blocktxcount = tx_count['tx count'][0]
        self.assertEqual(blocktxcount, 1)

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BlockTest)
    unittest.TextTestRunner(verbosity=2).run(suite)