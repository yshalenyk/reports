from reports.core import (
    ReportUtility,
    parse_args
)


class TendersUtility(ReportUtility):

    def __init__(self):
        ReportUtility.__init__(self, 'tenders', rev=True)
        self.view = 'report/tenders_owner_date'
        self.headers = ["tender", "tenderID", "lot", "currency",
                        "kind", "value", "bill"]
        self.tenders = set()

    def row(self, record):
        id = record["tender"]
        if id not in self.tenders:
            self.tenders.add(id)
            row = list(record.get(col) for col in self.headers[:-1])
            row.append(self.get_payment(float(record.get(u'value', 0))))
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
