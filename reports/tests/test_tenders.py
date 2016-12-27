import pytest
import couchdb
import mock
import os.path
from reports.config import Config
from reports.utilities.tenders import TendersUtility
from copy import copy
from reports.tests.utils import(
    get_mock_parser,
    test_data,
    assert_csv,
    db,
    assertLen
)
test_award_period = '2016-04-17T13:32:25.774673+02:00'

@pytest.fixture(scope='function')
def ut(request):    
    mock_parse = get_mock_parser()
    type(mock_parse.return_value).kind = mock.PropertyMock(
        return_value=['general'])
    with mock.patch('argparse.ArgumentParser.parse_args', mock_parse):
        utility = TendersUtility()
    return utility

def test_tenders_view_invalid_date(db, ut):
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
    assertLen(0, data, ut)

def test_tenders_view_invalid_method(db, ut):
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
    assertLen(0, data, ut)

def test_tenders_view_invalid_mode(db, ut):
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
    assertLen(0, data, ut)

def test_tenders_view_invalid_status(db, ut):
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
    assertLen(0, data, ut)

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
    assertLen(1, data, ut)
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
        row = [['0006651836f34bcda9a030c0bf3c0e6e,UA-2016-11-12-000150,,complete,,UAH,general,1000,,5.0'],]
        assert_csv(mock_csv, 'test/test@---tenders.csv', ut.headers, row)
        