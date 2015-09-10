from os import environ
from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

CASSANDRA_HOSTS = environ.get('CASSANDRA_HOSTS').split(',')
CASSANDRA_KEYSPACE = environ.get('CASSANDRA_KEYSPACE')
CASSANDRA_USER = environ.get('CASSANDRA_USER')
CASSANDRA_PWD = environ.get('CASSANDRA_PWD')
CASSANDRA_PROTOCOL_VERSION = int(environ.get('CASSANDRA_PROTOCOL_VERSION'))
CASSANDRA_QUERY_CONCURRENCY = int(environ.get('CASSANDRA_QUERY_CONCURRENCY'))
CASSANDRA_QUERY_TIMEOUT = int(environ.get('CASSANDRA_QUERY_TIMEOUT'))
TILE_SIZE = int(environ.get('TILE_SIZE'))
LOG_LEVEL = environ.get('LOG_LEVEL')
PROCESS_COUNT = int(environ.get('PROCESS_COUNT'))
