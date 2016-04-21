import couchdbkit as ckit
import os.path
from couchdbkit.exceptions import ResourceNotFound
import ConfigParser


OWNERS = {
    "smarttender": "it.ua",
    "dzo": "netcast.com.ua",
    "privatmarket": "privatmarket.ua",
    "prom": "prom.ua",
    "etender": "e-tender.biz",
    "publicbid": "public-bid.com.ua",
    "newtend": "newtend.com",
}


def get_config(name):
    config = ConfigParser.ConfigParser()
    config.read(name)
    sections = config.sections()
    configs = {}
    for section in sections:
        configs[section] = config.items(section)
    return configs

def get_db(server, db_name):
    try:
        db = server.get_db(db_name)
    except ResourceNotFound:
        print "Database not esists!"
    return db

def get_server(schema):
    server = ckit.Server(schema)
    return server


def get_response(view_name,*args, **kwargs):
    return  db.view(view_name, args=args, kwargs=kwargs)


