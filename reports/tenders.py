import sys
from core import *
from dateparser import parse

class TendersUtility(ReportUtility):

    def __init__(self):
        ReportUtility.__init__(self, 'tenders', rev=True)
        
        self.headers = ["tender", "value", "bill"]
        self.tenders = set()

    def row(self, record):
        row = []
        id = record["tender"]

        #temporarily skip lots
        if "lot" in record:
            return None
        # --------------
        if id  not in self.tenders:
            self.tenders.add(id)
            row.append(id)
            value= record["value"]
            row.append(value)
            row.append(self.get_payment(float(value)))
            return row


    def rows(self):
        for resp in self.response:
            r = self.row(resp['value'])
            if r:
                yield r

        
        
def run():
    utility= TendersUtility()
    utility.run()
 




if __name__ == "__main__":
    run()
