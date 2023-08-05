#!/bin/python3

from boto3.session import Session
from botocore.exceptions import ClientError
from boto3.exceptions import S3UploadFailedError
import json
import os


def load_access_keys(access_key_path):
    # Get AWS credentials
    with open(os.path.expanduser(access_key_path)) as f:
        creds = json.load(f)

    ACCESS_KEY=creds.get('access-key')
    SECRET_KEY=creds.get('secret-access-key')
    return (ACCESS_KEY, SECRET_KEY)


class S3Client():
    """Creates an s3 session.
    
    Raises:
        ValueError -- [description]
        ValueError -- [description]
    
    Returns:
        [type] -- [description]
    """

    region_name = None
    resource = None
    access_key_path = None

    def __init__(self, region_name, load_access_keys = lambda: load_access_keys(access_key_path='~/.rootkey.json')):
        self.region_name = region_name
        self.load_access_keys = load_access_keys
        self.resource = self.__get_s3_resource()


    def __get_s3_resource(self):
        """Using *load_access_keys* function to load authentication keys to connect to aws region of the class.

        File at *access_key_path* contains: {'access-key':'ABC', 'secret-access-key':'ABC'}
        
        Keyword Arguments:
            access_key_path {str} -- Path to access keys. (default: {'~/.rootkey.json'})
            region_name {str} -- [description] (default: {''})
        
        Returns:
            [Amazon S3 session.resource] -- s3 session.resource is used for future s3 interactions.
        """

        ACCESS_KEY, SECRET_KEY = self.load_access_keys()

        session = Session(
                aws_access_key_id=ACCESS_KEY,
                aws_secret_access_key=SECRET_KEY,
                region_name=self.region_name)
        return session.resource('s3')

    # GET
    def get_bucket(self, bucket_name=None):
        if not bucket_name:
            raise ValueError('No bucket_name.')
        if not self.resource.Bucket(bucket_name) in self.resource.buckets.all():
            msg = 'The bucket "{}" does not exist.'.format(bucket_name)
            raise ValueError(msg)
        return self.resource.Bucket(bucket_name)
    
    def get_all_buckets(self):
        """ Function to list all available bucket names."""
        return [bucket.name for bucket in self.resource.buckets.all()]
    
    # CREATE
    def create_bucket(self, bucket_name):
        return self.resource.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': self.region_name})
    
    def delete_bucket(self, bucket_name):
        bucket = self.resrouce.Bucket(bucket_name)
        bucket.delete()

class S3Bucket():
    bucket_name = None
    bucket_region = None
    def __init__(self, bucket_name, bucket_region):
        self.bucket_name = bucket_name
        self.bucket_region = bucket_region
        self.s3Client = S3Client(region_name = bucket_region)
        self.client = self.s3Client.get_bucket(bucket_name)


    def upload_file(self, local_file, s3_path):
        self.client.upload_file(local_file, s3_path)

    def put_file(self, local_file, s3_path, content_type='', content_disposition='', acl='', mock=False):
        """

        Keyword Arguments:
            local_file {str} -- [description]
            s3_path {str} -- [description]
            content_type {str} -- [description] (default: {''})
            content_disposition {str} -- [description] (default: {''})
            acl {str} -- [description] (default: {''})
            mock {bool} -- [description] (default: {False})
        """
        print ('Uploading "{}" to "{}"'.format(local_file, s3_path))
        if not mock:
            # Upload a new file
            with open(local_file, 'rb') as data:
                self.client.put_object(Key=s3_path, Body=data, ContentType=content_type, ContentDisposition=content_disposition, ACL=acl)
        return True


    def upload_directory(self, local_directory='', target_directory='', ignore_dirs=[], content_type='', content_disposition='', acl=''):
        """Upload all files in *local_directory* to *target_directory* on bucket.
        
        Keyword Arguments:
            local_directory {str} -- [description] (default: {''})
            target_directory {str} -- [description] (default: {''})
            ignore_dirs {list} -- [description] (default: {[]})
            content_type {str} -- [description] (default: {''})
            content_disposition {str} -- [description] (default: {''})
            acl {str} -- [description] (default: {''})
        """
        print('Uploading to bucket: {}'.format(self.bucket_name))
        for root, dirs, files in os.walk(local_directory):
            for filename in files:
                local_path = os.path.join(root, filename)
                relative_path = os.path.relpath(local_path, local_directory)

                ignore = False
                for ig in ignore_dirs:
                    if relative_path.startswith(ig):
                        print('Ignoring: {}'.format(relative_path))
                        ignore = True
                if ignore:
                    continue

                s3_path = os.path.join(target_directory, relative_path)
                print ('Uploading "{}" to "{}"'.format(relative_path, s3_path))

                # Upload a new file
                self.upload_file(relative_path, s3_path) 
        return True


    def get_files(self, prefix='', delimiter=''):
        return self.client.objects.filter(Prefix=prefix, Delimiter=delimiter)


    def delete_files(self, prefix='', delimiter='', mock=False):
        for s3_file in self.get_files(prefix, delimiter):
            print('Deleting {}'.format(s3_file.key))
            if not mock:
                s3_file.delete()


    def set_s3_acl(acl='public-read', prefix='', delimiter=''):
        for s3_file in self.get_files(prefix, delimiter):
            s3_file.Acl().put(ACL=acl)
