from aws_helpers.s3 import S3Client, S3Bucket
from botocore.exceptions import ClientError
import unittest
from aws_helpers.test import TEST_BUCKET_NAME, CD_BUCKET_NAME, REGION


class TestS3(unittest.TestCase):
    s3client = S3Client(REGION)

    def test_get_bucket(self):
        self.assertEqual(TEST_BUCKET_NAME, self.s3client.get_bucket(TEST_BUCKET_NAME).name)
        self.assertRaises(ValueError, self.s3client.get_bucket)

    def test_get_all_buckets(self):
        self.assertTrue(lambda: TEST_BUCKET_NAME in self.s3client.get_all_buckets())
    
    def test_create_bucket(self):
        try:
            bucket = self.s3client.get_bucket(CD_BUCKET_NAME)
            bucket.delete()
        except:
            pass
        self.s3client.create_bucket(CD_BUCKET_NAME)
        self.assertRaises(ClientError, lambda: self.s3client.create_bucket(CD_BUCKET_NAME))

    def test_delete_bucket(self):
        try:
            # Try to create bucket if it doesn't exist
            self.s3client.create_bucket(CD_BUCKET_NAME)
        except:
            pass
        self.s3client.get_bucket(CD_BUCKET_NAME).delete()


class TestBucket(unittest.TestCase):
    bucket = S3Bucket(TEST_BUCKET_NAME, REGION)


    def test_upload_file(self):
        self.bucket.upload_file('testfiles/.testkey.json', 'permtestkey.json')
        self.bucket.upload_file('testfiles/.testkey.json', '.testkey.json')
        self.assertEqual('test/.testkey.json', list(self.bucket.get_files('test/.testkey.json'))[0].key)
    

    def test_put_file(self):
        self.bucket.delete_files('.testkey2.json')
        # Pretend to put then check it's not there
        self.bucket.put_file('testfiles/.testkey.json', '.testkey2.json', mock=True)
        self.assertEqual(None, None if not list(self.bucket.get_files('.testkey2.json')) else 'some')
        # Actually put it and check it is there
        self.bucket.put_file('testfiles/.testkey.json', '.testkey2.json')
        self.assertEqual('.testkey2.json', list(self.bucket.get_files('.testkey2.json'))[0].key)
    

    def test_delete_files(self):
        # Put in case it isn't there already but it should bt
        self.bucket.put_file('testfiles/.testkey.json', '.testkey2.json')
        self.bucket.upload_file('testfiles/.testkey.json', '.testkey.json')

        # Pretend to delete .testkey.json
        self.bucket.delete_files('.testkey.json', mock=True)

        # Check that .testkey.json and testkey2.json still there
        self.assertEqual('some', None if not list(self.bucket.get_files('.testkey.json')) else 'some')
        self.assertEqual('some', None if not list(self.bucket.get_files('.testkey2.json')) else 'some')

        # Delete both files
        self.bucket.delete_files('.testkey')
        # Check that files are gone
        self.assertEqual(None, None if not list(self.bucket.get_files('.testkey.json')) else 'some')
        self.assertEqual(None, None if not list(self.bucket.get_files('.testkey2.json')) else 'some')


    def test_get_file(self):
        self.assertEqual('permtestkey.json', list(self.bucket.get_files('permtestkey.json'))[0].key)
        self.assertEqual(None, None if not list(self.bucket.get_files('.testkey.json')) else 'some')
    

    def test_upload_direcory(self):
        self.bucket.upload_directory('testfiles/', 'test/')
        self.assertEqual('some', None if not list(self.bucket.get_files('test/')) else 'some')

    
if __name__=="__main__":
    unittest.main()
