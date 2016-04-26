import sys
from core import *
from dateparser import parse



class RefundsUtility(ReportUtility):

    def __init__(self):
        ReportUtility.__init__(self, 'bids', rev=True)
        
        self.headers = thresholds_headers(self.thresholds)
        self.tenders = set()
        self.counter = [0 for _ in xrange(len(self.payments))]
        self.rows = [self.counter, self.payments]

    def count_row(self, record):
        # skip lots for now
        if "lot" in record:
            return
        #-------------------- 
        value = record["value"]
        id = record["tender"]
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
        self.rows.append(row)

    def count_rows(self):
        for resp in self.response:
            self.count_row(resp['value'])
    




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
        self.count_rows()
        self.get_rows()
        file_name = build_name(owner, start_key, end_key, 'refunds')

        write_csv(file_name, self.headers, self.rows)


def run():
    utility = RefundsUtility()
    utility.run()




if __name__ == "__main__":
    run()
