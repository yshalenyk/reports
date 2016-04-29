import sys
from core import *
from dateparser import parse


class TendersUtility(ReportUtility):

    def __init__(self):
        ReportUtility.__init__(self, 'tenders', rev=True)
        self.view = 'report/tenders_owner_date'
        self.headers = ["tender", "value", "bill", "kind"]
        self.tenders = set()

    def row(self, record):
        row = []
        id = record["tender"]

        if id not in self.tenders:
            self.tenders.add(id)
            row.append(id)
            value = record["value"]
            row.append(value)
            row.append(self.get_payment(float(value)))
            row.append(record["kind"])
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
