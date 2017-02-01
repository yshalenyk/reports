from reports.core import BaseBidsUtility
from reports.helpers import (
    get_cmd_parser,
    value_currency_normalize
)


class BidsUtility(BaseBidsUtility):

    def __init__(self):
        super(BidsUtility, self).__init__('bids')
        self.headers = [u"tender", u"tenderID", u"lot",
                        u"value", u"currency", u"bid", u'rate', u"bill"]

    def row(self, record):
        bid = record.get(u'bid', '')
        rate = None
        use_audit = True
        self.get_initial_bids(record.get('audits', ''),
                              record.get('tender', ''))

        if not self.initial_bids:
            use_audit = False
        if record.get('startdate', '') < "2016-04-01" and \
                not self.bid_date_valid(bid):
            return
        row = list(record.get(col, '') for col in self.headers[:-2])
        value = float(record.get(u'value', 0))
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
        r = str(rate) if rate else ''
        row.append(r)
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
        row.append(self.get_payment(value, initial_bid_date > self.threshold_date))
        self.Logger.info(
            "Bill {} for tender {} with value {}".format(
                row[-1], row[0], value
            )
        )
        return row

    def rows(self):
        for resp in self.response:
            row = self.row(resp["value"])
            if row:
                yield row


def run():
    utility = BidsUtility()
    utility.run()


if __name__ == "__main__":
    run()
