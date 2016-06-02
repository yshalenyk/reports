import argparse
import iso8601
import requests
import json
import requests_cache


requests_cache.install_cache('exchange_chache')


def get_cmd_parser():
    parser = argparse.ArgumentParser(
        description="Openprocurement Billig"
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
        '-i',
        '--ignore',
        dest='ignore',
        type=argparse.FileType('r'),
        help='File with ids that should be skipped'
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
