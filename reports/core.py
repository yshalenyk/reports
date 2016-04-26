import couchdbkit
#import couchdb
import os.path
import csv
import os
import os.path
import click
from restkit import BasicAuth
from config import Config
from couchdbkit.exceptions import ResourceNotFound
from dateparser import parse
from ConfigParser import NoSectionError



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
        self.config = Config()
        self.operation = operation
        name, uri, user, passwd = self.config.get_db_params()

        if user and passwd:
            resource = couchdbkit.resource.CouchdbResource(filters=[BasicAuth(user, passwd)])
            self.server = couchdbkit.Server(uri, resource_instance=resource)
        else:
            self.server = couchdbkit.Server(uri)
        self.get_db(name)
        self.thresholds = self.config.get_thresholds()
        self.payments = self.config.get_payments(self.rev)
        self.view = 'reports/bids'


    def get_db(self, db_name):
        try:
            db = self.server.get_db(db_name)
        except ResourceNotFound:
            self.config.logger.info("Database not esists!")
            raise
        self.db = db
        

    def get_payment(self, value):
        index = 0
        for th in self.thresholds:
            if value <= th:
                return self.payments[index]
            index += 1
        return self.payments[-1]

    def get_response(self, startkey='', endkey=''):
        if not startkey:
            self.response = self.db.view(self.view).iterator()
        if endkey:
            self.response =self.db.view(self.view, startkey=startkey, endkey=endkey).iterator()
        else:
            self.response = self.db.view(self.view, startkey=startkey).iterator()


#class BaseDateParamType(click.ParamType):
#    name = 'date'
#
#    def convert(self, value, param, ctx) :
#        try:
#            #date1, date2 = value.split()
#            #return (parse(date1.strip()), parse(date2.strip()))
#            return parse(value)
#        except ValueError:
#            self.fail('{} is not a valid date'.format(value))
#
#class ListType(click.CompositeParamType):
#    name = 'date'
#
#    def convert(self, value, param, ctx) :
#        try:
#            #date1, date2 = value.split()
#            #return (parse(date1.strip()), parse(date2.strip()))
#            return parse(value)
#        except ValueError:
#            self.fail('{} is not a valid date'.format(value))




def write_csv(name, headers, rows):
    with open(name, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)


def build_name(key, start_key, end_key, procedure):
    if end_key:
        end_date = "--" + end_key[1]
    else:
        end_date = ''
    if start_key:
        start_date = start_key[1]
    name = key + "." + start_date + end_date +"-"+ procedure+ ".csv"
    if not os.path.exists("release/"):
        os.mkdir("release/")
    return "release/" + name

def thresholds_headers(thold):
    prev_th = None
    result = []
    thrash = []
    for i in thold:
        thrash.append(str(i/1000))
    for th in thrash:
        if not prev_th:
            result.append("<= " + th)
        else:
            result.append(">" + prev_th + "<=" + th)
        prev_th = th
    result.append(">" + thrash[-1])
    return result



def parse_args(args):
    endkey = []
    if len(args.d) > 2:
        raise Exception
    key = args.o.strip()
    if key in OWNERS:
        owner = OWNERS[key]
    elif key in OWNERS.values():
        owner = key
    else:
        raise Exception
    startdate = parse(args.d[0]).isoformat()
    if len(args.d) > 1:
        enddate = parse(args.d[1]).isoformat()
        endkey = [owner, enddate]
    else:
        enddate = ''
    startkey = [owner, startdate]
    return owner, startkey, endkey
