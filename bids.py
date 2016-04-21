from utils import *
import couchdbkit as ckit
import argparse
import datetime
from dateparser import parse
VIEW = "reports/bids"

HEADERS = ["tender", "lot", "value", "bid", "bill"]

conf = get_config("config.cfg")
db_schema = "http://" + conf["db"][0][1]
db_name = conf["db"][1][1]


def build_row(rec):
    row = []
    record = rec["value"]
    row.append(record["tender"])
    try:
           row.append(record["lot"])
    except KeyError:
           row.append("--")
    value = record["value"]
    row.append(value)
    row.append(record["bid"])
    th = [float(item[1]) for item in conf["thrasholds"]]
    paymens = [float(item[1]) for item in conf["payments_from_emall"]]
    row.append(get_payment(float(value), th, paymens))
    return row

def rows(response):
    for resp in response:
        yield build_row(resp)






if __name__ == "__main__":
    enddate = ''
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", type=str, required=True, help="owner")
    parser.add_argument("-d", nargs="+",required=True,  help="dates")
    args = parser.parse_args()
    if len(args.d) > 2:
        raise Exception()
    db = get_db(db_schema, db_name)
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
    startkey = [owner, startdate]
    if enddate:
        endkey = [owner, enddate]
        resp =  db.view("reports/bids", startkey=startkey, endkey=endkey).iterator()
        name = build_name(owner, startdate, enddate)
    else:
        resp =  db.view("reports/bids", startkey=startkey).iterator()
        name = build_name(owner, startdate)
    write_csv(name, HEADERS, rows(resp))

