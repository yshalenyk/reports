from pkg_resources import resource_stream

config_file = "config.cfg"
config = resource_stream(__name__, config_file)

