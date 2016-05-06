from ConfigParser import ConfigParser, NoSectionError, NoOptionError
import logging
import logging.handlers
from logging.config import fileConfig


class Config(object):

    def __init__(self, path):
        self.config = ConfigParser()
        self.config.read(path)
        self.init_logger(path)

    def init_logger(self, file_path):
        fileConfig(file_path)
        self.logger = logging.getLogger()

    def get_option(self, section, name):
        try:
            opt = self.config.get(section, name)
        except NoSectionError:
            print("No section {} in configuration file".format(section))
            sys.exit(1)
        except NoOptionError:
            print("No option {} in configuration file".format(name))
            sys.exit(1)
        return opt

    def get_api_url(self):
        host = self.get_option('api', 'host')
        ver = self.get_option('api', 'version')
        url = host + '/api/{}'.format(ver)
        return url

    def get_thresholds(self):
        t = self.config.get('payments', 'thresholds')
        return [float(i.strip()) for i in t.split(',')]

    def get_payments(self, rev=False):
        if rev:
            p = self.config.get('payments', "emall")
        else:
            p = self.config.get('payments', "cdb")
        return [float(i.strip()) for i in p.split(',')]

    def get_out_path(self):
        return self.get_option('out', 'out_dir')


def create_db_url(host, port, user, passwd, db_name=''):
    if user and passwd:
        up = user + ':' + passwd + '@'
    else:
        up = ''
    url = 'http://' + up + host + ':' + port
    if db_name:
        url += '/{}'.format(db_name)
    return url


if __name__ == '__main__':
    print create_db_url('127.0.0.1', '5984', '', '')
