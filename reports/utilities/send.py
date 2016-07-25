import boto3
import argparse
import os.path
import logging
import os
from gevent.pool import Pool
from botocore.exceptions import ClientError
from logging.config import fileConfig
from ConfigParser import ConfigParser

Logger = None


def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c',
        '--config',
        dest='config',
        required=True,
        help='Path to configuration file'
    )
    parser.add_argument(
        '-f',
        '--file',
        nargs='+',
        required=True,
        dest='files',
        help='Files to send'
    )
    parser.add_argument(
        '-n',
        '--notify',
        action='store_true',
        help='Notification flag'
    )
    return parser


class AWSClient(object):

    def __init__(self, config):
        fileConfig(config)
        self.config = ConfigParser()
        self.config.read(config)
        try:
            self.session = boto3.Session()
        except ClientError as e:
            print "Errori {}".format(e)
        self.Logger = logging.getLogger('AWS')
        self.bucket = self.config.get('aws', 'bucket')
        self.expires = self.config.get('aws', 'expires')
        self.s3 = self.session.client('s3')
        self.links = {}

    def send_file(self, file):
        broker = file.split('@')[0]
        key = os.path.basename(file)
        try:
            self.s3.upload_file(
                    file,
                    self.bucket,
                    key)
            self.links[broker] = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=self.expires,
            )
        except ClientError as e:
            print "Error during uploading file {}. Error {}".format(file, e)


def run():
    parser = get_parser()
    args = parser.parse_args()

    client = AWSClient(args.config)
    pool = Pool(10)
    pool.map(client.send_file, args.files)
    for key, link in client.links.iteritems():
        print "Url for {} ==>{}\n".format(key, link)


if __name__ == '__main__':
    run()
