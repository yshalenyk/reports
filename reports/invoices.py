from core import *
import sys
from dateparser import parse



class InvoicesUtility(ReportUtility):

    def __init__(self):
        ReportUtility.__init__(self, 'invoices')
        
        self.headers = thresholds_headers(self.thresholds)
        self.counter = [0 for _ in xrange(len(self.payments))]
        self._rows = [self.counter, self.payments]

 


    def row(self, record):
        value = record["value"]
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
    utility= InvoicesUtility()
    utility.run()
 


if __name__ == "__main__":
    run()
