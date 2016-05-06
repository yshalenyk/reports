from core import *
import sys
import yaml
import requests
import requests_cache
import logging

Logger = logging.getLogger(__name__)
requests_cache.install_cache('audit_cache')

class BidsUtility(ReportUtility):

    def __init__(self):
        ReportUtility.__init__(self, 'bids')
        self.headers = [u"tender", u"lot", u"value", u"currency", u"bid", u"bill"]
        self.view = 'report/bids_owner_date'
        self.skip_bids = set()

    def bid_date_valid(self, bid_id, audit):
        if bid_id in self.skip_bids or not audit:
            self.config.logger.info('Skipped cached early bid: %s', bid_id)
            return False
        try:
            yfile = yaml.load(requests.get(self.api_url + audit['url']).text)
            initial_bids = yfile['timeline']['auction_start']['initial_bids']
            for bid in initial_bids:
                if bid['date'] < "2016-04-01":
                    self.skip_bids.add(bid['bidder'])
        except Exception as e:
            self.config.logger.error('falied to parse audit file of %s bid', bid_id)

        if bid_id in self.skip_bids:
            self.config.logger.info('Skipped fetched early bid: %s', bid_id)            
            return False
        return True

    def row(self, record):
        bid = record.get(u'bid', '')
        if record.get('tender_start_date', '') < "2016-04-01" and \
                not self.bid_date_valid(bid, record.get(u'audits', '')):
            return
        row = list(record.get(col) for col in self.headers[:-1])
        row.append(self.get_payment(float(record.get(u'value', 0))))
        return row

    def rows(self):
        for resp in self.response:
            row = self.row(resp["value"])
            if row:
                yield row

def run():
    utility = BidsUtility()
    owner, period, config = parse_args()
    utility.init_from_args(owner, period, config)
    utility.run()


if __name__ == "__main__":
    run()
