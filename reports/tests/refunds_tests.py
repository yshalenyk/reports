import unittest
import mock
from reports.tests.base import BaseRefundsUtilityTest
from copy import copy

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

class ReportRefundsUtilityTestCase(BaseRefundsUtilityTest):

    def test_invoices_utility_output(self):
        self.utility.counter = [0 for _ in self.utility.config.payments]
        data = { "awardPeriod": {
                    "startDate": '2016-04-17T13:32:25.774673+02:00',
                },
                "lots": test_lots,
                "bids": test_bids,
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
        doc['lots'][0]['value']= {'amount': 25000, 'currency': 'UAH'}
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
        doc['lots'][0]['value']= {'amount': 55000, 'currency': 'UAH'}
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
        doc['lots'][0]['value']= {'amount': 255000, 'currency': 'UAH'}
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
        doc['lots'][0]['value']= {'amount': 1255000, 'currency': 'UAH'}
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
                "awardPeriod": {
                    "startDate": '2016-04-17T13:32:25.774673+02:00',
                },
                "lots": test_lots,
                "bids": test_bids,
        }
        doc.update(data)
        self.utility.db.save(doc)
        doc.update({'_id': 'sddsfsdd'})
        doc['lots'][0]['value']= {'amount': 25000, 'currency': 'UAH'}

        self.utility.db.save(doc)
        doc.update({'_id': 'sddsfsdf'})
        doc['lots'][0]['value']= {'amount': 55000, 'currency': 'UAH'}

        self.utility.db.save(doc)
        doc.update({'_id': 'sddsfsdfa'})
        doc['lots'][0]['value']= {'amount': 255000, 'currency': 'UAH'}

        self.utility.db.save(doc)
        doc.update({'_id': 'sddsfsdfb'})
        doc['lots'][0]['value']= {'amount': 1255000, 'currency': 'UAH'}

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
