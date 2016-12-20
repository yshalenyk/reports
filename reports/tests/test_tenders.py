import pytest
import couchdb
import mock
import os.path
from reports.config import Config
from reports.utilities.tenders import TendersUtility
from copy import copy
from reports.tests.utils import(
    get_mock_parser,
    test_data
)
test_award_period = '2016-04-17T13:32:25.774673+02:00'

test_config = os.path.join(os.path.dirname(__file__), 'tests.ini')

@pytest.fixture(scope='function')
def db(request): 
    conf = Config(test_config)
    host = conf.get_option('db', 'host')
    port = conf.get_option('db', 'port')
    user = conf.get_option('user', 'username')
    passwd = conf.get_option('user', 'password')

    db_name = conf.get_option('db', 'name')
    def create_db_url(host, port, user, passwd):
        up = ''
        if user and passwd:
            up = '{}:{}@'.format(user, passwd)
        url = 'http://{}{}:{}'.format(up, host, port)
        return url
    server = couchdb.Server(
        create_db_url(host, port, user, passwd)
    )  
    if db_name not in server:
        server.create(db_name)
    def delete():
        server.delete(db_name)
    request.addfinalizer(delete)

@pytest.fixture(scope='function')
def ut(request):    
    mock_parse = get_mock_parser()
    type(mock_parse.return_value).kind = mock.PropertyMock(
        return_value=['general'])
    with mock.patch('argparse.ArgumentParser.parse_args', mock_parse):
        utility = TendersUtility()
    return utility

def assertLen(count, data):
    mock_parse = get_mock_parser()
    type(mock_parse.return_value).kind = mock.PropertyMock(
        return_value=['general'])
    with mock.patch('argparse.ArgumentParser.parse_args', mock_parse):
        utility = TendersUtility()
    doc = copy(test_data)
    doc.update(data)
    utility.db.save(doc)
    utility.get_response()
    utility.response = list(utility.response)
    assert count == len(utility.response)

def test_tenders_view_invalid_date(db):
    data = {
        "enquiryPeriod": {
            "startDate": '2016-03-17T13:32:25.774673+02:00',
        },
        'owner': 'test',
        "procurementMethod": "open",
        "contracts": [
            {
                "status": "active",
            }],
    }
    assertLen(0, data)

def test_tenders_view_invalid_method(db):
    data = {
        "procurementMethod": "test",
        "enquiryPeriod": {
            "startDate": '2016-04-17T13:32:25.774673+02:00',
        },
        'owner': 'test',
        "contracts": [
            {
                "status": "active",
            }],
    }
    assertLen(0, data)

def test_tenders_view_invalid_mode(db):
    data = {
        "mode": "test",
        "procurementMethod": "open",
        "enquiryPeriod": {
            "startDate": '2016-04-17T13:32:25.774673+02:00',
        },
        'owner': 'test',
        "contracts": [
            {
                "status": "active",
            }],
    }
    assertLen(0, data)

def test_tenders_view_invalid_status(db):
    data = {
        "procurementMethod": "open",
        "enquiryPeriod": {
            "startDate": '2016-04-17T13:32:25.774673+02:00',
        },
        'awardPeriod': {'startDate': '2016-04-22T13:32:25.774673+02:00'},
        "contracts": [{
            "status": "unsuccessful",
        }],
    }
    assertLen(0, data)

def test_tenders_view_valid(db, ut):
    data = {
        "owner": "test",
        "status": "complete",
        "date": '2016-04-22T13:32:25.774673+02:00',
        "procurementMethod": "open",
        'numberOfBids': 2,
        'awardPeriod': {'startDate': '2016-04-22T13:32:25.774673+02:00'},
        "enquiryPeriod": {
            "startDate": '2016-04-17T13:32:25.774673+02:00',
        },
        "contracts": [
            {
                "status": "active",
                "date": '2016-04-22T13:32:25.774673+02:00',
                "dateSigned": '2016-05-22T13:32:25.774673+02:00',
                "documents": [{
                    'datePublished': "2016-06-22T13:32:25.774673+02:00",
                }]
            }
        ],
    }
    assertLen(1, data)
    ut.get_response()
    ut.response = list(ut.response)
    response = list(ut.response)
    assert u"2016-04-22T11:32:25.774" == response[0]['key'][1]




def test_tenders_utility_output(db, ut):
    data = {
        "owner": "test",
        "status": "complete",
        "date": '2016-04-22T13:32:25.774673+02:00',
        "procurementMethod": "open",
        'numberOfBids': 2,
        'awardPeriod': {'startDate': '2016-04-22T13:32:25.774673+02:00'},
        "enquiryPeriod": {
            "startDate": '2016-04-17T13:32:25.774673+02:00',
        },
        "contracts": [
            {
                "status": "active",
                "date": '2016-04-22T13:32:25.774673+02:00',
                "dateSigned": '2016-05-22T13:32:25.774673+02:00',
                "documents": [{
                    'datePublished': "2016-06-22T13:32:25.774673+02:00",
                }]
            }
        ],
    }
    mock_csv = mock.mock_open()
    doc = copy(test_data)
    doc.update(data)
    ut.db.save(doc)
    with mock.patch('__builtin__.open', mock_csv):
        ut.run()
        calls = [
            mock.call('test/test@---tenders.csv', 'w'),
            mock.call().__enter__(),
            mock.call().write(','.join(ut.headers) + '\r\n'),
            mock.call().write(
                '0006651836f34bcda9a030c0bf3c0e6e,'
                'UA-2016-11-12-000150,,complete,,UAH,general,1000,,5.0\r\n'
            ),
            mock.call().__exit__(None, None, None),
        ]
        mock_csv.assert_has_calls(calls)


