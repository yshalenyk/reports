import pytest
import mock
import couchdb
import os.path
from copy import copy
from reports.config import Config
from reports.utilities import bids, invoices, tenders, refunds
from reports.utilities.bids import BidsUtility
from reports.tests.utils import(
    get_mock_parser,
    test_data,
    assert_csv,
    db,
    assertLen
)

test_bids_invalid = [
    [{
        "owner": "test",
        "status": "invalid",
        "date": "2016-03-17T13:32:25.774673+02:00",
        "id": "44931d9653034837baff087cfc2fb5ac",
    }],
    [{
        "status": "invalid",
        "owner": "test",
        "date": "2016-04-17T13:32:25.774673+02:00",
        "id": "44931d9653034837baff087cfc2fb5ac"
    }]
]

test_bids_valid = [
    [{
        "owner": "test",
        "status": "active",
        "date": "2016-04-17T13:32:25.774673+02:00",
        "id": "44931d9653034837baff087cfc2fb5ac",
    }],
    [{  
        "owner": "test",
        "status": "active",
        "date": "2016-05-05T13:32:25.774673+02:00",
        "id": "44931d9653034837baff087cfc2fb5ac",
    }],

    [{
        "status": "active",
        "owner": "test",
        "date": "2016-05-10T13:32:25.774673+02:00",
        "id": "f55962b1374b43ddb886821c0582bc7f"
    }]]

test_award_period = '2016-04-17T13:32:25.774673+02:00'

@pytest.fixture(scope='function')
def ut(request):
    mock_parse = get_mock_parser()
    with mock.patch('argparse.ArgumentParser.parse_args', mock_parse):
        utility = BidsUtility()
    return utility

def test_bids_view_invalid_date(db, ut):
    data = {
        "awardPeriod": {
            "startDate": test_award_period,
        },
        'owner': 'teser',
        "bids": test_bids_invalid[0],
    }
    assertLen(0, data, ut)

def test_bids_view_invalid_mode(db, ut):
    data = {
        'mode': 'test',
        "awardPeriod": {
            "startDate": test_award_period,
        },
        'owner': 'teser',
        "bids": test_bids_valid[0],
    }
    assertLen(0, data, ut)

def test_bids_view_invalid_status(db, ut):
    data = {
        "procurementMethod": "open",
        "awardPeriod": {
            "startDate": test_award_period,
        },
        'owner': 'teser',
        'bids': test_bids_invalid[1],
    }
    assertLen(0, data, ut)

def test_bids_view_invalid_method(db, ut):
    data = {
        "procurementMethod": "test",
        "awardPeriod": {
            "startDate": test_award_period,
        },
        'owner': 'teser',
        'bids': test_bids_valid[0],
    }
    assertLen(0, data, ut)

def test_bids_view_valid(db, ut):
    data = {
        "awardPeriod": {
            "startDate": test_award_period,
        },
        'owner': 'teser',
        'bids': test_bids_valid[0],
    }
    assertLen(1, data, ut)
    ut.get_response()
    ut.response = list(ut.response)
    response = list(ut.response)
    assert 1000 == response[0]['value']['value']
    assert "44931d9653034837baff087cfc2fb5ac"== response[0]['value']['bid']
    assert "0006651836f34bcda9a030c0bf3c0e6e"== response[0]['value']['tender']
    assert "UA-2016-11-12-000150"== response[0]['value']['tenderID']
    assert u"UAH"== response[0]['value']['currency']

def test_bids_view_period(db, ut):
    ut.owner = 'test'
    data = {
        "awardPeriod": {
            "startDate": test_award_period,
        },
        'owner': 'teser',
        'bids': test_bids_valid[0],
    }
    doc = copy(test_data)
    doc.update(data)
    ut.db.save(doc)
    data = {
        "_id": "10028cddd23540e5b6abb9efd2756d1d",
        "awardPeriod": {
            "startDate": "2016-11-09T15:00:00+02:00",
        },
        'owner': 'teser',
        'bids': test_bids_valid[1],

    }
    doc = copy(test_data)
    doc.update(data)
    ut.db.save(doc)
    data = {
        "_id": "00028aasd2isdfsde5b6abb9efd2756d1d",
        "awardPeriod": {
            "startDate": "2016-11-30T15:00:00+02:00",
        },
        'owner': 'teser',
        'bids': test_bids_valid[2],
    }
    doc = copy(test_data)
    doc.update(data)
    ut.db.save(doc)

    ut.start_date = ''
    ut.end_date = ''
    ut.get_response()
    assert 3 == len(list(ut.response))

    ut.start_date = "2016-11-10T15:00:00"
    ut.end_date = ''
    ut.get_response()
    assert 1 == len(list(ut.response))
    ut.start_date = "2016-12-01T15:00:00"
    ut.end_date = ''
    ut.get_response()
    assert 0 == len(list(ut.response))
    ut.start_date = "2016-11-01T15:00:00"
    ut.end_date = "2016-12-01T15:00:00"
    ut.get_response()
    assert 2 == len(list(ut.response))

def test_bids_view_with_lots(db, ut):
    data = {
        "enquiryPeriod": {
            "startDate": '2016-04-17T13:32:25.774673+02:00',
        },
        "awardPeriod": {
            "startDate": test_award_period,
        },

        "lots": [
            {
                "status": "active",
                "id": "324d7b2dd7a54df29bad6d0b7c91b2e9",
                "value": {
                    "currency": "UAH",
                    "amount": 2000,
                    "valueAddedTaxIncluded": False,
                },
            }
        ],
        "bids": [
            {
                "date": "2016-04-07T16:36:58.983102+03:00",
                "owner": "test",
                "status": "active",
                "id": "a22ef2b1374b43ddb886821c0582bc7dk",
                "lotValues": [
                    {
                        "relatedLot": "324d7b2dd7a54df29bad6d0b7c91b2e9",
                        "date": "2016-04-07T16:36:58.983062+03:00",
                    }
                ],
            }
        ],
    }
    assertLen(1, data, ut)

def test_bids_utility_output(db, ut):
    data = {
        'awardPeriod': {'startDate': test_award_period },
        'bids': test_bids_valid[0],
        "enquiryPeriod": {
            "startDate": '2016-04-17T13:32:25.774673+02:00',
        }
    }
    
    mock_csv = mock.mock_open()
    doc = copy(test_data)
    doc.update(data)
    ut.db.save(doc)
    with mock.patch('__builtin__.open', mock_csv):    
        ut.run()
        row = [['0006651836f34bcda9a030c0bf3c0e6e,UA-2016-11-12-000150,,1000,UAH,44931d9653034837baff087cfc2fb5ac,,7.0'],]
        assert_csv(mock_csv, 'test/test@---bids.csv', ut.headers, row)
        

def test_bids_utility_output_with_lots(db, ut):
    data = {
        "enquiryPeriod": {
            "startDate": '2016-04-17T13:32:25.774673+02:00',
        },
        "awardPeriod": {
            "startDate": test_award_period,
        },

        "lots": [
            {
                "status": "active",
                "id": "324d7b2dd7a54df29bad6d0b7c91b2e9",
                "value": {
                    "currency": "UAH",
                    "amount": 2000,
                    "valueAddedTaxIncluded": False,
                },
            }
        ],
        "bids": [
            {
                "date": "2016-04-07T16:36:58.983102+03:00",
                "status": "active",

                "owner": "test",
                "id": "a22ef2b1374b43ddb886821c0582bc7dk",
                "lotValues": [
                    {
                        "relatedLot": "324d7b2dd7a54df29bad6d0b7c91b2e9",
                        "date": "2016-04-07T16:36:58.983062+03:00",
                    }
                ],
            }
        ],
    }
    mock_csv = mock.mock_open()
    doc = copy(test_data)
    doc.update(data)
    ut.db.save(doc)       
    with mock.patch('__builtin__.open', mock_csv):
        ut.run()
        row = [["0006651836f34bcda9a030c0bf3c0e6e,UA-2016-11-12-000150,324d7b2dd7a54df29bad6d0b7c91b2e9,2000,UAH,a22ef2b1374b43ddb886821c0582bc7dk,,7.0"],]
        assert_csv(mock_csv, 'test/test@---bids.csv', ut.headers, row)
        
