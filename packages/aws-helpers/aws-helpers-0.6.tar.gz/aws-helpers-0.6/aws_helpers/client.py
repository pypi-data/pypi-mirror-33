
#!/bin/python3

from boto3.session import Session
import json
import os


def load_access_keys(access_key_path):
    """Function passed by default by S3Client to get AWS access keys. Loads the keys *access_key_path* json file.
    
    File at *access_key_path* contains: {'access-key':'ABC', 'secret-access-key':'ABC'}

    Arguments:
        access_key_path {str} -- Path to a json file containing access keys.
    
    Returns:
        tuple (str) -- Tuple of access-key, secret-access-key from json file.
    """

    # Get AWS credentials
    with open(os.path.expanduser(access_key_path)) as f:
        creds = json.load(f)

    ACCESS_KEY=creds.get('access-key')
    SECRET_KEY=creds.get('secret-access-key')
    return (ACCESS_KEY, SECRET_KEY)


class Client():
    """Returns a Client object which has functions to aid interacting with boto3.session."""

    load_access_keys = lambda self: load_access_keys(access_key_path='~/.rootkey.json')
    region_name = None
    session = None

    def __init__(self, region_name, replacement_access_key_function = None):
        """Set properties of the S3Client.
        
        Arguments:
            region_name {str} -- AWS region name e.g. for EU (Ireland): eu-west-1
        
        Keyword Arguments:
            load_access_keys {function} -- A function which returns a tuple of str's (access-key, secret-access-key) (default: {lambda:load_access_keys(access_key_path='~/.rootkey.json')})
        """

        if replacement_access_key_function is not None:
            self.load_access_keys = replacement_access_key_function

        self.region_name = region_name
        self.__set_session()
    
    
    def __set_session(self):
        """Using *load_access_keys* function to load authentication keys to connect to aws region of the class.

        Set self.session to boto3.session object.

        
        Keyword Arguments:
            access_key_path {str} -- Path to access keys. (default: {'~/.rootkey.json'})
            region_name {str} -- AWS region name e.g. eu-west-1 (default: {''})
        
        """
        ACCESS_KEY, SECRET_KEY = self.load_access_keys()

        session = Session(
                aws_access_key_id=ACCESS_KEY,
                aws_secret_access_key=SECRET_KEY,
                region_name=self.region_name)
        self.session = session


    def get_session(self):
        """Get boto3.session of this Client."""
        return self.session


    def get_resource(self, resource_type):
        """Get AWS resource.
        
        Arguments:
            resource_type {str} -- AWS resource type.
        
        Returns:
            boto3.session.resource -- Returns resource object of specified type.
        """
        return self.session.resource(resource_type)