import couchdbkit as ckit
import os.path
import csv
import os
import os.path
from couchdbkit.exceptions import ResourceNotFound
from dateparser import parse

import ConfigParser


OWNERS = {
    "smarttender": "it.ua",
    "dzo": "netcast.com.ua",
    "privatmarket": "privatmarket.ua",
    "prom": "prom.ua",
    "etender": "e-tender.biz",
    "publicbid": "public-bid.com.ua",
    "newtend": "newtend.com",
}


def get_config(name):
    config = ConfigParser.ConfigParser()
    config.read(name)
    return config

def get_db(schema, db_name):
    server = ckit.Server(schema)
    try:
        db = server.get_db(db_name)
    except ResourceNotFound:
        print "Database not esists!"
    return db


def get_payment(value, thresholds, payments):
    index = 0
    for th in thresholds:
        if value <= th:
            return payments[index]
        index += 1
    return payments[-1]

def get_response(db, view, startkey='', endkey=''):
    if not startkey:
        return db.view(view).iterator()
    if endkey:
        return db.view(view, startkey=startkey, endkey=endkey).iterator()
    else:
        return db.view(view, startkey=startkey).iterator()

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

def build_thresholds_headers(thold):
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


def get_thesholds(conf):
   return [float(item[1]) for item in conf.items("thresholds")]

def get_payments(conf, rev=False):
    if not rev:
        return [float(item[1]) for item in conf.items("payments_from_emall")]
    else:
        return [float(item[1]) for item in conf.items("payments_to_emall")]


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
