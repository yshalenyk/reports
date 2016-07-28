import boto3
import argparse
import os.path
import logging
import os
import re
from jinja2 import Environment, PackageLoader
from gevent.pool import Pool
from botocore.exceptions import ClientError
from logging.config import fileConfig
from ConfigParser import ConfigParser


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

    def __init__(self, config_file):
        fileConfig(config_file)
        config = ConfigParser()
        config.read(config_file)
        try:
            session = boto3.Session()
        except ClientError as e:
            print "Error: {}".format(e)
        self.Logger = logging.getLogger('AWS')
        self.bucket = config.get('aws', 'bucket')
        self.expires = config.get('aws', 'expires')
        self.emails = {item[0]: item[1].split(',')
                       for item in config.items('emails')}
        self.s3 = session.client('s3')
        self.ses = session.client('ses')
        self.links = []
        self.template_env = Environment(
                loader=PackageLoader('reports', 'templates'))

    def _render_email(self, context):
        template = self.template_env.get_template('email.html')
        return template.render(context)

    def send_file(self, file):
        entry['broker'] = file.split('@')[0]
        key = os.path.basename(file)
        entry['period'] = '--'.join(re.findall(r'\d{4}-\d{2}-\d{2}', file))
        try:
            self.s3.upload_file(
                    file,
                    self.bucket,
                    key)
            entry['link'] = self.s3.generate_presigned_url(
                'get_object',
                Params={'Bucket': self.bucket, 'Key': key},
                ExpiresIn=self.expires,
            )
            print "Url for {} ==> {}\n".format(entr['broker'], entry['link'])
            self.links.append(entry)
        except ClientError as e:
            print "Error during uploading file {}. Error {}".format(file, e)

    def send_email(self, context):
        try:
            self.ses.send_email(
                Source=self.emails['from'],
                Destination={
                    'ToAdresses': [
                        self.emails[context[broker]],
                    ]
                },
                Message={
                    'Subject': {
                        'Data': "Openprocurement Billing",
                        "Charset": "UTF-8",
                    },
                    "Body": {
                        "Html": {
                            "Data": self._render_email(context),
                            "Charset": "UTF-8"

                        }
                    }
                }
            )
            print "Successfully sent message to {}".format(context['broker'])
        except KeyError as e:
            print "No email for broker {}".format(context['broker'])
        except ClientError as e:
            print "Fail during sening message. Error: {}".format(e)


def run():
    parser = get_parser()
    args = parser.parse_args()

    client = AWSClient(args.config)
    pool = Pool(10)
    pool.map(client.send_file, args.files)
    if args.notify:
        pool.map(client.send_email, client.links)

if __name__ == '__main__':
    run()
