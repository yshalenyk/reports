from utils import *
import couchdbkit as ckit
import argparse
import datetime
from dateparser import parse



VIEW = "reports/bids"

HEADERS = ["tender", "value", "bill"]

conf = get_config("config.cfg")
db_schema = "http://" + conf.get("db", "schema")
db_name = conf.get("db", "name")

db = get_db(db_schema, db_name)
thresholds = get_thesholds(conf) 
paymens = get_payments(conf, rev=True)

tenders_set = set()


def build_row(rec):
    row = []
    record = rec["value"]
    id = record["tender"]
    if "lot" in record:
        return None
    if id  not in tenders_set:
        tenders_set.add(id)
        row.append(id)
        value= record["value"]
        row.append(value)
        row.append(get_payment(float(value), thresholds, paymens))
        return row
    else:
        return None

def rows(response):
    for resp in response:
        row = build_row(resp)
        if row:
            yield row







if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-o", type=str, required=True, help="owner")
    parser.add_argument("-d", nargs="+",required=True,  help="dates")
    args = parser.parse_args()
    owner, startkey, endkey = parse_args(args)
    response = get_response(db ,VIEW, startkey, endkey)
    name = build_name(owner, startkey, endkey, "tenders")
    write_csv(name, HEADERS, rows(response))

