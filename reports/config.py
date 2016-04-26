from __future__ import print_function
import appdirs
import os
import os.path
import logging
import sys
from ConfigParser import ConfigParser, NoSectionError, NoOptionError



class Config():

    def __init__(self):
        app_name = 'reports'
        self.dirs = appdirs.AppDirs(app_name)
        self.init_config(app_name)
        self.init_logger(app_name)
        self.get_db_params()

    def init_config(self, app_name):
        conf_path = self.dirs.user_config_dir

        if not os.path.exists(conf_path):
            os.makedirs(conf_path)
        conf_file = os.path.join(self.dirs.user_config_dir, '{}.cfg'.format(app_name))
        if not os.path.exists(conf_file):
            with open(conf_file, 'w'):
                pass
        self.config = ConfigParser()
        self.config.read(conf_file)

    def init_logger(self, name):
        log_path = self.dirs.user_log_dir
        if not os.path.exists(log_path):
            os.makedirs(log_path)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(os.path.join(log_path, '{}.log'.format(name)))
        fh.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s -- %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)

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



    def get_db_params(self):
        db_name = self.get_option('db', 'name') 
        db_schema = self.get_option('db', 'uri')
        db_user = self.get_option('db', 'username')
        db_password = self.get_option('db', 'password')
        return db_name, db_schema, db_user, db_password


    def get_thresholds(self):
        t = self.config.get('payments', 'thresholds')
        return [float(i.strip()) for i in t.split(',')]


    def get_payments(self, rev=False):
        if rev:
            p = self.config.get('payments', "emall")
        else:
            p = self.config.get('payments', "cdb")
        return [float(i.strip()) for i in p.split(',')]

    def get_view(self, name):
        view = self.get_option('views', name)
        return view
        
            
            




   


if __name__ == '__main__':
    config = Config()
        
        
