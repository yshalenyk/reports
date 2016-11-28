import argparse
import iso8601
import requests
import json
import requests_cache
import re


requests_cache.install_cache('exchange_cache')


def get_cmd_parser():
    parser = argparse.ArgumentParser(
        description="Openprocurement Billing"
    )
    report = parser.add_argument_group('Report', 'Report parameters')
    report.add_argument(
        '-c',
        '--config',
        dest='config',
        required=True,
        help="Path to config file. Required"
    )
    report.add_argument(
        '-b',
        '--broker',
        dest='broker',
        required=True,
        help='Broker name. Required'
    )
    report.add_argument(
        '-p',
        '--period',
        nargs='+',
        dest='period',
        default=[],
        help='Specifies period for billing report.\n '
             'By default report will be generated from all database'
    )
    report.add_argument(
        '-t',
        '--timezone',
        dest='timezone',
        default='Europe/Kiev',
        help='Timezone. Default "Europe/Kiev"'
    )
    return parser


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


def create_db_url(host, port, user, passwd, db_name=''):
    up = ''
    if user and passwd:
        up = '{}:{}@'.format(user, passwd)
    url = 'http://{}{}:{}'.format(up, host, port)
    if db_name:
        url += '/{}'.format(db_name)
    return url


class Kind(argparse.Action):

    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):

        self.kinds = set(['general', 'special', 'defense', '_kind'])
        super(Kind, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=self.kinds,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(
            self, parser, args, values, option_string=None):
        options = values.split('=')
        self.parser = parser
        if len(options) < 2:
            parser.error("usage <option>=<kind>")
        action = options[0]
        kinds = options[1].split(',')
        try:
            getattr(self, action)(kinds)
        except AttributeError:
            self.parser.error("<option> should be one from [include, exclude, one]")

        setattr(args, self.dest, self.kinds)

    def include(self, kinds):
        for kind in kinds:
            self.kinds.add(kind)

    def exclude(self, kinds):
        for kind in kinds:
            if kind in self.kinds:
                self.kinds.remove(kind)

    def one(self, kinds):
        for kind in kinds:
            if kind not in ['general', 'special', 'defense', 'other', '_kind']:
                self.parser.error('Allowed only general, special, defense, other and _kind')
        self.kinds = set(kinds)


class Status(argparse.Action):

    def __init__(self,
                 option_strings,
                 dest,
                 nargs=None,
                 const=None,
                 default=None,
                 type=None,
                 choices=None,
                 required=False,
                 help=None,
                 metavar=None):

        self.statuses = {'action': '', 'statuses': set([u'active',
                                                        u'complete',
                                                        u'active.awarded',
                                                        u'cancelled',
                                                        u'unsuccessful'
                                                        ])}
        super(Status, self).__init__(
            option_strings=option_strings,
            dest=dest,
            nargs=nargs,
            const=const,
            default=self.statuses,
            type=type,
            choices=choices,
            required=required,
            help=help,
            metavar=metavar)

    def __call__(
            self, parser, args, values, option_string=None):
        options = values.split('=')
        self.parser = parser
        if len(options) < 2:
            parser.error("usage <option>=<kind>")
        action = options[0]
        statuses = options[1].split(',')
        try:
            getattr(self, action)(statuses)
        except AttributeError:
            self.parser.error("<option> should be one from [include, exclude, one]")

        setattr(args, self.dest, self.statuses)

    def include(self, sts):
        self.statuses['action'] = 'include'
        for status in sts:
            self.statuses['statuses'].add(status)

    def exclude(self, sts):
        self.statuses['action'] = 'exclude'
        for status in sts:
            if status in self.statuses:
                self.statuses['statuses'].remove(status)

    def one(self, sts):
        self.statuses['action'] = 'one'
        self.statuses['statuses'] = set(sts)


def get_operations(name):
    words = re.findall(r'\w+', name)
    return [w for w in words
            if w in ['bids', 'invoices', 'refunds', 'tenders']]


def get_send_args_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-c',
        '--config',
        dest='config',
        required=True,
        help='Path to configuration file'
    )
    parser.add_argument(
        '-f',
        '--file',
        nargs='+',
        dest='files',
        help='Files to send'
    )
    parser.add_argument(
        '-n',
        '--notify',
        action='store_true',
        help='Notification flag'
    )
    parser.add_argument(
        '-e',
        '--exists',
        action='store_true',
        help='Send mails from existing directory; timestamp required'
    )
    parser.add_argument(
        '-t',
        '--timestamp',
        help='Initial run timestamp'
    )
    parser.add_argument(
        '-b',
        '--brokers',
        nargs='+',
        help='Recipients'
    )
    parser.add_argument(
        '-i',
        '--include',
        nargs='+',
        help='Filetype f'
    )

    return parser
