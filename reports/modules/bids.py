import logging
from reports.helpers import thresholds_headers

from reports.core import (
    BaseBidsGenerator,
    RowMixin,
    RowInvoiceMixin,
    HeadersToRowMixin,
    CSVMixin
)

logger = logging.getLogger(__name__)

headers = [
    "tender",
    "tenderID",
    "lot",
    "value",
    "currency",
    "bid",
    'rate',
    "bill"
]

class Bids(BaseBidsGenerator,
           RowMixin,
           HeadersToRowMixin,
           CSVMixin
           ):
    fields = headers
    headers = headers
    module = 'bids'

    def row(self, row):
        record = self.record(row)
        bill = self.get_payment(record['value'])
        logger.info(
            "Bill {} for tender {} with value {}".format(
                bill, record['tender'], record['value']
            )
        )
        row = [str(c) for c in record.values()]
        row.append(str(bill))
        return row


class Invoices(BaseBidsGenerator,
               RowInvoiceMixin,
               HeadersToRowMixin,
               CSVMixin
               ):
    module = 'invoices'
    fields = headers

    def __init__(self, config):
        self.headers = config.headers
        self.counter = [0 for _ in range(5)]
        BaseBidsGenerator.__init__(self, config)

    def row(self, row):
        record = self.record(row)
        payment = self.get_payment(record['value'])
        for i, x in enumerate(self.config.payments):
            if payment == x:
                msg = 'Bill {} for value {} '\
                      'in {} tender'.format(payment, record['value'],
                                            record['tender'])
                logger.info(msg)
                self.counter[i] += 1
