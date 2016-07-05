# -*- coding: utf-8 -*-

import unittest
from reports.tests import(
    bids_tests,
    invoices_tests,
    normalization_tests,
    refunds_tests,
    tenders_tests
)


def suite():
    suite = unittest.TestSuite()
    suite.addTest(bids_tests.suite())
    suite.addTest(invoices_tests.suite())
    suite.addTest(normalization_tests.suite())
    suite.addTest(refunds_tests.suite())
    suite.addTest(tenders_tests.suite())
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='suite')
