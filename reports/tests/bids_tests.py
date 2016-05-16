import unittest
import mock
from reports.tests.base import BaseBidsUtilityTest
from reports.utilities.bids import BidsUtility
from copy import copy
from reports.tests.base import test_config


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


class ReportBidsViewTestCase(BaseBidsUtilityTest):

    def setUp(self):
        super(ReportBidsViewTestCase, self).setUp()
        self.utility.headers = [u"tender", u"tenderID", u"lot",
                                u"value", u"currency", u"bid", u"bill"]

    def test_bids_view_invalid_date(self):
        data = {
            "awardPeriod": {
                "startDate": test_award_period,
            },
            'owner': 'teser',
            "bids": test_bids_invalid[0],
        }
        self.assertLen(0, data)

    def test_bids_view_invalid_mode(self):
        data = {
            'mode': 'test',
            "awardPeriod": {
                "startDate": test_award_period,
            },
            'owner': 'teser',
            "bids": test_bids_valid[0],
        }
        self.assertLen(0, data)

    def test_bids_view_invalid_status(self):
        data = {
            "procurementMethod": "open",
            "awardPeriod": {
                "startDate": test_award_period,
            },
            'owner': 'teser',
            'bids': test_bids_invalid[1],
        }
        self.assertLen(0, data)

    def test_bids_view_invalid_method(self):
        data = {
            "procurementMethod": "test",
            "awardPeriod": {
                "startDate": test_award_period,
            },
            'owner': 'teser',
            'bids': test_bids_valid[0],
        }
        self.assertLen(0, data)

    def test_bids_view_valid(self):
        data = {
            "awardPeriod": {
                "startDate": test_award_period,
            },
            'owner': 'teser',
            'bids': test_bids_valid[0],
        }
        self.assertLen(1, data)
        response = list(self.utility.response)
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
        data = {
            "awardPeriod": {
                "startDate": test_award_period,
            },
            'owner': 'teser',
            'bids': test_bids_valid[0],
        }
        doc = copy(self.test_data)
        doc.update(data)
        self.utility.db.save(doc)
        data = {
            "_id": "10028cddd23540e5b6abb9efd2756d1d",
            "awardPeriod": {
                "startDate": "2016-11-09T15:00:00+02:00",
            },
            'owner': 'teser',
            'bids': test_bids_valid[1],

        }
        doc = copy(self.test_data)
        doc.update(data)
        self.utility.db.save(doc)
        data = {
            "_id": "00028aasd2isdfsde5b6abb9efd2756d1d",
            "awardPeriod": {
                "startDate": "2016-11-30T15:00:00+02:00",
            },
            'owner': 'teser',
            'bids': test_bids_valid[2],
        }
        doc = copy(self.test_data)
        doc.update(data)
        self.utility.db.save(doc)

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

    def test_bids_view_with_lots(self):
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
        self.assertLen(1, data)


class ReportBidsUtilityTestCase(BaseBidsUtilityTest):

    def setUp(self):
        super(ReportBidsUtilityTestCase, self).setUp()
        self.utility = BidsUtility()
        self.utility.init_from_args('test', [], test_config)

    def tearDown(self):
        del self.server[self.db_name]

    def test_bids_utility_output(self):
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
            mock_csv.assert_called_once_with('test/test@---bids.csv', 'w')
            handler = mock_csv()
            handler.write.assert_any_call(
                'tender,tenderID,lot,value,currency,bid,bill\r\n'
            )
            handler.write.assert_any_call(
                '0006651836f34bcda9a030c0bf3c0e6e,'
                'UA-2016-11-12-000150,,1000,UAH,'
                '44931d9653034837baff087cfc2fb5ac,7.0\r\n'
            )

    def test_bids_utility_output_with_lots(self):
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
        doc = copy(self.test_data)
        doc.update(data)
        self.utility.db.save(doc)
        with mock.patch('__builtin__.open', mock_csv):
            self.utility.run()
            mock_csv.assert_called_once_with('test/test@---bids.csv', 'w')
            handler = mock_csv()
            handler.write.assert_any_call(
                'tender,tenderID,lot,value,currency,bid,bill\r\n'
            )
            handler.write.assert_any_call(
                '0006651836f34bcda9a030c0bf3c0e6e,'
                'UA-2016-11-12-000150,324d7b2dd7a54df29bad6d0b7c91b2e9,'
                '2000,UAH,a22ef2b1374b43ddb886821c0582bc7dk,7.0\r\n'
            )


if __name__ == '__main__':
    unittest.main()
