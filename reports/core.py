import couchdb
import couchdb.design
import os.path
import csv
import os
import os.path
import requests
import requests_cache
import json
import iso8601
import arrow
import time
from dateutil.parser import parse
from config import Config, create_db_url
from design import bids_owner_date, tenders_owner_date
from argparse import ArgumentParser
from couchdb.design import ViewDefinition
from logging import getLogger


views = [bids_owner_date, tenders_owner_date]

requests_cache.install_cache('exchange_chache')


class BaseUtility(object):

    def __init__(self, operation, rev=False):
        self.rev = rev
        self.headers = None
        self.operation = operation

    def initialize(self, owner, period, config, ignored=set(), tz=''):
        self.owner = owner
        self.config = Config(config, self.rev)
        self.start_date = ''
        self.end_date = ''
        self.ignored_list = ignored
        self.timezone = tz

        if period:
            if len(period) == 1:
                self.start_date = self.convert_date(period[0])
            if len(period) == 2:
                self.start_date = self.convert_date(period[0])
                self.end_date = self.convert_date(period[1])
        self.get_db_connection()
        self.Logger = getLogger(self.operation)

    def get_db_connection(self):
        host = self.config.get_option('db', 'host')
        port = self.config.get_option('db', 'port')
        user_name = self.config.get_option('user', 'username')
        user_password = self.config.get_option('user', 'password')

        db_name = self.config.get_option('db', 'name')

        self.db = couchdb.Database(
            create_db_url(host, port, user_name, user_password, db_name)
        )

        a_name = self.config.get_option('admin', 'username')
        a_password = self.config.get_option('admin', 'password')
        self.adb = couchdb.Database(
            create_db_url(host, port, a_name, a_password, db_name)
        )

    def row(self):
        raise NotImplemented

    def rows(self):
        raise NotImplemented

    def convert_date(self, date):
        if len(date) < 3:
            date = time.strftime("%Y-%m-") + date
        date = arrow.get(parse(date), self.timezone)
        res = date.to('UTC').strftime("%Y-%m-%dT%H:%M:%S.%f")
        return res

    def get_payment(self, value):
        for index, threshold in enumerate(self.config.thresholds):
            if value <= threshold:
                return self.config.payments[index]
        return self.config.payments[-1]

    def _sync_views(self):
        ViewDefinition.sync_many(self.adb, views)

    def get_response(self):
        self._sync_views()

        if not self.view:
            raise NotImplemented

        if not self.start_date and not self.end_date:
            self.response = self.db.iterview(
                self.view, 1000,
                startkey=(self.owner, ""),
                endkey=(self.owner, "9999-12-30T00:00:00.000000")
            )
        elif self.start_date and not self.end_date:
            self.response = self.db.iterview(
                self.view, 1000,
                startkey=(self.owner, self.start_date),
                endkey=(self.owner, "9999-12-30T00:00:00.000000")
            )
        else:
            self.response = self.db.iterview(
                self.view, 1000,
                startkey=(self.owner, self.start_date),
                endkey=(self.owner, self.end_date)
            )

    def out_name(self):
        start = ''
        end = ''
        if self.start_date:
            start = arrow.get(parse(self.start_date)).to('Europe/Kiev').strftime("%m-%d")
        if self.end_date:
            end = arrow.get(parse(self.end_date)).to('Europe/Kiev').strftime("%m-%d")
        name = "{}@{}--{}-{}.csv".format(
            self.owner,
            start,
            end,
            self.operation
        )
        self.put_path = os.path.join(self.config.out_path, name)

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


def thresholds_headers(cthresholds):
    prev_threshold = None
    result = []
    thresholds = [str(t / 1000) for t in cthresholds]
    for t in thresholds:
        if not prev_threshold:
            result.append("<= " + t)
        else:
            result.append(">" + prev_threshold + "<=" + t)
        prev_threshold = t
    result.append(">" + thresholds[-1])
    return result


def parse_args():
    parser = ArgumentParser()
    parser.add_argument('-o', '--owner', dest='owner', required=True)
    parser.add_argument(
        '-c', '--config', dest='config',
        required=False,
        default='~/.config/reports/reports.ini'
    )
    parser.add_argument('-p', '--period', nargs='+', dest='period', default=[])
    parser.add_argument('-i', '--ignored', dest='ignored')
    parser.add_argument(
        '-t',
        '--timezone',
        dest='timezone',
        default='Europe/Kiev'
    )
    args = parser.parse_args()
    if args.ignored and os.path.exists(args.ignored):
        with open(args.ignored) as ignore_f:
            ignored_list = set(unicode(line.strip('\n')) for line in ignore_f)
    else:
        ignored_list = set()
    return (args.owner.strip(), args.period,
            args.config, ignored_list, args.timezone)


def value_currency_normalize(value, currency, date):
    if not isinstance(value, (float, int)):
        raise ValueError
    base_url = 'http://bank.gov.ua/NBUStatService'\
        '/v1/statdirectory/exchange?date={}&json'.format(
            iso8601.parse_date(date).strftime('%Y%m%d')
        )
    resp = requests.get(base_url).text.encode('utf-8')
    doc = json.loads(resp)
    if currency == u'RUR':
        currency = u'RUB'
    rate = filter(lambda x: x[u'cc'] == currency, doc)[0][u'rate']
    return value * rate, rate
