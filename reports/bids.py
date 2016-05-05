from core import *
import sys
import yaml
import requests
from dateparser import parse


class BidsUtility(ReportUtility):

    def __init__(self):
        ReportUtility.__init__(self, 'bids')
        
        self.headers = [u"tender", u"lot", u"value", u"currency", u"bid", u"bill"]
        self.view = 'report/bids_owner_date' 
        self.skip_bids = set()


    def row(self, record):
        row = []
        audit = record.get(u'audits', '')
        if audit:
            try:
               yfile = yaml.load(requests.get(self.api_url + audit['url']).text)
               initial_bids = yfile['timeline']['auction_start']['initial_bids']
               for bid in initial_bids:
                   if bid['date'] < "2016-04-01T00:00+0300":
                      self.skip_bids.add(bid['bidder'])
            except Exception:
                self.config.logger('falied to parse audit file')
                
        for k in self.headers[:-1]:
            try:
                cell = record[k]
                if k == u'bid':
                    if cell in self.skip_bids:
                        return None
                if k == u'value':
                    bill = self.get_payment(float(cell))
                row.append(cell)
            except KeyError:
                row.append('')
        row.append(bill)
        return row

    def rows(self):
        for resp in self.response:
            row = self.row(resp["value"])
            if row:
                yield row 

       
def run():
    utility= BidsUtility()
    owner, period, config = parse_args()
    utility.init_from_args(owner, period, config)
    utility.run()
   

if __name__ == "__main__":
    run()
