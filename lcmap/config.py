from os import environ
from os.path import join, dirname
from dotenv import load_dotenv
load_dotenv('.env')

CASSANDRA_HOSTS = environ.get('CASSANDRA_HOSTS', ['localhost']).split(',')
CASSANDRA_PORT = int(environ.get('CASSANDRA_PORT', 9042))
CASSANDRA_KEYSPACE = environ.get('CASSANDRA_KEYSPACE', 'lcmap')
CASSANDRA_USER = environ.get('CASSANDRA_USER', None)
CASSANDRA_PASS = environ.get('CASSANDRA_PASS', None)
CASSANDRA_PROTOCOL_VERSION = int(environ.get('CASSANDRA_PROTOCOL_VERSION','4'))
CASSANDRA_QUERY_CONCURRENCY = int(environ.get('CASSANDRA_QUERY_CONCURRENCY','100'))
CASSANDRA_QUERY_TIMEOUT = int(environ.get('CASSANDRA_QUERY_TIMEOUT','5000'))

LOG_LEVEL = environ.get('LOG_LEVEL')
