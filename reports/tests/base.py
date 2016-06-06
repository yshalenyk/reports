# coding: utf-8
import unittest
import couchdb
import mock
from reports.utilities import bids, invoices, tenders, refunds
from copy import copy
from reports.tests.utils import(
    get_mock_parser,
    test_data
)


class BaseUtilityTest(unittest.TestCase):

    def setUp(self):
        self.server = couchdb.Server('http://test:test@127.0.0.1:5984')
        self.test_data = test_data
        self.db_name = 'reports-test'
        if self.db_name not in self.server:
            self.server.create(self.db_name)

    def test_payments_computation(self):
        for x in [0, 10000, 20000]:
            self.assertEqual(
                self.utility.config.payments[0], self.utility.get_payment(x))
        for x in [20001, 40000, 50000]:
            self.assertEqual(
                self.utility.config.payments[1], self.utility.get_payment(x))
        for x in [50001, 100000, 200000]:
            self.assertEqual(
                self.utility.config.payments[2], self.utility.get_payment(x))
        for x in [200001, 500000, 1000000]:
            self.assertEqual(
                self.utility.config.payments[3], self.utility.get_payment(x))
        for x in [1000001, 10000000, 2000000]:
            self.assertEqual(
                self.utility.config.payments[4], self.utility.get_payment(x))

    def tearDown(self):
        del self.server[self.db_name]

    def assertLen(self, count, data):
        doc = copy(self.test_data)
        doc.update(data)
        self.utility.db.save(doc)
        self.utility.get_response()
        self.utility.response = list(self.utility.response)
        self.assertEqual(count, len(self.utility.response))


class BaseBidsUtilityTest(BaseUtilityTest):

    def setUp(self):
        super(BaseBidsUtilityTest, self).setUp()
        mock_parse = get_mock_parser()
        with mock.patch('argparse.ArgumentParser.parse_args', mock_parse):
            self.utility = bids.BidsUtility()


class BaseTenderUtilityTest(BaseUtilityTest):

    def setUp(self):
        super(BaseTenderUtilityTest, self).setUp()
        mock_parse = get_mock_parser()
        type(mock_parse.return_value).kind = mock.PropertyMock(
            return_value=['general'])
        with mock.patch('argparse.ArgumentParser.parse_args', mock_parse):
            self.utility = tenders.TendersUtility()


class BaseRefundsUtilityTest(BaseUtilityTest):

    def setUp(self):
        super(BaseRefundsUtilityTest, self).setUp()
        mock_parse = get_mock_parser()
        type(mock_parse.return_value).kind = mock.PropertyMock(
            return_value=['general'])
        with mock.patch('argparse.ArgumentParser.parse_args', mock_parse):
            self.utility = refunds.RefundsUtility()


class BaseInvoicesUtilityTest(BaseUtilityTest):

    def setUp(self):
        super(BaseInvoicesUtilityTest, self).setUp()
        mock_parse = get_mock_parser()
        with mock.patch('argparse.ArgumentParser.parse_args', mock_parse):
            self.utility = invoices.InvoicesUtility()
