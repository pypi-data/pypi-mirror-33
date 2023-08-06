#!/bin/python3

from botocore.exceptions import ClientError
from boto3.exceptions import S3UploadFailedError
from aws_helpers.client import Client
import json
import os


class S3Client(Client):
    """Returns an S3Client object which has functions to aid interacting with Amazon s3.
    
    Returns:
        S3Client
    """
    resource = None


    def __init__(self, region_name, replacement_access_key_function = None):
        """Set properties of the S3Client.
        
        Arguments:
            region_name {str} -- AWS region name e.g. for EU (Ireland): eu-west-1
        
        Keyword Arguments:
            load_access_keys {function} -- A function which returns a tuple of str's (access-key, secret-access-key) (default: {lambda:load_access_keys(access_key_path='~/.rootkey.json')})
        """

        super(S3Client, self).__init__(region_name, replacement_access_key_function)
        self.__set_s3_resource()


    def __set_s3_resource(self):
        """Set self.resource to boto3.session.resource."""
        self.resource = self.session.resource('s3')


    def get_s3_resource(self):
        """Get boto3.session.resource('s3') object.
        
        Returns:
            boto3.session.resource('s3) -- boto3 S3 resource.
        """
        return self.get_resource('s3')


    def get_bucket(self, bucket_name=None):
        """Get an S3 bucket object (boto3.session.resource.Bucket) for the current S3Client.
        
        Keyword Arguments:
            bucket_name {str} -- AWS bucket name (default: {None})
        
        Raises:
            ValueError -- If bucket does not exist or bucket_name not provided.
        
        Returns:
            boto3.session.resource.Bucket -- S3 bucket object.
        """

        if not bucket_name:
            raise ValueError('No bucket_name.')
        if not self.resource.Bucket(bucket_name) in self.resource.buckets.all():
            msg = 'The bucket "{}" does not exist.'.format(bucket_name)
            raise ValueError(msg)
        return self.resource.Bucket(bucket_name)


    def get_all_buckets(self):
        """Function to return a list of all Bucket objects available with this S3Client."""
        return self.resource.buckets.all()


    def list_all_buckets(self):
        """ Function to return a list of all available bucket names."""
        return [bucket.name for bucket in self.get_all_buckets()]
    

    def create_bucket(self, bucket_name):
        """Create a bucket using this S3Client in this S3Client's region."""
        return self.resource.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': self.region_name})
    

    def delete_bucket(self, bucket_name):
        """Delete bucket with *bucket_name* using this S3Client.
        
        Arguments:
            bucket_name {str} -- Name of bucket to delete.
        """

        bucket = self.get_bucket(bucket_name)
        bucket.delete()


class S3Bucket():
    bucket_name = None
    bucket_region = None
    def __init__(self, bucket_name, bucket_region):
        self.bucket_name = bucket_name
        self.bucket_region = bucket_region
        self.s3_client = S3Client(region_name = bucket_region)
        self.client = self.s3_client.get_bucket(bucket_name)


    def upload_file(self, local_file, s3_path, mock=False):
        """Upload file at *local_file* path to *s3_path"
        
        Arguments:
            local_file {str} -- Path to local file.
            s3_path {str} -- Path on S3.
        
        Keyword Arguments:
            mock {bool} -- Print what would have happened but don't upload anything. (default: {False})
        """

        print("Uploading {0} to {1}".format(local_file, s3_path))
        if not mock:
            self.client.upload_file(local_file, s3_path)


    def put_file(self, local_file, s3_path, content_type='', content_disposition='', acl='', mock=False):
        """

        Keyword Arguments:
            local_file {str} -- Path to local file.
            s3_path {str} -- Path to save file to on S3 bucket.
            content_type {str} -- Mimetype e.g. text/html or stylesheet (default: {''})
            content_disposition {str} -- e.g. inline, attachment, form-data (default: {''})
            acl {str} -- ACL rules for content access e.g. 'public-read' (default: {''})
            mock {bool} -- Print what would have happened but don't put anything. (default: {False})
        """
        print ('Uploading "{}" to "{}"'.format(local_file, s3_path))
        if not mock:
            # Upload a new file
            with open(local_file, 'rb') as data:
                self.client.put_object(Key=s3_path, Body=data, ContentType=content_type, ContentDisposition=content_disposition, ACL=acl)
        return True


    def upload_directory(self, local_directory, target_directory, ignore_dirs=[], content_type='', content_disposition='', acl=''):
        """Upload all files in *local_directory* to *target_directory* on bucket.
        
        Keyword Arguments:
            local_directory {str} -- Path to local directory.
            target_directory {str} -- Path to target directory on S3 to upload into. 
            ignore_dirs {list} -- Ignore local directories starting with these strings. (default: {[]})
            content_type {str} -- Mimetype e.g. text/html or stylesheet (default: {''})
            content_disposition {str} -- e.g. inline, attachment, form-data (default: {''})
            acl {str} -- ACL rules for content access e.g. 'public-read' (default: {''})
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
                print ('Uploading "{}" to "{}"'.format(local_path, s3_path))

                # Upload a new file
                self.upload_file(local_path, s3_path) 
        return True


    def get_files(self, prefix='', delimiter=''):
        """Get AWS S3 files.
        
        Keyword Arguments:
            prefix {str} -- All files with this prefix. (default: {''})
            delimiter {str} -- Do not include files with this prefix. (default: {''})
        
        Returns:
            S3 object iterator -- Object iterator (similar to a list, can convert using list(get_files())) containing all the files that matched.
        """

        return self.client.objects.filter(Prefix=prefix, Delimiter=delimiter)


    def delete_files(self, prefix='', delimiter='', mock=False):
        """Delete all files on S3 matching the prefix, ignoring those that match the delimiter.
        
        Keyword Arguments:
            prefix {str} -- String to match. (default: {''})
            delimiter {str} -- Files to not include. (default: {''})
            mock {bool} -- Print what would have happened but don't delete anything. (default: {False})
        """

        for s3_file in self.get_files(prefix, delimiter):
            print('Deleting {}'.format(s3_file.key))
            if not mock:
                s3_file.delete()


    def set_s3_acl(acl='public-read', prefix='', delimiter='', mock=False):
        """Set ACL status for files matching *prefix* and not containing *delimiter*.
        
        Keyword Arguments:
            acl {str} -- ACL rules for content access e.g. 'public-read' (default: {'public-read'})
            prefix {str} -- String to match. (default: {''})
            delimiter {str} -- Files to not include. (default: {''})
        """

        print("Setting ACL status for {0} to {1}".format(prefix, alc))
        if not mock:
            for s3_file in self.get_files(prefix, delimiter):
                s3_file.Acl().put(ACL=acl)
