import couchdbkit as ckit
import os.path
import csv
import os
import os.path
from couchdbkit.exceptions import ResourceNotFound

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
    sections = config.sections()
    configs = {}
    for section in sections:
        configs[section] = config.items(section)
    return configs

def get_db(schema, db_name):
    server = ckit.Server(schema)
    try:
        db = server.get_db(db_name)
    except ResourceNotFound:
        print "Database not esists!"
    return db


def get_payment(value, thrasholds, payments):
    index = 0
    for th in thrasholds:
        if value <= th:
            return payments[index]
        index += 1
    return payments[-1]


def write_csv(name, headers, rows):
    with open(name, 'w') as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(headers)
        for row in rows:
            writer.writerow(row)

def build_name(key, start_date, end_date=''):
    if end_date:
        end_date = "--" + end_date
    name = key + "." + start_date + end_date + ".csv"
    if not os.path.exists("release/"):
        os.mkdir("release/")
    return "release/" + name

def build_thr_headers(thold):
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
