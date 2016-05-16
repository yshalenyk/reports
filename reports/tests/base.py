import unittest
import couchdb
import os.path
from reports.core import ReportUtility
from copy import copy


test_config = os.path.join(os.path.dirname(__file__), 'tests.ini')


test_data = {
        "procurementMethod": "open",
        "status": "complete",
        "owner": "",
        "_id": "0006651836f34bcda9a030c0bf3c0e6e",
        "tenderID": "UA-2016-11-12-000150",
        "dateModified": "2016-04-31T19:03:53.704712+03:00",
        "tenderPeriod": {
            "startDate": "2016-11-13T15:15:00+02:00",
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


class BaseUtilityTest(unittest.TestCase):
    def setUp(self):
        self.server = couchdb.Server('http://test:test@127.0.0.1:5984')
        self.test_data = test_data
        self.db_name = 'reports-test'
        if self.db_name not in self.server:
            self.server.create(self.db_name)
        self.utility = ReportUtility('test')
        self.utility.init_from_args('test', [], test_config)
        self.test_payments_computation()

    def test_payments_computation(self):
        for x in [0, 10000, 20000]:
            self.assertEqual(
                self.utility.payments[0], self.utility.get_payment(x))
        for x in [20001, 40000, 50000]:
            self.assertEqual(
                self.utility.payments[1], self.utility.get_payment(x))
        for x in [50001, 100000, 200000]:
            self.assertEqual(
                self.utility.payments[2], self.utility.get_payment(x))
        for x in [200001, 500000, 1000000]:
            self.assertEqual(
                self.utility.payments[3], self.utility.get_payment(x))
        for x in [1000001, 10000000, 2000000]:
            self.assertEqual(
                self.utility.payments[4], self.utility.get_payment(x))

    def tearDown(self):
        del self.server[self.db_name]

    def assertLen(self, count, data):
        doc = copy(self.test_data)
        doc.update(data)
        self.utility.db.save(doc)
        self.utility.get_response()
        self.utility.response = list(self.utility.response)


class BaseBidsUtilityTest(BaseUtilityTest):

    def setUp(self):
        super(BaseBidsUtilityTest, self).setUp()
        self.utility.view = 'report/bids_owner_date'


class BaseTenderUtilityTest(BaseUtilityTest):

    def setUp(self):
        super(BaseTenderUtilityTest, self).setUp()
        self.utility.view = 'report/tenders_owner_date'
