import unittest
import mock
from reports.tests.base import BaseBidsUtilityTest
from reports.utilities.invoices import InvoicesUtility
from reports.core import thresholds_headers
from copy import copy
from reports.tests.base import test_config

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


class ReportInvoicesUtilityTestCase(BaseBidsUtilityTest):

    def setUp(self):
        super(ReportInvoicesUtilityTestCase, self).setUp()
        self.utility = InvoicesUtility()
        self.utility.init_from_args('test', [], test_config)
        self.utility.headers = thresholds_headers(self.utility.thresholds)

    def tearDown(self):
        del self.server[self.db_name]

    def test_invoices_utility_output(self):
        self.utility.counter = [0 for _ in self.utility.payments]
        data = {
            "awardPeriod": {
                "startDate": test_award_period,
            },
            'owner': 'test',
            'bids': test_bids_valid[0],
        }
        mock_csv = mock.mock_open()
        doc = copy(self.test_data)
        doc.update(data)
        self.utility.db.save(doc)
        with mock.patch('__builtin__.open', mock_csv):
            self.utility.run()
            self.assertEqual(
                self.utility.counter, [1, 0, 0, 0, 0]
            )
            mock_csv.assert_called_once_with('test/test@---invoices.csv', 'w')
            handler = mock_csv()
            handler.write.assert_any_call('{}{}'.format(
                ','.join(self.utility.headers), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(i) for i in self.utility.counter]), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(c*p) for c, p in zip(
                    self.utility.counter, self.utility.payments
                )]), '\r\n'
            ))

        self.utility.counter = [0 for _ in self.utility.payments]
        doc = self.utility.db[doc['_id']]
        doc.update({'value': {'amount': 25000, 'currency': 'UAH'}})
        self.utility.db.save(doc)

        mock_csv = mock.mock_open()
        with mock.patch('__builtin__.open', mock_csv):
            self.utility.run()
            self.assertEqual(
                self.utility.counter, [0, 1, 0, 0, 0]
            )
            mock_csv.assert_called_once_with('test/test@---invoices.csv', 'w')
            handler = mock_csv()
            handler.write.assert_any_call('{}{}'.format(
                ','.join(self.utility.headers), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(i) for i in self.utility.counter]), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(c*p) for c, p in zip(
                    self.utility.counter, self.utility.payments
                )]), '\r\n'
            ))

        self.utility.counter = [0 for _ in self.utility.payments]
        doc = self.utility.db[doc['_id']]
        doc.update({'value': {'amount': 55000, 'currency': 'UAH'}})
        self.utility.db.save(doc)

        mock_csv = mock.mock_open()
        with mock.patch('__builtin__.open', mock_csv):
            self.utility.run()
            self.assertEqual(
                self.utility.counter, [0, 0, 1, 0, 0]
            )
            mock_csv.assert_called_once_with('test/test@---invoices.csv', 'w')
            handler = mock_csv()
            handler.write.assert_any_call('{}{}'.format(
                ','.join(self.utility.headers), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(i) for i in self.utility.counter]), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(c*p) for c, p in zip(
                    self.utility.counter, self.utility.payments
                )]), '\r\n'
            ))

        self.utility.counter = [0 for _ in self.utility.payments]
        doc = self.utility.db[doc['_id']]
        doc.update({'value': {'amount': 255000, 'currency': 'UAH'}})
        self.utility.db.save(doc)

        mock_csv = mock.mock_open()
        with mock.patch('__builtin__.open', mock_csv):
            self.utility.run()
            self.assertEqual(
                self.utility.counter, [0, 0, 0, 1, 0]
            )
            mock_csv.assert_called_once_with('test/test@---invoices.csv', 'w')
            handler = mock_csv()
            handler.write.assert_any_call('{}{}'.format(
                ','.join(self.utility.headers), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(i) for i in self.utility.counter]), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(c*p) for c, p in zip(
                    self.utility.counter, self.utility.payments
                )]), '\r\n'
            ))

        self.utility.counter = [0 for _ in self.utility.payments]
        doc = self.utility.db[doc['_id']]
        doc.update({'value': {'amount': 1255000, 'currency': 'UAH'}})
        self.utility.db.save(doc)

        mock_csv = mock.mock_open()
        with mock.patch('__builtin__.open', mock_csv):
            self.utility.run()
            self.assertEqual(
                self.utility.counter, [0, 0, 0, 0, 1]
            )
            mock_csv.assert_called_once_with('test/test@---invoices.csv', 'w')
            handler = mock_csv()
            handler.write.assert_any_call('{}{}'.format(
                ','.join(self.utility.headers), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(i) for i in self.utility.counter]), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(c*p) for c, p in zip(
                    self.utility.counter, self.utility.payments
                )]), '\r\n'
            ))
            del self.utility.db[doc['_id']]

        doc = copy(self.test_data)
        data = {
            "awardPeriod": {
                "startDate": test_award_period,
            },
            'owner': 'test',
            'bids': test_bids_valid[0],
        }

        doc.update(data)
        self.utility.db.save(doc)
        doc.update({
            '_id': 'sddsfsdd',
            'value': {'amount': 25000, 'currency': 'UAH'}
        })
        self.utility.db.save(doc)
        doc.update({
            '_id': 'sddsfsdf',
            'value': {'amount': 55000, 'currency': 'UAH'}
        })
        self.utility.db.save(doc)
        doc.update({
            '_id': 'sddsfsdfa',
            'value': {'amount': 255000, 'currency': 'UAH'}
        })
        self.utility.db.save(doc)
        doc.update({
            '_id': 'sddsfsdfb',
            'value': {'amount': 1255000, 'currency': 'UAH'}
        })
        self.utility.db.save(doc)
        mock_csv = mock.mock_open()
        self.utility.counter = [0 for _ in self.utility.payments]
        with mock.patch('__builtin__.open', mock_csv):
            self.utility.run()
            self.assertEqual(
                self.utility.counter, [1, 1, 1, 1, 1]
            )
            mock_csv.assert_called_once_with('test/test@---invoices.csv', 'w')
            handler = mock_csv()
            handler.write.assert_any_call('{}{}'.format(
                ','.join(self.utility.headers), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(i) for i in self.utility.counter]), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(c*p) for c, p in zip(
                    self.utility.counter, self.utility.payments)]
                ), '\r\n'
            ))
            del self.utility.db[doc['_id']]


if __name__ == '__main__':
    unittest.main()
