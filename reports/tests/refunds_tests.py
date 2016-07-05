import unittest
import mock
from reports.tests.base import BaseRefundsUtilityTest
from copy import copy


test_award_period = '2016-04-17T13:32:25.774673+02:00'


class ReportRefundsUtilityTestCase(BaseRefundsUtilityTest):

    def test_invoices_utility_output(self):
        self.utility.counter = [0 for _ in self.utility.config.payments]
        data = {
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
        mock_csv = mock.mock_open()
        doc = copy(self.test_data)
        doc.update(data)
        self.utility.db.save(doc)
        with mock.patch('__builtin__.open', mock_csv):
            self.utility.run()
            self.assertEqual(
                self.utility.counter, [1, 0, 0, 0, 0]
            )
            calls = [
                mock.call('test/test@---refunds.csv', 'w'),
                mock.call().__enter__(),
                mock.call().write(
                    str('{}{}'.format(','.join(self.utility.headers), '\r\n'))
                ),
                mock.call().write('{}{}'.format(','.join(
                    [str(i) for i in self.utility.counter]), '\r\n')
                ),
                mock.call().write('{}{}'.format(','.join(
                    [str(i) for i in self.utility.config.payments]), '\r\n')
                ),
                mock.call().write('{}{}'.format(','.join([
                    str(c * p) for c, p in zip(
                        self.utility.counter, self.utility.config.payments
                    )]), '\r\n')
                ),
                mock.call().__exit__(None, None, None),
            ]
            mock_csv.assert_has_calls(calls)

        self.utility.counter = [0 for _ in self.utility.config.payments]
        doc = self.utility.db[doc['_id']]
        doc.update({'value': {'amount': 25000, 'currency': 'UAH'}})
        self.utility.db.save(doc)

        mock_csv = mock.mock_open()
        with mock.patch('__builtin__.open', mock_csv):
            self.utility.run()
            self.assertEqual(
                self.utility.counter, [0, 1, 0, 0, 0]
            )
            mock_csv.assert_called_once_with('test/test@---refunds.csv', 'w')
            handler = mock_csv()
            handler.write.assert_any_call('{}{}'.format(
                ','.join(self.utility.headers), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(i) for i in self.utility.counter]), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(c * p) for c, p in zip(
                    self.utility.counter, self.utility.config.payments
                )]), '\r\n'
            ))

        self.utility.counter = [0 for _ in self.utility.config.payments]
        doc = self.utility.db[doc['_id']]
        doc.update({'value': {'amount': 55000, 'currency': 'UAH'}})
        self.utility.db.save(doc)

        mock_csv = mock.mock_open()
        with mock.patch('__builtin__.open', mock_csv):
            self.utility.run()
            self.assertEqual(
                self.utility.counter, [0, 0, 1, 0, 0]
            )
            mock_csv.assert_called_once_with('test/test@---refunds.csv', 'w')
            handler = mock_csv()
            handler.write.assert_any_call('{}{}'.format(
                ','.join(self.utility.headers), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(i) for i in self.utility.counter]), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(c * p) for c, p in zip(
                    self.utility.counter, self.utility.config.payments
                )]), '\r\n'
            ))

        self.utility.counter = [0 for _ in self.utility.config.payments]
        doc = self.utility.db[doc['_id']]
        doc.update({'value': {'amount': 255000, 'currency': 'UAH'}})
        self.utility.db.save(doc)

        mock_csv = mock.mock_open()
        with mock.patch('__builtin__.open', mock_csv):
            self.utility.run()
            self.assertEqual(
                self.utility.counter, [0, 0, 0, 1, 0]
            )
            mock_csv.assert_called_once_with('test/test@---refunds.csv', 'w')
            handler = mock_csv()
            handler.write.assert_any_call('{}{}'.format(
                ','.join(self.utility.headers), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(i) for i in self.utility.counter]), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(c * p) for c, p in zip(
                    self.utility.counter, self.utility.config.payments
                )]), '\r\n'
            ))

        self.utility.counter = [0 for _ in self.utility.config.payments]
        doc = self.utility.db[doc['_id']]
        doc.update({'value': {'amount': 1255000, 'currency': 'UAH'}})
        self.utility.db.save(doc)

        mock_csv = mock.mock_open()
        with mock.patch('__builtin__.open', mock_csv):
            self.utility.run()
            self.assertEqual(
                self.utility.counter, [0, 0, 0, 0, 1]
            )
            mock_csv.assert_called_once_with('test/test@---refunds.csv', 'w')
            handler = mock_csv()
            handler.write.assert_any_call('{}{}'.format(
                ','.join(self.utility.headers), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(i) for i in self.utility.counter]), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(c * p) for c, p in zip(
                    self.utility.counter, self.utility.config.payments
                )]), '\r\n'
            ))
            del self.utility.db[doc['_id']]

        doc = copy(self.test_data)
        data = {
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
        self.utility.counter = [0 for _ in self.utility.config.payments]
        with mock.patch('__builtin__.open', mock_csv):
            self.utility.run()
            self.assertEqual(
                self.utility.counter, [1, 1, 1, 1, 1]
            )
            mock_csv.assert_called_once_with('test/test@---refunds.csv', 'w')
            handler = mock_csv()
            handler.write.assert_any_call('{}{}'.format(
                ','.join(self.utility.headers), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(i) for i in self.utility.counter]), '\r\n'
            ))
            handler.write.assert_any_call('{}{}'.format(
                ','.join([str(c * p) for c, p in zip(
                    self.utility.counter, self.utility.config.payments)]
                ), '\r\n'
            ))
            del self.utility.db[doc['_id']]

def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(ReportRefundsUtilityTestCase))
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
