from core import (
    ReportUtility,
    parse_args,
    thresholds_headers,
)


class RefundsUtility(ReportUtility):

    def __init__(self):
        ReportUtility.__init__(self, 'refunds', rev=True)
        self.tenders = set()
        self.view = 'report/tenders_owner_date'

    def row(self, record):
        value = record["value"]
        id = record["tender"]
        if record[u'currency'] not in [u'UAH']:
            return
        if id not in self.tenders:
            self.tenders.add(id)
            payment = self.get_payment(float(value))
            for i, x in enumerate(self.payments):
                if payment == x:
                    self.counter[i] += 1

    def get_rows(self):
        row = []
        for c, v in zip(self.counter, self.payments):
            row.append(c*v)
        self._rows.append(row)

    def rows(self):
        for resp in self.response:
            self.row(resp['value'])
        self.get_rows()
        for row in self._rows:
            yield row


def run():
    utility = RefundsUtility()
    owner, period, config = parse_args()
    utility.init_from_args(owner, period, config)
    utility.headers = thresholds_headers(utility.thresholds)
    utility.counter = [0 for _ in xrange(len(utility.payments))]
    utility._rows = [utility.counter, utility.payments]
    utility.run()


if __name__ == "__main__":
    run()
