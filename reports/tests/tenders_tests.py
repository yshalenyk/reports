import unittest
import mock
from copy import copy
from reports.tests.base import BaseTenderUtilityTest, test_config
from reports.utilities.tenders import TendersUtility

test_award_period = '2016-04-17T13:32:25.774673+02:00'


class ReportTendersTestCase(BaseTenderUtilityTest):

    def setUp(self):
        super(ReportTendersTestCase, self).setUp()

    def tearDown(self):
        del self.server[self.db_name]

    def test_tenders_view_invalid_date(self):
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
        self.assertLen(0, data)

    def test_tenders_view_invalid_method(self):
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
        self.assertLen(0, data)

    def test_tenders_view_invalid_mode(self):
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
        self.assertLen(0, data)

    def test_tenders_view_invalid_status(self):
        data = {
            "procurementMethod": "open",
            "enquiryPeriod": {
                 "startDate": '2016-04-17T13:32:25.774673+02:00',
             },
            "contracts": [{
                    "status": "unsuccessful",
                }],
        }
        self.assertLen(0, data)

    def test_tenders_view_valid(self):
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
        self.assertLen(1, data)
        # response = list(self.utility.response)
        # self.assertEqual(
        #         "2016-06-22T13:32:25.774673+02:00", response[0]['key'][1])


class ReportTendersUtilityTestCase(BaseTenderUtilityTest):

    def setUp(self):
        super(ReportTendersUtilityTestCase, self).setUp()
        self.utility = TendersUtility()
        self.utility.init_from_args('test', [], test_config)

    def tearDown(self):
        del self.server[self.db_name]

    def test_tenders_utility_output(self):
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
            mock_csv.assert_called_once_with('test/test@---tenders.csv', 'w')
            handler = mock_csv()
            handler.write.assert_any_call(
                'tender,tenderID,lot,currency,kind,value,bill\r\n'
            )
            handler.write.assert_any_call(
                '0006651836f34bcda9a030c0bf3c0e6e,'
                'UA-2016-11-12-000150,,UAH,_kind,1000,5.0\r\n'
            )


if __name__ == '__main__':
    unittest.main()
