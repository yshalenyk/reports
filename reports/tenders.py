import sys
from core import *
from dateparser import parse

class TendersUtility(ReportUtility):

    def __init__(self):
        ReportUtility.__init__(self, 'bids', rev=True)
        
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
        file_name = build_name(owner, start_key, end_key, 'tenders')

        write_csv(file_name, self.headers, self.rows())

        


        
        
        
def run():
    utility= TendersUtility()
    utility.run()
 




if __name__ == "__main__":
    run()
