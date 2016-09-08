import boto3
import argparse
import os.path
import logging
import os
import subprocess
import smtplib
import re
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from jinja2 import Environment, PackageLoader
from botocore.exceptions import ClientError
from logging.config import fileConfig
from ConfigParser import ConfigParser
from reports.helpers import get_operations

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
        self.Logger = logging.getLogger('AWS')
        self.bucket = self.config.get('aws', 'bucket')
        self.expires = self.config.get('aws', 'expires')
        self.s3_cred_path = self.config.get('aws', 's3_pass_path')
        self.ses_cred_path = self.config.get('aws', 'ses_pass_path')
        self.smtp_server = self.config.get('email', 'smtp_server')
        self.smtp_port = self.config.get('email', 'smtp_port')
        self.verified_email = self.config.get('email', 'verified_email')
        self.subject = self.config.get('email', 'subject')
        self.emails_to = dict((key, field.split(',')) for key, field in self.config.items('brokers_emails'))
        self.template_env = Environment(
                loader=PackageLoader('reports', 'templates'))
        self.links = []

    def _update_credentials(self, path):
        cmd = "pass {}".format(path)
        cred = dict(item.split('=') for item in
                    subprocess.check_output(cmd, shell=True).split('\n')
                    if item)
        return cred

    def _render_email(self, context):
        template = self.template_env.get_template('email.html')
        return template.render(context)

    def send_files(self, files):
        cred = self._update_credentials(self.s3_cred_path)

        s3 = boto3.client(
            's3',
            aws_access_key_id=cred.get('AWS_ACCESS_KEY_ID'),
            aws_secret_access_key=cred.get('AWS_SECRET_ACCESS_KEY'),
            region_name=cred.get('AWS_DEFAULT_REGION')
        )

        for f in files:
            entry = {}
            key = os.path.basename(f)
            broker = key.split('@')[0]
            entry['period'] = '--'.join(re.findall(r'\d{4}-\d{2}-\d{2}', key))
            entry['broker'] = broker
            operations = get_operations(key)
            entry['encrypted'] = 'bids' in operations
            if len(operations) == 2:
                entry['type'] = ' and '.join(operations)
            else:
                entry['type'] = ', '.join(operations)
            try:
                s3.upload_file(
                    f,
                    self.bucket,
                    key)
                entry['link'] = s3.generate_presigned_url(
                    'get_object',
                    Params={'Bucket': self.bucket, 'Key': key},
                    ExpiresIn=self.expires,
                )
                self.links.append(entry)
            except ClientError as e:
                print "Error during uploading file {}. Error {}".format(f, e)

    def send_emails(self):
        cred = self._update_credentials(self.ses_cred_path)
        user = cred.get('AWS_ACCESS_KEY_ID')
        password = cred.get('AWS_SECRET_ACCESS_KEY')
        smtpserver = smtplib.SMTP(self.smtp_server, self.smtp_port)

        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo()
        smtpserver.login(user, password)

        try:
            for context in self.links:
                recipients = self.emails_to[context['broker']]
                msg = MIMEText(self._render_email(context), 'html', 'utf-8')
                msg['Subject'] = 'Prozorro Billing: all {} ({})'.format(context['type'], context['period'])
                msg['From'] = self.verified_email
                msg['To'] = COMMASPACE.join(recipients)

                smtpserver.sendmail(self.verified_email, recipients,  msg.as_string())
        finally:
            smtpserver.close()


def run():
    parser = get_parser()
    args = parser.parse_args()

    client = AWSClient(args.config)
    client.send_files(args.files)
    for broker in client.links:
        print "Url for {} ==> {}\n".format(broker['broker'], broker['link'])
    if args.notify:
        client.send_emails()


if __name__ == '__main__':
    run()
