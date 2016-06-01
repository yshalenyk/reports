import yaml
import requests
import requests_cache
from reports.core import (
    BaseUtility,
    parse_args,
    value_currency_normalize
)
from requests.exceptions import RequestException
from yaml.scanner import ScannerError

requests_cache.install_cache('audit_cache')


class BidsUtility(BaseUtility):

    def __init__(self):
        super(BidsUtility, self).__init__('bids')
        self.headers = [u"tender", u"tenderID", u"lot",
                        u"value", u"currency", u"bid", u'rate', u"bill"]
        self.view = 'report/bids_owner_date'
        self.skip_bids = set()

    def bid_date_valid(self, bid_id, audit):
        if bid_id in self.skip_bids or not audit:
            self.Logger.info('Skipped cached early bid: %s', bid_id)
            return False
        try:
            yfile = yaml.load(
                requests.get(self.config.api_url + audit['url']).text
            )
            initial_bids = yfile['timeline']['auction_start']['initial_bids']
            for bid in initial_bids:
                if bid['date'] < "2016-04-01":
                    self.skip_bids.add(bid['bidder'])
        except RequestException as e:
            msg = 'Request falied at getting audit file'\
                'of {0}  bid with {1}'.format(bid_id, e)
            self.Logger.error(msg)
        except ScannerError:
            msg = 'falied to scan audit file of {} bid'.format(bid_id)
            self.Logger.error(msg)
        except KeyError:
            msg = 'falied to parse audit file of {} bid'.format(bid_id)
            self.Logger.error(msg)

        if bid_id in self.skip_bids:
            self.Logger.info('Skipped fetched early bid: %s', bid_id)
            return False
        return True

    def row(self, record):
        bid = record.get(u'bid', '')
        rate = None
        if record.get('tender_start_date', '') < "2016-04-01" and \
                not self.bid_date_valid(bid, record.get(u'audits', '')):
            return
        row = list(record.get(col, '') for col in self.headers[:-2])
        value = float(record.get(u'value', 0))
        if record[u'currency'] != u'UAH':
            old = value
            value, rate = value_currency_normalize(
                value, record[u'currency'], record[u'startdate']
            )
            msg = "Changed value {} {} by exgange rate {} on {}"\
                " is  {} UAH in {}".format(
                    old, record[u'currency'], rate,
                    record[u'startdate'], value, record['tender']
                )
            self.Logger.info(msg)
        r = str(rate) if rate else ''
        row.append(r)
        row.append(self.get_payment(value))
        self.Logger.info(
            "Bill {} for tender {} with value {}".format(
                row[-1], row[0], value
            )
        )
        return row

    def rows(self):
        for resp in self.response:
            row = self.row(resp["value"])
            if row:
                yield row


def run():
    utility = BidsUtility()
    owner, period, config, ignored, tz = parse_args()
    utility.initialize(owner, period, config, ignored, tz)
    utility.run()


if __name__ == "__main__":
    run()
