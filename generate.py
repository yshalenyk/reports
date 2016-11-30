import argparse
import subprocess as sbp
import os.path import itertools
import csv
import os
import logging
from ConfigParser import ConfigParser
from logging.handlers import RotatingFileHandler
from subprocess import PIPE
from datetime import date
from os.path import join as _join
from datetime import datetime
from copy import copy


CONFIG = ConfigParser()
CONFIG.read('etc/reports.ini')


BASE_PATH = os.path.abspath(os.path.dirname(__file__))
WORK_PATH = _join(BASE_PATH, 'var', 'reports')
ZIP_PATH = CONFIG.get('zip', 'zip_path')
RUN_TIME = datetime.now().strftime('%Y-%m-%d/%H-%M-%S-%f')
NOTIFY_ON = 'bids-invoices'
BROKERS = dict(CONFIG.items('brokers_emails')).keys()

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.DEBUG)

hd = RotatingFileHandler('var/log/generate.log', maxBytes=1024*1024*1024)
ft = logging.Formatter('%(asctime)s - %(message)s')
hd.setFormatter(ft)

LOGGER.addHandler(hd)
LOGGER.debug("test message")


scripts = ['bids', 'invoices', 'tenders', 'refunds']


def generation_period():
    end = date.today().replace(day=1)
    if end.month == 1:
        start = end.replace(year=end.year-1, month=12, day=1)
    else:
        start = end.replace(month=end.month-1, day=1)
    return start.strftime('%Y-%m-%d'), end.strftime('%Y-%m-%d')


def generate_for_broker(broker, startdate, enddate, exclude=''):
    cmds = []
    for job in scripts:
        args = [script(job), '-b', broker, '-p', startdate, enddate]
        if exclude and job in ['tenders', 'refunds']:
            iargs = args
            iargs.extend(['-i', exclude])
            cmds.append(iargs)
        else:
            cmds.append(args)
    ps = [Popen(cmd) for cmd in cmds]
    for p in ps:
        p.wait()


def create_all_bids(brokers, start, end):
    with open(_join(WORK_PATH, 'all@{}--{}-bids.csv'.format(start, end))):
        pass

    for broker in brokers:
        name = '{}@{}--{}-bids.csv'.format(broker, start, end)
        file_path = _join(WORK_PATH, name)
        started = False

        try:
            with open(file_path) as part_csv:
                reader = csv.reader(part_csv)
                header = next(reader)
                all_file_name = 'all@{}--{}-bids.csv'.format(start, end)
                with open(_join(WORK_PATH, all_file_name), 'a+')\
                        as all_bids_csv:
                    writer = csv.writer(all_bids_csv)
                    if not started:
                        writer.writerow(header)
                        started = True

                    for row in reader:
                        writer.writerow(row)
            log('Created {}'.format(name))
        except (OSError, IOError) as e:
            log('Failed to create all bids for {}'
                ' -- {}. Error {}'.format(start, end, e))


def create_all_tenders_zip(brokers, start, end):
    zname = 'all@{}--{}-tenders-refunds.zip'.format(start, end)
    cmd = [
        script('zip'),
        '-z', zname,
        '-f'
    ]
    cmd.extend([
        _join(WORK_PATH, 'var', 'reports', file)
        for file in ['{}@{}--{}-{}.csv'.format(broker, start, end, t)
                     for t in ['tenders', 'refunds']
                     for broker in brokers]
    ])
    pzip = sbp.Popen(cmd, stdout=PIPE, stderr=PIPE)
    out, err = pzip.communicate()
    if err:
        log('Error during creating all tenders archive')


def create_all_bids_zip(brokers, start, end):
    zname = 'all@{}--{}-bids.zip'.format(start, end)
    bname = 'all@{}--{}-bids.csv'.format(start, end)
    cmd = [
        script('zip'),
        '-z', zname,
        '-f', _join(WORK_PATH, bname)
    ]
    for broker in brokers:
        iname = '{}@{}--{}-invoices.csv'.format(broker, start, end)
        cmd.append(_join(WORK_PATH, iname))
    pzip = sbp.Popen(cmd, stdout=PIPE, stderr=PIPE)
    out, err = pzip.communicate()
    if err:
        log('Error during creating zip archive with all bids')


def upload_and_notify(broker, start, end, time, notify=False, exists=False):
    # TODO: functionalliti is not full
    # all files:
    #           all@$start--$end-bids-invoices.zip;
    #           all@$start--$end-tenders-refunds.zip

    base_cmd = [script('send'), '--timestamp', time]
    if exists:
        base_cmd.append('-e')
    else:
        base_cmd.append('-f')
    if broker == 'all':
        cmd = copy(base_cmd)
        bids_file = 'all@{}--{}-{}.zip'.format(start, end, 'bids')
        tenders_file = 'all@{}--{}-{}.zip'.format(
            start, end, 'tenders-refunds'
        )
        cmd.extend([_join(WORK_PATH, bids_file), _join(WORK_PATH, tenders_file)])

        if notify:
            cmd.append('-n')
        sender = sbp.Popen(cmd, stdout=PIPE, stdin=PIPE)
        out, err = sender.communicate()
        if err:
            log('Falied to send files')
        else:
            log('Successfuly sent files to s3')

    else:
        if not exists:
            cmds = []
            for file in zip_names(broker, start, end):
                cmd = copy(base_cmd)
                cmd.append(_join(WORK_PATH, file))
                if notify and notify_match(broker, start, end, file):
                    cmd.append('-n')
                cmds.append(cmd)
            ps = [sbp.Popen(cmd, stdout=PIPE, stdin=PIPE) for cmd in cmds]
            for p in ps:
                p.wait()
        else:
            cmd = copy(base_cmd)
            if notify:
                cmd.append('-n')
            cmd.extend(['--include', NOTIFY_ON])
            sender = sbp.Popen(cmd, stdout=PIPE, stdin=PIPE)
            out, err = sender.communicate()
            if err:
                log('Falied to send files')
            else:
                log('Successfuly sent files to s3')


def notify_match(broker, start, end, file):
    if '{}@{}--{}-{}.zip'.format(
            broker, start, end, NOTIFY_ON) == file:
        return True
    return False


def zip_names(broker, start, end):
    return [
        '{}@{}--{}-{}.zip'.format(broker, start, end, '-'.join(ops))
        for ops in
        file_combination()
    ]


def get_password_for(broker, path):
    return sbp.check_output(['pass', _join(ZIP_PATH, broker)])


def clean_up(brokers, start, end):
    if 'all' not in brokers:
        brokers.append('all')

    for broker in brokers:
        file_prefix = '{}@{}--{}'.format(broker, start, end)
        log('Running clean up on {}'.format(broker))
        for file in os.listdir(WORK_PATH):
            if file.startswith(file_prefix):
                try:
                    os.remove(_join(WORK_PATH, file))
                    LOGGER.info('Deleted {}'.format(file))
                except (IOError, OSError) as e:
                    msg = 'Falied to remove {}. Error: {}'.format(file, e)
                    log(msg)


def create_archives(broker, start, end):

    def csv_names(broker, start, end, ops):
        return ['{}@{}--{}-{}.csv'.format(broker, start, end, op)
                for op in ops]

    for ops in file_combination():
        zname = '{}@{}--{}-{}.zip'.format(
            broker, start, end, '-'.join(ops)
        )
        files = [_join(WORK_PATH, c)
                 for c in csv_names(broker, start, end, ops)]
        args = [script('zip'), '-z', zname, '-f']
        args.extend(files)
        if 'bids' in ops:
            password = get_password_for(broker, ZIP_PATH)
            args.extend(['-p', password])
        pzip = sbp.Popen(args, stdout=PIPE, stdin=PIPE)
        out, err = pzip.communicate()
        if pzip.returncode != 0 or err:
            log('Falied to create archive with {} for {}'.format(ops, broker))


def file_combination():
    for r in xrange(1, len(scripts) + 1):
        for ops in itertools.combinations(scripts, r):
            yield ops


def script(name):
    return _join(BASE_PATH, 'bin', name)


def parse_args():
    parser = argparse.ArgumentParser()

    # parser.add_argument('-c', '--config', required=True, help='Path to config file')
    parser.add_argument('--exclude', help='Path to exclude file')
    parser.add_argument('--brokers', nargs='+', help='Brokers to generate')
    parser.add_argument('--period', nargs='+', help='Period for generated report')
    parser.add_argument('--include', nargs='+', help='file content')
    parser.add_argument('--notify', action='store_true', default=False, help='Notification flag')
    parser.add_argument('--timestamp', help='s3 folder')
    parser.add_argument('--notify-brokers', nargs='+', help='brokers to notify')
    return parser.parse_args()


def log(msg, stdout=False):
    LOGGER.info(msg)
    if stdout:
        print msg


def run():
    args = parse_args()
    global NOTIFY_ON
    global BROKERS
    if args.period:
        start = args.period[0]
        end = args.period[1]
    else:
        start, end = generation_period()

    if args.brokers:
        BROKERS = args.brokers
    if args.include:
        NOTIFY_ON = '-'.join([op for op in scripts
                              if op in args.include])
    r = RUN_TIME
    exists = False
    if args.timestamp:
        r = args.timestamp
        exists = True

    for broker in BROKERS:
        if broker != 'all':
            if not exists:
                generate_for_broker(broker, start, end)
                create_archives(broker, start, end)
            upload_and_notify(broker, start, end, time=r,
                              notify=args.notify, exists=exists)

    create_all_bids(BROKERS, start, end)
    create_all_bids_zip(BROKERS, start, end)
    create_all_tenders_zip(BROKERS, start, end)
    if 'all' in BROKERS:
        upload_and_notify('all', start, end, time=r,
                          notify=args.notify, exists=exists)
    clean_up(BROKERS, start, end)


if __name__ == '__main__':
    run()
