#!/bin/python3

from boto3.session import Session
import json
import os


def get_s3_session(access_json_path='~/.rootkey.json',region_name=''):
    # Get AWS credentials
    with open(os.path.expanduser(access_json_path)) as f:
        creds = json.load(f)

    ACCESS_KEY=creds.get('access-key')
    SECRET_KEY=creds.get('secret-access-key')

    session = Session(
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            region_name=region_name)
    return session.resource('s3')


def get_bucket(bucket_name=None, bucket_region=None):
    if not bucket_name or not bucket_region:
        raise ValueError('No bucket_region or name.')
    if not bucket_name:
        raise ValueError('No bucket_name.')
    if not bucket_region:
        raise ValueError('No bucket_region.')

    return get_s3_session(region_name=bucket_region).Bucket(bucket_name)


def upload_file(local_file='', target_file='', bucket_name='', bucket_region='', content_type='', content_disposition='', acl='', mock=False):
            print ('Uploading "{}" to "{}"'.format(local_file, target_file))
            if not mock:
                # Upload a new file
                with open(local_file, 'rb') as data:
                   get_bucket(bucket_name, bucket_region).put_object(Key=s3_path, Body=data, ContentType=content_type, ContentDisposition=content_disposition, ACL=acl)
            return


def upload_directory(local_directory='', target_directory='', ignore_dirs=[], bucket_name='', bucket_region='', content_type='', content_disposition='', acl=''):
    """Upload all files in *local_directory* to *target_directory* on bucket.
    
    Keyword Arguments:
        local_directory {str} -- Local directory. (default: {'public'})
        ignore_dirs {list} -- Directories to ignore. (default: {['img/photos']})
        bucket_name {str} -- Name of the bucket. (default: {'ps-george.com'})
    """

    print('Uploading to bucket: {}'.format(bucket_name))
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
            upload_file(relative_path, s3_path, bucket_name, content_type, content_disposition, acl) 
    return


def get_s3_files(bucket_name=None, bucket_region=None, delimiter='', prefix=''):
    return get_bucket(bucket_name, bucket_region).objects.filter(Delimiter=delimiter, Prefix=prefix)


def delete_s3_file(bucket_name=None, bucket_region=None, delimiter='', prefix=''):
    s3_file = get_s3_files(bucket_name, bucket_region, delimeter, prefix)
    print('Deleting {}'.format(s3_file.key))
    s3_file.delete()

    

def delete_s3_files(bucket_name=None, bucket_region=None, delimiter='', prefix='', mock=False):
    for s3_file in get_s3_files(bucket_name, bucket_region, delimiter, prefix):
        print('Deleting {}'.format(s3_file.key))
        if not mock:
            s3_file.delete()


def set_s3_acl(acl='', bucket_name=None, bucket_region=None, delimiter='', prefix=''):
    for s3_file in get_s3_files(bucket_name, bucket_region, delimiter, prefix):
        s3_file.Acl().put(ACL='public-read')
