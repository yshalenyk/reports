import boto3
import argparse
import os.path
import logging
import os
import subprocess
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE
from jinja2 import Environment, PackageLoader
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
        self.Logger = logging.getLogger('AWS')
        self.bucket = self.config.get('aws', 'bucket')
        self.expires = self.config.get('aws', 'expires')
        self.s3_cred_path = self.config.get('aws', 's3_pass_path')
        self.ses_cred_path = self.config.get('aws', 'ses_pass_path')
        self.smtp_server = self.config.get('email', 'smtp_server')
        self.smtp_port = self.config.get('email', 'smtp_port')
        self.verified_email = self.config.get('email', 'verified_email')
        self.emails_to = dict(
            (broker.strip(), email.strip().split(','))
            for item in [e for e in self.config.get('email', 'emails').split('\n') if e]
            for (broker, email) in [ item.split(':') ]
        )
        self.template_env = Environment(
                loader=PackageLoader('reports', 'templates'))
        self.links = []

    def _update_credentials(self, path):
        cmd = "pass {}".format(path)
        cred = dict(item.split('=') for item in
                    subprocess.check_output(cmd, shell=True).split('\n')
                    if item)
        os.environ.update(cred)

    def _render_email(self, context):
        template = self.template_env.get_template('email.html')
        return template.render(context)

    def send_files(self, files):
        self._update_credentials(self.s3_cred_path)
        s3 = boto3.client('s3')
        for f in files:
            entry = {}
            key = os.path.basename(f)
            broker = key.split('@')[0]
            entry['period'] = '--'.join(re.findall(r'\d{4}-\d{2}-\d{2}', key))
            entry['broker'] = broker
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
        self._update_credentials(self.ses_cred_path)
        user = os.environ.get('AWS_ACCESS_KEY_ID')
        password = os.environ.get('AWS_SECRED_KEY')

        smtpserver = smtplib.SMTP(self.smtp_server, self.smtp_port)

        smtpserver.ehlo()
        smtpserver.starttls()
        smtpserver.ehlo()

        smtpserver.login(user, password)
        try:
            for context in self.links:
                recipients = self.emails_to(context['broker']) 
                msg = MIMEMultipart('alternative')
                msg['Subject'] = 'Openprocurement Billing'
                msg['From'] = self.verified_email
                msg['To'] = COMMASPACE.join(recipients)
                msg.attach(MIMEText(self._render_email(context), 'html'))
                smtpserver.sendmail(self.verified_email, recipients, msg.as_string())
        finally:
            smtpserver.close()


def run():
    parser = get_parser()
    args = parser.parse_args()

    client = AWSClient(args.config)
    client.send_files(args.files)
    for key, link in client.links.iteritems():
        print "Url for {} ==> {}\n".format(key, link)
    if args.notify:
        client.send_emails()


if __name__ == '__main__':
    run()
