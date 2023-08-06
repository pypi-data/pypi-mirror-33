# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2004-today OpenERP SA (<http://www.openerp.com>)
#    Copyright (C) 2011-today Synconics Technologies Pvt. Ltd. (<http://www.synconics.com>)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from openerp.osv import osv, fields
from openerp.tools import config
from boto3.session import Session
from botocore.exceptions import ClientError
from boto3.exceptions import S3UploadFailedError
import re
import os
import logging

_BUCKET_REGEX = re.compile(r'^[0-9a-zA-Z.]*$')
_MIN_FILE_SIZE = 10  # Minimum file size in Bytes.
_logger = logging.getLogger(__name__)


class AmazonS3(osv.osv_memory):
    """ Amazon S3 Connection and tools. """

    _name = "bboxx.common.amazon.s3"
    _description = "Amazon S3 Connection and tools"

    """
      _____       _                        _      __                  _   _                 
     |_   _|     | |                      | |    / _|                | | (_)                
       | |  _ __ | |_ ___ _ __ _ __   __ _| |   | |_ _   _ _ __   ___| |_ _  ___  _ __  ___ 
       | | | '_ \| __/ _ \ '__| '_ \ / _` | |   |  _| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
      _| |_| | | | ||  __/ |  | | | | (_| | |   | | | |_| | | | | (__| |_| | (_) | | | \__ \
     |_____|_| |_|\__\___|_|  |_| |_|\__,_|_|   |_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|___/

    """

    def __get_client(self, client_type='resource', region_name='eu-west-1'):
        """ Function to get the s3 resource or client object that connects to S3. """
        exceptions = self.pool['bboxx.common.exceptions']

        # Get credentials.
        aws_access_key_id = config.get('aws_access_key_id', False)
        aws_secret_access_key = config.get('aws_secret_access_key', False)

        # Validate credentials.
        if not aws_access_key_id or not aws_secret_access_key:
            msg = 'Unable to establish a connection with S3.'
            field_errors = {}

            if not aws_access_key_id:
                field_errors['aws_access_key_id'] = 'Not provided.'

            if not aws_secret_access_key:
                field_errors['aws_secret_access_key'] = 'Not provided.'

            raise exceptions.BboxxValidationError(msg, 'AWSS3-CRED-01', field_errors=field_errors)

        # Get session to connect to Amazon S3.
        session = Session(aws_access_key_id=aws_access_key_id,
                          aws_secret_access_key=aws_secret_access_key,
                          region_name=region_name)

        if client_type == 'resource':
            return session.resource("s3")
        # Assuming the other value that is 'client'.
        else:
            return session.client("s3")

    def __create_bucket(self, bucket_name, region_name='eu-west-1'):
        """ Function that creates a bucket. """
        exceptions = self.pool['bboxx.common.exceptions']

        # Add 'test_' at the beginning of the bucket name in case it is not production to not overwrite data.
        if not self.pool['bboxx.utils'].production_instance() and not bucket_name.startswith('test.'):
            bucket_name = "test.%s" % bucket_name

        # Validate bucket name.
        if not _BUCKET_REGEX.match(bucket_name):
            msg = 'The name of the bucket is not valid. Only numbers, letters and points admitted.'
            field_errors = {'bucket_name': 'Not valid format.'}
            raise exceptions.BboxxValidationError(msg, 'AWSS3-CB-01', field_errors=field_errors)

        # If the bucket already exists, will be skipped internally by the 'boto3' library.
        s3 = self.__get_client(region_name=region_name)
        return s3.create_bucket(Bucket=bucket_name, CreateBucketConfiguration={'LocationConstraint': region_name})

    def __get_bucket(self, bucket_name, create=True):
        """ Function that returns the bucket name with 'test.' at the beginning if necessary.
        If does not exists create a new one."""
        s3 = self.__get_client()

        if not self.pool['bboxx.utils'].production_instance() and not bucket_name.startswith('test.'):
            bucket_name = 'test.%s' % bucket_name

        if not s3.Bucket(bucket_name) in s3.buckets.all():
            if create:
                self.__create_bucket(bucket_name)
            else:
                exceptions = self.pool['bboxx.common.exceptions']
                msg = 'The selected bucket does not exists.'
                raise exceptions.BboxxValidationError(msg, 'AWSS3-GB-01')

        return bucket_name

    def __get_all_buckets(self):
        """ Function to list all available buckets. """
        s3 = self.__get_client()

        return [bucket.name for bucket in s3.buckets.all()]

    def __get_bucket_folders(self, bucket_name, path=''):
        """ Function to get the folders . """
        s3 = self.__get_client(client_type='client')
        folders = []

        try:
            for folder in s3.list_objects(Bucket=bucket_name, Prefix=path, Delimiter="/")['CommonPrefixes']:
                folders.append(folder['Prefix'])
        except s3.exceptions.NoSuchBucket:
            _logger.debug("Bucket '%s' does not exists." % bucket_name)

        return folders

    def __get_bucket_objects(self, bucket_name, path=None):
        """ Function to list all objects for bucket 'bucket_name' in path 'path' or all if none. """
        s3 = self.__get_client()

        if path:
            bucket_objects = [obj for obj in s3.Bucket(bucket_name).objects.filter(Prefix=path)]
        else:
            bucket_objects = [obj for obj in s3.Bucket(bucket_name).objects.all()]

        return bucket_objects

    def __check_file(self, bucket_name, s3_file_path, file_name):
        """ Function to verify that a file exists and is correct on S3. """
        # Check that the file was uploaded to S3.
        _file = self.__get_bucket_objects(bucket_name, path=s3_file_path)

        if not _file:
            raise IOError("File '%s' not found." % file_name)

        if _file[0].size < _MIN_FILE_SIZE:
            pretty_size = "%s Bytes" % _file[0].size
            pretty_min = "%s Bytes" % _MIN_FILE_SIZE
            raise ValueError("The file size '%s' is lower than the minimum size required '%s'" % (pretty_size,
                                                                                                  pretty_min))

    def __upload_file(self, bucket_name, file_name, s3_path, local_path=''):
        """ Function to upload a file to S3. """
        s3 = self.__get_client()
        bucket_name = self.__get_bucket(bucket_name)

        # Convert path into correct format.
        local_file = os.path.join(local_path, file_name)
        s3_file_path = os.path.join(s3_path, file_name)

        # Upload the file.
        s3.Bucket(bucket_name).upload_file(local_file, s3_file_path)

        # Validate uploaded file.
        self.__check_file(bucket_name, s3_file_path, file_name)

        return

    def __upload_data(self, bucket_name, file_name, s3_path, data):
        """ Function to upload data into a S3 file. """
        s3 = self.__get_client()
        bucket_name = self.__get_bucket(bucket_name)

        # Convert path into correct format.
        s3_file_path = os.path.join(s3_path, file_name)

        # Upload the data into file.
        s3.Bucket(bucket_name).put_object(Key=s3_file_path, Body=data)

        # Validate uploaded file.
        self.__check_file(bucket_name, s3_file_path, file_name)

        return

    def __download_file(self, bucket_name, file_name, s3_path, local_path=''):
        """ Function to download a S3 file into your local. """
        s3 = self.__get_client()

        # Convert path into correct format.
        s3_file_path = os.path.join(s3_path, file_name)
        local_file_path = os.path.join(local_path, file_name) if local_path else file_name

        # Validate the file exists before.
        self.__check_file(bucket_name, s3_file_path, file_name)

        # Download the file into your local.
        s3.Bucket(bucket_name).download_file(s3_file_path, local_file_path)

        return

    def __delete_file(self, bucket_name, file_name, s3_path):
        """ Function to delete a S3 file. """
        s3 = self.__get_client()

        # Convert path into correct format.
        s3_file_path = os.path.join(s3_path, file_name)

        # Validate the file exists before.
        self.__check_file(bucket_name, s3_file_path, file_name)

        # Delete the file.
        s3.Object(bucket_name, s3_file_path).delete()

        return

    def __move_file(self, old_bucket_name, new_bucket_name, old_file_name, new_file_name, old_s3_path, new_s3_path):
        """ Function to move an existing S3 file to another place. """
        s3 = self.__get_client()

        # Convert path into correct format.
        old_s3_file_path = os.path.join(old_s3_path, old_file_name)
        new_s3_file_path = os.path.join(new_s3_path, new_file_name)

        # Validate the file exists before.
        self.__check_file(old_bucket_name, old_s3_file_path, old_file_name)

        # Copy the file into the new place and delete the old one.
        copy_source = {'Bucket': old_bucket_name, 'Key': old_s3_file_path}
        s3.Object(new_bucket_name, new_s3_file_path).copy_from(CopySource=copy_source)
        s3.Object(old_bucket_name, old_s3_file_path).delete()

        return

    """
       _____      _ _       _     _           __                  _   _                 
      / ____|    | | |     | |   | |         / _|                | | (_)                
     | |     __ _| | | __ _| |__ | | ___    | |_ _   _ _ __   ___| |_ _  ___  _ __  ___ 
     | |    / _` | | |/ _` | '_ \| |/ _ \   |  _| | | | '_ \ / __| __| |/ _ \| '_ \/ __|
     | |___| (_| | | | (_| | |_) | |  __/   | | | |_| | | | | (__| |_| | (_) | | | \__ \
      \_____\__,_|_|_|\__,_|_.__/|_|\___|   |_|  \__,_|_| |_|\___|\__|_|\___/|_| |_|___/

    """
    def _validate_bucket(self, bucket_name):
        """ Function to validate that OpenERP users only create/access the allowed buckets. """
        if not bucket_name.startswith('test.openerp') and not bucket_name.startswith('openerp'):
            msg = "Sorry, you are not allowed to access bucket '%s'. Only 'openerp' buckets are allowed" % bucket_name
            raise self.pool['bboxx.common.exceptions'].BboxxValidationError(msg, 'AWS-S3-VAL-01')

        return

    def get_all_buckets(self):
        """ Function to get all the openerp buckets. """
        exceptions = self.pool['bboxx.common.exceptions']

        try:
            bucket_list = self.__get_all_buckets()
        except ClientError as err:
            msg = 'Client Error while getting all the buckets: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWSS3-GAB-01')
        except (exceptions.BboxxInternalServerError, exceptions.BboxxValidationError):
            raise
        except Exception as err:
            msg = 'Unexpected error while getting all the buckets: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWSS3-GAB-02')

        return [x for x in bucket_list if x.startswith('openerp') or x.startswith('test.openerp')]

    def get_bucket_folders(self, bucket_name, path=''):
        """ Function to get the first level path that corresponds to the DB. """
        self._validate_bucket(bucket_name)

        return self.__get_bucket_folders(bucket_name, path=path)

    def get_bucket_objects(self, bucket_name, path=None):
        """ Function to list all objects of a bucket path (if none, all of them). """
        self._validate_bucket(bucket_name)

        try:
            return self.__get_bucket_objects(bucket_name, path=path)
        except Exception as err:
            raise self.pool['bboxx.common.exceptions'].BboxxValidationError(str(err), 'AWSS3-GBO-01')

    def upload_file(self, bucket_name, file_name, s3_path, local_path=''):
        """ Function to upload a file into S3. """
        self._validate_bucket(bucket_name)

        exceptions = self.pool['bboxx.common.exceptions']

        try:
            self.__upload_file(bucket_name, file_name, s3_path, local_path=local_path)

        # Expected error that could happen while uploading the file.
        except S3UploadFailedError as err:
            msg = 'Unable to upload the file: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWS-S3-UF01')

        # Expected error that could happen while verifying the file.
        except IOError as err:
            msg = 'Unable to upload the file: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWS-S3-UF02')

        # Expected error that could happen while verifying the file.
        except ValueError as err:
            msg = 'Unable to upload the file: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWS-S3-UF03')

        except Exception as err:
            msg = 'FATAL ERROR trying to upload file to S3, please contact admin: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWS-S3-UF04')

        return

    def upload_data(self, bucket_name, file_name, s3_path, data):
        """ Function to upload a file into S3. """
        self._validate_bucket(bucket_name)

        exceptions = self.pool['bboxx.common.exceptions']

        try:
            self.__upload_data(bucket_name, file_name, s3_path, data)

        # Expected error that could happen while uploading the file.
        except S3UploadFailedError as err:
            msg = 'Unable to upload the data into a file: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWS-S3-UD01')

        # Expected error that could happen while verifying the file.
        except IOError as err:
            msg = 'Unable to upload the data into a file: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWS-S3-UD02')

        # Expected error that could happen while verifying the file.
        except ValueError as err:
            msg = 'Unable to upload the data into a file: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWS-S3-UD03')

        except Exception as err:
            msg = 'FATAL ERROR trying to upload data into a S3 file, please contact admin: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWS-S3-UD04')
        return

    def download_file(self, bucket_name, file_name, s3_path, local_path=''):
        """ Function to upload a S3 file. """
        self._validate_bucket(bucket_name)

        exceptions = self.pool['bboxx.common.exceptions']

        try:
            self.__download_file(bucket_name, file_name, s3_path, local_path=local_path)

        # Expected error that could happen while uploading the file.
        except S3UploadFailedError as err:
            msg = 'Unable to download file: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWS-S3-DF01')

        # Expected error that could happen while verifying the file.
        except IOError as err:
            msg = 'Unable to download file: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWS-S3-DF02')

        # Expected error that could happen while verifying the file.
        except ValueError as err:
            msg = 'Unable to download file: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWS-S3-DF03')

        # Unexpected error.
        except Exception as err:
            msg = 'FATAL ERROR trying to download the file from S3, please contact admin: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWS-S3-DF04')
        return

    def delete_file(self, bucket_name, file_name, s3_path):
        """ Function to delete a S3 file. """
        self._validate_bucket(bucket_name)

        exceptions = self.pool['bboxx.common.exceptions']

        try:
            self.__delete_file(bucket_name, file_name, s3_path)

        # Expected error that could happen while verifying the file.
        except IOError as err:
            msg = 'Unable to delete file: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWS-S3-DELF01')

        # Expected error that could happen while verifying the file.
        except ValueError as err:
            msg = 'Unable to delete file: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWS-S3-DELF02')

        # Unexpected error.
        except Exception as err:
            msg = 'FATAL ERROR trying to delete the file from S3, please contact admin: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWS-S3-DELF03')

        return

    def rename_file(self, bucket_name, new_file_name, s3_path, old_file_name):
        """ Function to rename an existing S3 file in the same folder. """
        self._validate_bucket(bucket_name)

        exceptions = self.pool['bboxx.common.exceptions']

        try:
            self.__move_file(bucket_name, bucket_name, old_file_name, new_file_name, s3_path, s3_path)

        # Expected error that could happen while verifying the file.
        except IOError as err:
            msg = 'Unable to rename file: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWS-S3-RNMF01')

        # Expected error that could happen while verifying the file.
        except ValueError as err:
            msg = 'Unable to rename file: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWS-S3-RNMF02')

        # Unexpected error.
        except Exception as err:
            msg = 'FATAL ERROR trying to rename the file from S3, please contact admin: %s' % err
            raise exceptions.BboxxValidationError(msg, 'AWS-S3-RNMF03')

        return