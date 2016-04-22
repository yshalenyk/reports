from utils import *
import couchdbkit as ckit
import argparse
import datetime
from dateparser import parse
from collections import Counter
VIEW = "reports/bids"

HEADERS = ["tender", "lot", "value", "bid", "bill"]

conf = get_config("config.cfg")
db_schema = "http://" + conf["db"][0][1]
db_name = conf["db"][1][1]

db = get_db(db_schema, db_name)

th = [float(item[1]) for item in conf["thrasholds"]]
headers = build_thr_headers(th)
paymens = [float(item[1]) for item in conf["payments_from_emall"]]
counter = [0 for _ in xrange(len(paymens))]



def count_row(rec):
    record = rec["value"]
    value = record["value"]
    payment = get_payment(value, th, paymens)
    for i, x in enumerate(paymens):
        if payment == x:
            counter[i] += 1
def build_rows():
    rows = [counter, paymens]
    row = []
    for c, v in zip(counter, paymens):
        row.append(c*v)
    rows.append(row)
    return rows





if __name__ == "__main__":
    enddate = ''
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", type=str, required=True, help="owner")
    parser.add_argument("-d", nargs="+",required=True,  help="dates")
    args = parser.parse_args()
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
    c = 0
    for row in resp:
        count_row(row)
        c += 1
    print c
    rows = build_rows()
    write_csv(name, headers, rows)

