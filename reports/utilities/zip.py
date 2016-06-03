import pyminizip
import argparse
import os.path
import ConfigParser


def get_argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', dest='files', nargs='+', required=True)
    parser.add_argument('-c', dest='config', required=True)
    return parser


def run():
    parser = get_argument_parser()
    args = parser.parse_args()
    config = ConfigParser.ConfigParser()
    config.read(args.config)
    passwords = dict(config.items('passwords'))
    owner = os.path.basename(args.files[0].split('@')[0])
    operations = [os.path.basename(f).split('-')[-1].split('.')[0]
                  for f in args.files]
    pyminizip.compress_multiple(
        args.files,
        '{}-{}.zip'.format(owner, '-'.join(operations)),
        passwords[owner],
        4
    )
