from reports.utilities.send import AWSClient
import os
import unittest
import mock
import boto3
from mock import Mock, MagicMock
from mock import patch
import errno
from socket import error
from .utils import test_config
from datetime import datetime
from email.mime.text import MIMEText
from email.utils import COMMASPACE

class TestAWSClient(unittest.TestCase):
    """Tests for `send.py`."""

    def setUp(self):
        self.aws_client = AWSClient(test_config)
        self.aws_client._update_credentials = MagicMock(return_value={'AWS_ACCESS_KEY_ID':'user', 'AWS_SECRET_ACCESS_KEY': 'pass'})

    def test_get_entry(self):
        """Check correct result"""

        # if file_name correct
        file_name = 'broker1@2016-09-01--2016-10-01-bids-invoices.zip'

        result = self.aws_client.get_entry(file_name)
        self.assertEqual(result, 
            {'encrypted': True, 'type': 'bids and invoices',
             'period': '2016-09-01--2016-10-01', 'broker': 'broker1'})

        # check only one value
        file_name = 'test@2016-09-01--2016-10-01-bids.zip'
        result = self.aws_client.get_entry(file_name)
        self.assertEqual(result['type'], 'bids')
        # check encryption if no type bids
        file_name = 'test@2016-09-01--2016-10-01-invoices.zip'
        result = self.aws_client.get_entry(file_name)
        self.assertEqual(result['encrypted'], False)

        # check all available values
        file_name = 'test@2016-09-01--2016-10-01-bids-invoices-tenders-refunds.zip'
        result = self.aws_client.get_entry(file_name)
        self.assertEqual(result['type'], 'bids, invoices, tenders, refunds')

    def test_update_credentials(self):
        path = 'billing/s3/sandbox'
        with mock.patch('subprocess.check_output', return_value='aws_access_key_id=user\naws_secret_access_key=pass' ):
            result = self.aws_client._update_credentials(path)
            self.assertEqual(result['AWS_ACCESS_KEY_ID'], 'user')
            self.assertEqual(result['AWS_SECRET_ACCESS_KEY'], 'pass')

    def test_render_email_with_encrypt(self):
        context = {'link': 'test_url', 'encrypted': True, 'type': 'bids and invoices', 'period': '2016-09-01--2016-10-01', 'broker': 'broker1'}
        result = self.aws_client._render_email(context)
        self.assertIn('test_url', result)
        self.assertIn("Zip archive is encryped by password you've received earlier. Please use this password to decrypt the file.",result)
        self.assertIn('bids and invoices', result)
        self.assertIn('2016-09-01--2016-10-01', result)
        self.assertIn('broker1', result)

    def test_render_email_without_encrypt(self):
        context = {'link': 'test_url', 'encrypted': False, 'type': 'bids and invoices', 'period': '2016-09-01--2016-10-01', 'broker': 'broker1'}
        result = self.aws_client._render_email(context)
        self.assertIn('test_url', result)        
        self.assertNotIn("Zip archive is encryped by password you've received earlier. Please use this password to decrypt the file.",result)
        self.assertIn('bids and invoices', result)
        self.assertIn('2016-09-01--2016-10-01', result)
        self.assertIn('broker1',result)

    def test_send_files_exception(self):
        # exception test
        files = []        
        m = Mock()         
        with mock.patch('reports.utilities.send.boto3.client', m):              
            result = self.aws_client.send_files(files)
            with self.assertRaises(Exception) as e:
                print "Error during uploading file {}. Error {}".format(files[0], e)

    def test_send_files_withTS(self):
        # when timestamp is set
        files = ['broker1@2016-09-01--2016-10-01-bids-invoices.zip']
        timestamp = '2016-11-21/13-07-39-406832'        
        key = '/'.join([timestamp, 'broker1@2016-09-01--2016-10-01-bids-invoices.zip'])        
                       
        with mock.patch('reports.utilities.send.boto3.client') as s:
            self.aws_client.send_files(files, timestamp)
            s.return_value.upload_file.assert_called_with('broker1@2016-09-01--2016-10-01-bids-invoices.zip', self.aws_client.bucket, key)
            s.return_value.generate_presigned_url.assert_called_with('get_object', ExpiresIn='1209600', Params={'Bucket': 'some-name', 'Key': '2016-11-21/13-07-39-406832/broker1@2016-09-01--2016-10-01-bids-invoices.zip'})

    @mock.patch('reports.utilities.send.datetime')
    def test_send_files_withoutTS(self,mock_datatime):
        # when timestamp isn`t set
        files = ['broker1@2016-09-01--2016-10-01-bids-invoices.zip']
        mock_datatime.now.return_value = datetime(year=2011, month=11, day=11, hour=11, minute=11, second=11, microsecond=11) 
        key = '/'.join(['2011-11-11/11-11-11-000011', 'broker1@2016-09-01--2016-10-01-bids-invoices.zip'])     
        with mock.patch('reports.utilities.send.boto3.client') as s:
            
            self.aws_client.send_files(files)
            s.return_value.upload_file.assert_called_with('broker1@2016-09-01--2016-10-01-bids-invoices.zip', self.aws_client.bucket, key)
            s.return_value.generate_presigned_url.assert_called_with('get_object', ExpiresIn='1209600', Params={'Bucket': 'some-name', 'Key': '2011-11-11/11-11-11-000011/broker1@2016-09-01--2016-10-01-bids-invoices.zip'})
    
    def test_send_test_emails(self):
        # if email present
        file_name = 'broker1@2016-09-01--2016-10-01-bids-invoices.zip'
        email = ['test1@test.com', 'test2@test.com']

        entry = self.aws_client.get_entry(file_name)
        entry['link'] = 'test_url'
        self.aws_client.links.append(entry)

        msg = MIMEText(self.aws_client._render_email(entry), 'html', 'utf-8')
        msg['Subject'] = 'Prozorro Billing: {} {} ({})'.format('broker1', 'bids and invoices', '2016-09-01--2016-10-01')
        msg['From'] = 'test@test.com'
        msg['To'] = COMMASPACE.join(email)

        with mock.patch('smtplib.SMTP') as s:           
            server = s.return_value
            self.aws_client.send_emails(email)
            server.sendmail.assert_called_with('test@test.com', email, msg.as_string())
        
    def test_send_real_emails(self):
        # if email isn`t present
        file_name = 'broker1@2016-09-01--2016-10-01-bids-invoices.zip'

        entry = self.aws_client.get_entry(file_name)
        entry['link'] = 'test_url'
        self.aws_client.links.append(entry)

        msg = MIMEText(self.aws_client._render_email(entry), 'html', 'utf-8')
        msg['Subject'] = 'Prozorro Billing: {} {} ({})'.format('broker1', 'bids and invoices', '2016-09-01--2016-10-01')
        msg['From'] = 'test@test.com'
        msg['To'] = COMMASPACE.join(['mail1@test.com', 'mail2@test.com'])

        with mock.patch('smtplib.SMTP') as s:           
            server = s.return_value
            self.aws_client.send_emails()
            server.sendmail.assert_called_with('test@test.com', ['mail1@test.com', 'mail2@test.com'], msg.as_string())
    
    def test_send_from_timestamp(self):
        timestamp = '2016-09-13/13-59-56-779740'
        file_name = '2016-09-13/13-59-56-779740/broker1@2016-09-01--2016-10-01-bids-invoices.zip'
        m = Mock()
        m.list_objects.return_value  = {'Contents': [ {'Key': '2016-09-13/13-59-56-779740/broker1@2016-09-01--2016-10-01-bids-invoices.zip' }  ], 'Prefix': '2016-09-13/13-59-56-779740',  'EncodingType': 'url'}
        s3 = MagicMock()
        s3.return_value = m            
       
        with mock.patch('reports.utilities.send.boto3.client', s3):
            entry = self.aws_client.get_entry(os.path.basename('2016-09-13/13-59-56-779740/broker1@2016-09-01--2016-10-01-bids-invoices.zip'))
            self.aws_client.send_from_timestamp(timestamp)
            self.assertEqual(entry, {'encrypted': True, 'type': 'bids and invoices', 'period': '2016-09-01--2016-10-01', 'broker': 'broker1'})
            self.assertEqual(self.aws_client.links[0]['broker'], 'broker1')
            res_dict = self.aws_client.links[-1]
            link = res_dict.get('link')
            self.assertNotEqual(link, None)
            m.generate_presigned_url.assert_called_with('get_object', ExpiresIn='1209600', Params={'Bucket': 'some-name', 'Key': '2016-09-13/13-59-56-779740/broker1@2016-09-01--2016-10-01-bids-invoices.zip'})
