from reports.core import BaseBidsUtility
from reports.helpers import (
    thresholds_headers,
    value_currency_normalize
)


class InvoicesUtility(BaseBidsUtility):

    def __init__(self):
        super(InvoicesUtility, self).__init__('invoices')
        self.headers = thresholds_headers(
            self.config.thresholds
        )

        self.counter = [0 for _ in xrange(0, 5)]

    def row(self, record):
        value = float(record.get("value", 0))
        bid = record.get(u"bid", '')
        use_audit = True
        self.get_initial_bids(record.get('audits', ''),
                              record.get('tender', ''))
        if not self.initial_bids:
            use_audit = False

        if record.get('startdate', '') < "2016-04-01" and \
                not self.bid_date_valid(bid):
            return
        if record[u'currency'] != u'UAH':
            old = value
            value, rate = value_currency_normalize(
                value, record[u'currency'], record[u'startdate']
            )
            msg = "Changed value {} {} by exgange rate {} on {}"\
                " is  {} UAH in {}".format(
                    old, record[u'currency'], rate,
                    record[u'startdate'], value, record['tender']
                )
            self.Logger.info(msg)

        if use_audit:
            initial_bid = [b for b in self.initial_bids
                           if b['bidder'] == bid]
            if not initial_bid:
                initial_bid_date = record.get('initialDate', '')
            else:
                initial_bid_date = initial_bid[0]['date']

        else:
            self.Logger.fatal('Unable to load initial bids'
                              ' for tender id={} for audits.'
                              'Use initial bid date from revisions'.format(record.get('tender')))
            initial_bid_date = record.get('initialDate', '')
            self.Logger.info('Initial date from revisions {}'.format(initial_bid_date))

        payment = self.get_payment(value, initial_bid_date < self.threshold_date)
        for i, x in enumerate(self.payments):
            if payment == x:
                msg = 'Computated bill {} for value {} '\
                      'in {} tender'.format(payment, value, record['tender'])
                self.Logger.info(msg)
                self.counter[i] += 1

    def rows(self):
        self._rows = [self.counter, self.payments]
        for resp in self.response:
            self.row(resp['value'])
        self._rows.append(
            [c * v for c, v in zip(self.counter, self.payments)]
        )
        for row in self._rows:
            yield row


def run():
    utility = InvoicesUtility()
    utility.run()


if __name__ == "__main__":
    run()
