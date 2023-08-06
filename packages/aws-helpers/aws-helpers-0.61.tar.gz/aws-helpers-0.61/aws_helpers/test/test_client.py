from botocore.exceptions import ClientError
import boto3.session
import unittest
from aws_helpers.client import load_access_keys, Client
from aws_helpers.test import REGION


class AccessKeysTest(unittest.TestCase):
    def test_load_access_keys(self):
        access_key, secret_key = load_access_keys(access_key_path='testfiles/.testkey.json')
        self.assertEqual('ABC',access_key)
        self.assertEqual('DEF',secret_key)

        self.assertRaises(OSError, lambda: load_access_keys('fail'))


class ClientTest(unittest.TestCase):
    def test_fail_client(self):
        # Invalid region
        bad_region = Client('EU (Ireland)')
        # Invalid keys
        bad_keys = Client(REGION, lambda: load_access_keys('testfiles/.testkey.json'))

    def test_get_session(self):
        client = Client(REGION)
        sess = client.get_session()

    def test_get_resource(self):
        client = Client(REGION)
        # Check that resource you get has correct boto3 type
        s3 = client.get_resource('s3')
        

if __name__=="__main__":
    unittest.main()
