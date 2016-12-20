import pytest
import couchdb
import mock
import os.path
from reports.config import Config
from reports.utilities.refunds import RefundsUtility
from copy import copy
from reports.tests.utils import(
    get_mock_parser,
    test_data
)

test_bids = [
                    {
                        "date": "2016-04-07T16:36:58.983102+03:00",
                        "owner": "test",
                        "id": "a22ef2b1374b43ddb886821c0582bc7dk",
                        "lotValues": [
                            {
                                "relatedLot": "324d7b2dd7a54df29bad6d0b7c91b2e9",
                                "date": "2016-04-07T16:36:58.983062+03:00",
                            }
                        ],
                    }
                ]
test_lots = [
                    {
                        "status": "complete",
                        "id": "324d7b2dd7a54df29bad6d0b7c91b2e9",
                        "date": '2016-04-17T13:32:25.774673+02:00',
                        "value": {
                            "currency": "UAH",
                            "amount": 2000,
                            "valueAddedTaxIncluded": False,
                        },
                    }
                ]

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
    mock_parse = get_mock_parser()
    with mock.patch('argparse.ArgumentParser.parse_args', mock_parse):
        utility = RefundsUtility()
    ut.counter = [0 for _ in utility.config.payments]
    request.addfinalizer(delete)

@pytest.fixture(scope='function')
def ut(request):
    mock_parse = get_mock_parser()
    type(mock_parse.return_value).kind = mock.PropertyMock(
        return_value=['general'])
    with mock.patch('argparse.ArgumentParser.parse_args', mock_parse):
        utility = RefundsUtility()
    return utility

def test_refunds_utility_output(db, ut):
    data = { "awardPeriod": {
                "startDate": '2016-04-17T13:32:25.774673+02:00',
            },
            "lots": test_lots,
            "bids": test_bids,
    }
    mock_csv = mock.mock_open()
    doc = copy(test_data)
    doc.update(data)
    ut.db.save(doc)
    with mock.patch('__builtin__.open', mock_csv):
        ut.run()
        assert ut.counter == [1, 0, 0, 0, 0]
        calls = [
            mock.call('test/test@---refunds.csv', 'w'),
            mock.call().__enter__(),
            mock.call().write(
                str('{}{}'.format(','.join(ut.headers), '\r\n'))
            ),
            mock.call().write('{}{}'.format(','.join(
                [str(i) for i in ut.counter]), '\r\n')
            ),
            mock.call().write('{}{}'.format(','.join(
                [str(i) for i in ut.config.payments]), '\r\n')
            ),
            mock.call().write('{}{}'.format(','.join([
                str(c * p) for c, p in zip(
                    ut.counter, ut.config.payments
                )]), '\r\n')
            ),
            mock.call().__exit__(None, None, None),
        ]
        mock_csv.assert_has_calls(calls)

def test_refunds_utility_handler_check(db, ut):
    data = { "awardPeriod": {
                "startDate": '2016-04-17T13:32:25.774673+02:00',
            },
            "lots": test_lots,
            "bids": test_bids,
    }
    doc = copy(test_data)
    doc.update(data)
    ut.db.save(doc)
    doc = ut.db[doc['_id']]
    print doc
    doc['lots'][0]['value']= {'amount': 25000, 'currency': 'UAH'}
    ut.db.save(doc)

    mock_csv = mock.mock_open()
    with mock.patch('__builtin__.open', mock_csv):
        ut.run()
        assert ut.counter == [0, 1, 0, 0, 0]
        mock_csv.assert_called_once_with('test/test@---refunds.csv', 'w')
        handler = mock_csv()
        handler.write.assert_any_call('{}{}'.format(
            ','.join(ut.headers), '\r\n'
        ))
        handler.write.assert_any_call('{}{}'.format(
            ','.join([str(i) for i in ut.counter]), '\r\n'
        ))
        handler.write.assert_any_call('{}{}'.format(
            ','.join([str(c * p) for c, p in zip(
                ut.counter, ut.config.payments
            )]), '\r\n'
        ))

def test_refunds_utility_middle_handler_check(db, ut):
    data = { "awardPeriod": {
                "startDate": '2016-04-17T13:32:25.774673+02:00',
            },
            "lots": test_lots,
            "bids": test_bids,
    }
    doc = copy(test_data)
    doc.update(data)
    ut.db.save(doc)
    doc = ut.db[doc['_id']]
    doc['lots'][0]['value']= {'amount': 55000, 'currency': 'UAH'}
    ut.db.save(doc)

    mock_csv = mock.mock_open()
    with mock.patch('__builtin__.open', mock_csv):
        ut.run()
        assert ut.counter == [0, 0, 1, 0, 0]
        
        mock_csv.assert_called_once_with('test/test@---refunds.csv', 'w')
        handler = mock_csv()
        handler.write.assert_any_call('{}{}'.format(
            ','.join(ut.headers), '\r\n'
        ))
        handler.write.assert_any_call('{}{}'.format(
            ','.join([str(i) for i in ut.counter]), '\r\n'
        ))
        handler.write.assert_any_call('{}{}'.format(
            ','.join([str(c * p) for c, p in zip(
                ut.counter, ut.config.payments
            )]), '\r\n'
        ))

def test_refunds_utility_correct_handler_check(db, ut):
    data = { "awardPeriod": {
                "startDate": '2016-04-17T13:32:25.774673+02:00',
            },
            "lots": test_lots,
            "bids": test_bids,
    }
    doc = copy(test_data)
    doc.update(data)
    ut.db.save(doc)
    doc = ut.db[doc['_id']]
    doc['lots'][0]['value']= {'amount': 255000, 'currency': 'UAH'}
    ut.db.save(doc)

    mock_csv = mock.mock_open()
    with mock.patch('__builtin__.open', mock_csv):
        ut.run()
        assert ut.counter== [0, 0, 0, 1, 0]
        
        mock_csv.assert_called_once_with('test/test@---refunds.csv', 'w')
        handler = mock_csv()
        handler.write.assert_any_call('{}{}'.format(
            ','.join(ut.headers), '\r\n'
        ))
        handler.write.assert_any_call('{}{}'.format(
            ','.join([str(i) for i in ut.counter]), '\r\n'
        ))
        handler.write.assert_any_call('{}{}'.format(
            ','.join([str(c * p) for c, p in zip(
                ut.counter, ut.config.payments
            )]), '\r\n'
        ))

def test_refunds_utility_last_handler_check(db, ut):
    data = { "awardPeriod": {
                "startDate": '2016-04-17T13:32:25.774673+02:00',
            },
            "lots": test_lots,
            "bids": test_bids,
    }
    doc = copy(test_data)
    doc.update(data)
    ut.db.save(doc)
    doc = ut.db[doc['_id']]
    doc['lots'][0]['value']= {'amount': 1255000, 'currency': 'UAH'}
    ut.db.save(doc)

    mock_csv = mock.mock_open()
    with mock.patch('__builtin__.open', mock_csv):
        ut.run()
        assert ut.counter== [0, 0, 0, 0, 1]
        
        mock_csv.assert_called_once_with('test/test@---refunds.csv', 'w')
        handler = mock_csv()
        handler.write.assert_any_call('{}{}'.format(
            ','.join(ut.headers), '\r\n'
        ))
        handler.write.assert_any_call('{}{}'.format(
            ','.join([str(i) for i in ut.counter]), '\r\n'
        ))
        handler.write.assert_any_call('{}{}'.format(
            ','.join([str(c * p) for c, p in zip(
                ut.counter, ut.config.payments
            )]), '\r\n'
        ))
        del ut.db[doc['_id']]

def test_refunds_utility_all_handlers_check(db, ut):
    data = { 
            "awardPeriod": {
                "startDate": '2016-04-17T13:32:25.774673+02:00',
            },
            "lots": test_lots,
            "bids": test_bids,
    }
    doc = copy(test_data)
    doc.update(data)
    ut.db.save(doc)
    doc.update({'_id': 'sddsfsdd'})
    doc['lots'][0]['value']= {'amount': 25000, 'currency': 'UAH'}

    ut.db.save(doc)
    doc.update({'_id': 'sddsfsdf'})
    doc['lots'][0]['value']= {'amount': 55000, 'currency': 'UAH'}

    ut.db.save(doc)
    doc.update({'_id': 'sddsfsdfa'})
    doc['lots'][0]['value']= {'amount': 255000, 'currency': 'UAH'}

    ut.db.save(doc)
    doc.update({'_id': 'sddsfsdfb'})
    doc['lots'][0]['value']= {'amount': 1255000, 'currency': 'UAH'}

    ut.db.save(doc)
    mock_csv = mock.mock_open()
    ut.counter = [0 for _ in ut.config.payments]
    with mock.patch('__builtin__.open', mock_csv):
        ut.run()
        assert ut.counter == [1, 1, 1, 1, 1]
        
        mock_csv.assert_called_once_with('test/test@---refunds.csv', 'w')
        handler = mock_csv()
        handler.write.assert_any_call('{}{}'.format(
            ','.join(ut.headers), '\r\n'
        ))
        handler.write.assert_any_call('{}{}'.format(
            ','.join([str(i) for i in ut.counter]), '\r\n'
        ))
        handler.write.assert_any_call('{}{}'.format(
            ','.join([str(c * p) for c, p in zip(
                ut.counter, ut.config.payments)]
            ), '\r\n'
        ))
        del ut.db[doc['_id']]


 
