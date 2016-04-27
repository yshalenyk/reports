import couchdb
import couchdb.design
import os.path
import csv
import os
import os.path
from design import bids_view
from config import Config
from design import bids
from argparse import ArgumentParser
from dateparser import parse
from couchdb.http import ResourceNotFound
from couchdb.design import ViewDefinition


views = [bids_view]


OWNERS = {
    "smarttender": "it.ua",
    "dzo": "netcast.com.ua",
    "privatmarket": "privatmarket.ua",
    "prom": "prom.ua",
    "etender": "e-tender.biz",
    "publicbid": "public-bid.com.ua",
    "newtend": "newtend.com",
}



class ReportUtility():

    def __init__(self, operation, rev=False):
        self.rev = rev
        self.headers = None
        self.operation = operation
    def init_from_args(self, owner, period, config=None):
        if owner in OWNERS:
            self.owner = OWNERS[owner]
        else:
            self.owner = owner
        self.owner = OWNERS[owner]
        self.config = Config(config)
        if len(period) != 2:
            raise ValueError('Invalid period')
        self.start_date = parse(period[0]).isoformat()
        self.end_date = parse(period[1]).isoformat()
        name, uri = self.config.get_db_params()
        self.server = couchdb.Server(uri)
        if name not in self.server:
            raise Exception('Database not exists')
        self.db = self.server[name]
        self.thresholds = self.config.get_thresholds()
        self.payments = self.config.get_payments(self.rev)
        self.view = 'report/bids'



    def row(self):
        raise NotImplemented

    def rows(self):
        raise NotImplemented


    def get_payment(self, value):
        index = 0
        for th in self.thresholds:
            if value <= th:
                return self.payments[index]
            index += 1
        return self.payments[-1]

    def _sync_views(self):
        ViewDefinition.sync_many(self.db, views)
        
        

    def get_response(self):
        self._sync_views()
        self.response = self.db.view(self.view,
                                     startkey=[self.owner, self.start_date],
                                     endkey=[self.owner, self.end_date])

            

    def out_name(self):
        name = self.owner + "@" + self.start_date + "--" \
               + self.end_date +"-"+ self.operation+ ".csv"

        self.put_path = os.path.join(self.config.get_out_path(), name)

    def write_csv(self):
        if not self.headers:
            raise ValueError
        with open(self.put_path, 'w') as out_file:
            writer = csv.writer(out_file)
            writer.writerow(self.headers)
            for row in self.rows():
                writer.writerow(row)

    def run(self):
        self.get_response()
        self.out_name()
        self.write_csv()






def thresholds_headers(thresholds):
    prev_threshold = None
    result = []
    threshold = []
    for t in thresholds:
        threshold.append(str(t/1000))
    for t in threshold:
        if not prev_threshold:
            result.append("<= " + t)
        else:
            result.append(">" + prev_threshold + "<=" + t)
        prev_threshold = t
    result.append(">" + threshold[-1])
    return result

def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-o', '--owner', dest='owner',  required=True)
    parser.add_argument('-c', '--config', dest='config', required=False, default='~/.config/reports/reports.ini')
    parser.add_argument('-p', '--period', nargs='+', dest='period')
    args = parser.parse_args()
    return args.owner.strip(), args.period, args.config
   
