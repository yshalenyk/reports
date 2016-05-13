import unittest
import couchdb
import os
import os.path
from couchdb import Session
from ConfigParser import ConfigParser
from reports.config import create_db_url
from reports.core import ReportUtility
from copy import copy


test_config = os.path.join(os.path.dirname(__file__), 'tests.ini')
config = ConfigParser()
config.read(test_config)


test_data = {
        "procurementMethod": "open",
        "status": "complete",
        "owner": "",
        "_id": "0006651836f34bcda9a030c0bf3c0e6e",
        "tenderID": "UA-2016-11-12-000150",
        "dateModified": "2016-03-31T19:03:53.704712+03:00",
        "tenderPeriod": {
            "startDate": "2015-11-13T15:15:00+02:00",
        },
        "enquiryPeriod": {
           "startDate": "",
        },
        "contracts": [{
            "status": "",
            "id": "1ac8c648538d4930918b0b0a1e884ef2",
            "awardID": "3d5182c5a0424a4f8508da712affa82f"
        }],
        "awards": [{
            "status": "",
            "bid_id": "44931d9653034837baff087cfc2fb5ac",
            "date": "2016-11-17T13:32:25.774673+02:00",
            "id": "3d5182c5a0424a4f8508da712affa82f"
        }],
        "bids": [{
            "owner": "",
            "date": "",
            "id": ""
        }],
        "value": {
            "currency": "UAH",
            "amount": 1000,
        },
        "procuringEntity": {
        },

    }

test_thresholds = [20000, 50000, 200000, 1000000]
test_payments = [7, 50, 150, 250, 700]

test_bids_invalid = [
            [{
                "owner": "test",
                "date": "2016-03-17T13:32:25.774673+02:00",
                "id": "44931d9653034837baff087cfc2fb5ac",
            }],
            [{
                "status": "invalid",
                "owner": "test",
                "date": "2016-04-17T13:32:25.774673+02:00",
                "id": "44931d9653034837baff087cfc2fb5ac"
            }]]

test_bids_valid = [
            [{
                "owner": "test",
                "date": "2016-04-17T13:32:25.774673+02:00",
                "id": "44931d9653034837baff087cfc2fb5ac",
            }],
            [{
                "owner": "test",
                "date": "2016-05-05T13:32:25.774673+02:00",
                "id": "44931d9653034837baff087cfc2fb5ac",
            }],

            [{
                "owner": "test",
                "date": "2016-05-10T13:32:25.774673+02:00",
                "id": "f55962b1374b43ddb886821c0582bc7f"
            }]]


test_award_period = '2016-04-17T13:32:25.774673+02:00'


class ReportBidsTestCase(unittest.TestCase):

    def setUp(self):
        db_host = config.get('db', 'host')
        db_port = config.get('db', 'port')
        name = config.get('db', 'username')
        password = config.get('db', 'password')
        self.db_name = config.get('db', 'name')
        self.server = couchdb.Server(
            create_db_url(db_host, db_port, name, password),
            session=Session(retry_delays=range(10)))
        self.db = self.server.create(self.db_name)
        self.utility = ReportUtility('test')
        self.utility.payments = test_payments
        self.utility.thresholds = test_thresholds
        self.utility.adb = self.db
        self.utility.db = self.db
        self.utility.view = 'report/bids_owner_date'

    def tearDown(self):
        del self.server[self.db_name]

    def test_payments_computation(self):
        for x in [0, 10000, 20000]:
            self.assertEqual(7, self.utility.get_payment(x))
        for x in [20001, 40000, 50000]:
            self.assertEqual(50, self.utility.get_payment(x))
        for x in [50001, 100000, 200000]:
            self.assertEqual(150, self.utility.get_payment(x))
        for x in [200001, 500000, 1000000]:
            self.assertEqual(250, self.utility.get_payment(x))
        for x in [1000001, 10000000, 2000000]:
            self.assertEqual(700, self.utility.get_payment(x))

    def test_bids_view_invalid_date(self):
        self.utility.start_date = ''
        self.utility.end_date = ''
        self.utility.owner = 'test'
        vals = {
            "awardPeriod": {
                "startDate": test_award_period,
            },
            'owner': 'teser',
            "bids": test_bids_invalid[0],
        }
        doc = copy(test_data)
        doc.update(vals)
        self.db.save(doc)
        self.utility.get_response()
        self.assertEqual(0, len(list(self.utility.response)))

    def test_bids_view_invalid_mode(self):
        self.utility.start_date = ''
        self.utility.end_date = ''
        self.utility.owner = 'test'
        vals = {
            'mode': 'test',
            "awardPeriod": {
                "startDate": test_award_period,
            },
            'owner': 'teser',
            "bids": test_bids_invalid[0],
        }

        doc = copy(test_data)
        doc.update(vals)
        self.db.save(doc)
        self.utility.get_response()
        self.assertEqual(0, len(list(self.utility.response)))

    def test_bids_view_invalid_status(self):
        self.utility.start_date = ''
        self.utility.end_date = ''
        self.utility.owner = 'test'
        vals = {
            "procurementMethod": "open",
            "awardPeriod": {
                "startDate": test_award_period,
            },
            'owner': 'teser',
            'bids': test_bids_invalid[1],
        }
        doc = copy(test_data)
        doc.update(vals)
        self.db.save(doc)
        self.utility.get_response()
        self.assertEqual(0, len(list(self.utility.response)))

    def test_bids_view_invalid_method(self):
        self.utility.start_date = ''
        self.utility.end_date = ''
        self.utility.owner = 'test'
        vals = {
            "procurementMethod": "test",
            "awardPeriod": {
                "startDate": test_award_period,
            },
            'owner': 'teser',
            'bids': test_bids_valid[0],
        }
        doc = copy(test_data)
        doc.update(vals)
        self.db.save(doc)
        self.utility.get_response()
        self.assertEqual(0, len(list(self.utility.response)))

    def test_bids_view_valid(self):
        self.utility.start_date = ''
        self.utility.end_date = ''
        self.utility.owner = 'test'
        vals = {
            "awardPeriod": {
                "startDate": test_award_period,
            },
            'owner': 'teser',
            'bids': test_bids_valid[0],
        }
        doc = copy(test_data)
        doc.update(vals)
        self.db.save(doc)
        self.utility.get_response()
        response = list(self.utility.response)
        self.assertEqual(1, len(response))
        self.assertEqual(1000, response[0]['value']['value'])
        self.assertEqual(
            "44931d9653034837baff087cfc2fb5ac", response[0]['value']['bid']
        )
        self.assertEqual(
            "0006651836f34bcda9a030c0bf3c0e6e", response[0]['value']['tender']
        )
        self.assertEqual(
            "UA-2016-11-12-000150", response[0]['value']['tenderID']
        )
        self.assertEqual(
            u"UAH", response[0]['value']['currency']
        )

    def test_bids_view_period(self):
        self.utility.owner = 'test'
        vals = {
            "awardPeriod": {
                "startDate": test_award_period,
            },
            'owner': 'teser',
            'bids': test_bids_valid[0],
        }
        doc = copy(test_data)
        doc.update(vals)
        self.db.save(doc)
        vals = {
            "_id": "10028cddd23540e5b6abb9efd2756d1d",
            "awardPeriod": {
                "startDate": "2016-11-09T15:00:00+02:00",
            },
            'owner': 'teser',
            'bids': test_bids_valid[1],

        }
        doc = copy(test_data)
        doc.update(vals)
        self.db.save(doc)
        vals = {
            "_id": "00028aasd2isdfsde5b6abb9efd2756d1d",
            "awardPeriod": {
                "startDate": "2016-11-30T15:00:00+02:00",
            },
            'owner': 'teser',
            'bids': test_bids_valid[2],
        }
        doc = copy(test_data)
        doc.update(vals)
        self.db.save(doc)

        self.utility.start_date = ''
        self.utility.end_date = ''
        self.utility.get_response()
        self.assertEqual(3, len(list(self.utility.response)))

        self.utility.start_date = "2016-11-10T15:00:00"
        self.utility.end_date = ''
        self.utility.get_response()
        self.assertEqual(1, len(list(self.utility.response)))
        self.utility.start_date = "2016-12-01T15:00:00"
        self.utility.end_date = ''
        self.utility.get_response()
        self.assertEqual(0, len(list(self.utility.response)))
        self.utility.start_date = "2016-11-01T15:00:00"
        self.utility.end_date = "2016-12-01T15:00:00"
        self.utility.get_response()
        self.assertEqual(2, len(list(self.utility.response)))


class ReportTendersTestCase(unittest.TestCase):

    def setUp(self):
        db_host = config.get('db', 'host')
        db_port = config.get('db', 'port')
        name = config.get('db', 'username')
        password = config.get('db', 'password')
        self.db_name = config.get('db', 'name')
        self.server = couchdb.Server(
            create_db_url(db_host, db_port, name, password),
            session=Session(retry_delays=range(10)))
        self.db = self.server.create(self.db_name)
        self.utility = ReportUtility('test')
        self.utility.payments = test_payments
        self.utility.thresholds = test_thresholds
        self.utility.adb = self.db
        self.utility.db = self.db
        self.utility.view = 'report/tenders_owner_date'

    def tearDown(self):
        del self.server[self.db_name]

    def test_tenders_view_invalid_date(self):
        self.utility.start_date = ''
        self.utility.end_date = ''
        self.utility.owner = 'test'
        vals = {
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
        doc = copy(test_data)
        doc.update(vals)
        self.db.save(doc)
        self.utility.get_response()
        self.assertEqual(0, len(list(self.utility.response)))

    def test_tenders_view_invalid_method(self):
        self.utility.start_date = ''
        self.utility.end_date = ''
        self.utility.owner = 'test'
        vals = {
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
        doc = copy(test_data)
        doc.update(vals)
        self.db.save(doc)
        self.utility.get_response()
        self.assertEqual(0, len(list(self.utility.response)))

    def test_tenders_view_invalid_mode(self):
        self.utility.start_date = ''
        self.utility.end_date = ''
        self.utility.owner = 'test'
        vals = {
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
        doc = copy(test_data)
        doc.update(vals)
        self.db.save(doc)
        self.utility.get_response()
        self.assertEqual(0, len(list(self.utility.response)))

    def test_tenders_view_invalid_status(self):
        self.utility.start_date = ''
        self.utility.end_date = ''
        self.utility.owner = 'test'
        vals = {
            "procurementMethod": "open",
            "enquiryPeriod": {
                 "startDate": '2016-04-17T13:32:25.774673+02:00',
             },
            "contracts": [{
                    "status": "unsuccessful",
                }],
        }
        doc = copy(test_data)
        doc.update(vals)
        self.db.save(doc)
        self.utility.get_response()
        self.assertEqual(0, len(list(self.utility.response)))

    def test_tenders_view_valid(self):
        self.utility.start_date = ''
        self.utility.end_date = ''
        self.utility.owner = 'test'
        vals = {
            "owner": "test",
            "procurementMethod": "open",
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
        doc = copy(test_data)
        doc.update(vals)
        self.db.save(doc)
        self.utility.get_response()
        response = list(self.utility.response)
        self.assertEqual(1, len(response))
        # self.assertEqual(
        #         "2016-06-22T13:32:25.774673+02:00", response[0]['key'][1])


class ReportBidsLotsTestCase(unittest.TestCase):

    def setUp(self):
        db_host = config.get('db', 'host')
        db_port = config.get('db', 'port')
        name = config.get('db', 'username')
        password = config.get('db', 'password')
        self.db_name = config.get('db', 'name')
        self.server = couchdb.Server(
            create_db_url(db_host, db_port, name, password),
            session=Session(retry_delays=range(10)))
        self.db = self.server.create(self.db_name)
        self.utility = ReportUtility('test')
        self.utility.payments = test_payments
        self.utility.thresholds = test_thresholds
        self.utility.adb = self.db
        self.utility.db = self.db
        self.utility.view = 'report/bids_owner_date'

    def tearDown(self):
        del self.server[self.db_name]

    def test_bids_view_with_lots(self):
        self.utility.start_date = ''
        self.utility.end_date = ''
        self.utility.owner = 'test'
        vals = {
            "owner": "test",
            "procurementMethod": "open",
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
        doc = copy(test_data)
        doc.update(vals)
        self.db.save(doc)
        self.utility.get_response()
        response = list(self.utility.response)
        self.assertEqual(1, len(response))


if __name__ == '__main__':
    unittest.main()
