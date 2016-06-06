import unittest
import mock
from reports.helpers import value_currency_normalize
from reports.tests.utils import MockCurrencyResponce


class ValueNormalizationTestCase(unittest.TestCase):
    @mock.patch(
        'reports.helpers.requests.get',
        new=lambda *args, **kwargs: MockCurrencyResponce())
    def test_value_normalization(self):
        self.assertRaises(
            ValueError,
            value_currency_normalize,
            '1',
            u'EUR',
            '2015-10-11'
        )
        value_valid = 10
        currencies = [u'USD', u'RUR', u'EUR']
        for curr in currencies:
            value, rate = value_currency_normalize(
                value_valid, curr, '2015-10-11'
            )
            self.assertEqual(20, value)

if __name__ == '__main__':
    unittest.main()
