from reports.core import (
    ReportUtility,
    parse_args,
    value_currency_normalize
)


class TendersUtility(ReportUtility):

    def __init__(self):
        ReportUtility.__init__(self, 'tenders', rev=True)
        self.view = 'report/tenders_owner_date'
        self.headers = ["tender", "tenderID", "lot", "currency",
                        "kind", "value", "bill"]

    def row(self, record):
        row = list(record.get(col, '') for col in self.headers[:-1])
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

        row.append(self.get_payment(value))
        self.Logger.info("Bill {} for tender {} with value {}".format(
                row[-1], row[0], value
            )
        )
        return row

    def rows(self):
        for resp in self.response:
            r = self.row(resp['value'])
            if r:
                yield r


def run():
    utility = TendersUtility()
    owner, period, config = parse_args()
    utility.init_from_args(owner, period, config)
    utility.run()

if __name__ == "__main__":
    run()
