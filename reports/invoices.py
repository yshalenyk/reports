from utils import *
import couchdbkit as ckit
import argparse
import datetime
from dateparser import parse


VIEW = "reports/bids"


conf = get_config("config.cfg")
db_schema = "http://" + conf.get("db", "schema")
db_name = conf.get("db", "name")

db = get_db(db_schema, db_name)

thresholds = get_thesholds(conf)
headers = build_thresholds_headers(thresholds)
paymens = get_payments(conf)
counter = [0 for _ in xrange(len(paymens))]



def count_row(rec):
    record = rec["value"]
    value = record["value"]
    payment = get_payment(value, thresholds, paymens)
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
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", type=str, required=True, help="owner")
    parser.add_argument("-d", nargs="+",required=True,  help="dates")
    args = parser.parse_args()

    owner, startkey, endkey = parse_args(args)
    response = get_response(db, VIEW, startkey, endkey)
    name = build_name(owner, startkey, endkey, "invoices")
    for row in response:
        count_row(row)
    rows = build_rows()
    write_csv(name, headers, rows)

