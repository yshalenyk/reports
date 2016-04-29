from core import *
import sys
from dateparser import parse


class BidsUtility(ReportUtility):

    def __init__(self):
        ReportUtility.__init__(self, 'bids')
        
        self.headers = [u"tender", u"lot", u"value", u"currency", u"bid", u"bill"]
        self.view = 'report/bids_owner_date' 


    def row(self, record):
        row = []
        for k in self.headers[:-1]:
            try:
                cell = record[k]
                if k == u'value':
                    bill = self.get_payment(float(cell))
                row.append(cell)
            except KeyError:
                row.append('')
        row.append(bill)
        return row

    def rows(self):
        for resp in self.response:
            yield self.row(resp["value"])

       
def run():
    utility= BidsUtility()
    owner, period, config = parse_args()
    utility.init_from_args(owner, period, config)
    utility.run()
   

if __name__ == "__main__":
    run()
