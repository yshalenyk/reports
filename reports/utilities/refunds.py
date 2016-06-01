from reports.core import (
    BaseUtility,
    parse_args,
    thresholds_headers,
    value_currency_normalize
)


class RefundsUtility(BaseUtility):

    def __init__(self):
        super(RefundsUtility, self).__init__('refunds', rev=True)
        self.view = 'report/tenders_owner_date'

    def row(self, record):
        tender = record.get('tender', '')
        lot = record.get('lot', '')
        if lot:
            if tender in self.ignored_list and lot in self.ignored_list:
                self.Logger.info(
                    'Scip tender {} with lot {} by'
                    ' ignore list'.format(tender, lot)
                )
                return
        else:
            if tender in self.ignored_list:
                self.Logger.info(
                    'Scip tender {} by ignore list'.format(tender)
                )
                return
        if record.get('kind') == u'other':
            self.Logger.info('Scip tender {} by kind'.format(tender))
            return
        value = float(record.get("value", 0))
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
        payment = self.get_payment(value)
        for i, x in enumerate(self.config.payments):
            if payment == x:
                msg = 'Bill {} for value {} in tender {}'.format(
                    payment, value, record['tender']
                )
                self.Logger.info(msg)
                self.counter[i] += 1

    def rows(self):
        self._rows = [self.counter, self.config.payments]
        for resp in self.response:
            self.row(resp['value'])
        self._rows.append(
            [c * v for c, v in zip(self.counter, self.config.payments)]
        )
        for row in self._rows:
            yield row


def run():
    utility = RefundsUtility()
    owner, period, config, ignored = parse_args()
    utility.initialize(owner, period, config, ignored)
    utility.headers = thresholds_headers(utility.config.thresholds)
    utility.counter = [0 for _ in utility.config.payments]
    utility.run()


if __name__ == "__main__":
    run()
