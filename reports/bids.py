from core import *
import sys
from dateparser import parse


class BidsUtility(ReportUtility):

    def __init__(self):
        ReportUtility.__init__(self, 'bids')
        
        self.headers = [u"tender", u"lot", u"value", u"bid", u"bill"]


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

    def run(self):
        if len(sys.argv) < 3:
            raise RuntimeError
        owner = OWNERS[sys.argv[1]]
        start_key =[owner, parse(sys.argv[2]).isoformat()] 
        if len(sys.argv) > 3:
            end_key = [owner, parse(sys.argv[3]).isoformat()]
        else:
            end_key = ''

        self.get_response(start_key, end_key)
        file_name = build_name(owner, start_key, end_key, 'bids')

        write_csv(file_name, self.headers, self.rows())

        


        
        
        
def run():
    utility= BidsUtility()
    utility.run()
   

if __name__ == "__main__":
    run()
