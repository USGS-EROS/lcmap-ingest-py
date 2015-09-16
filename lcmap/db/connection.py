"""
   connection.py

   Manage connections to a Cassandra cluster.

   This module uses environment variables:

   CASSANDRA_HOSTS: comma separated list of hosts to connect
   CASSANDRA_KEYSPACE: LCMAP by default
   CASSANDRA_QUERY_CONCURRENCY: Integer, 100 by default
   CASSANDRA_PROTOCOL_VERSION: Integer, 4 by default

   You may optionally include authentication options. If you omit them,
   then an auth provider will not be used. Only the PlainTextAuthProvider
   is supported.

   CASSANDRA_USER: None by default
   CASSANDRA_PASS: None by default

"""

from cassandra import ConsistencyLevel
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.policies import RetryPolicy
from lcmap import config


import logging
logger = logging.getLogger()


def get_auth():
    if config.CASSANDRA_USER and config.CASSANDRA_PASS:
        return PlainTextAuthProvider(username=config.CASSANDRA_USER, password=config.CASSANDRA_PASS)

def get_retry():
    return RetryPolicy()

def get_version():
    return config.CASSANDRA_PROTOCOL_VERSION

def get_hosts():
    return config.CASSANDRA_HOSTS

def get_cluster():
    return Cluster(config.CASSANDRA_HOSTS,
                   compression=True,
                   protocol_version=get_version(),
                   default_retry_policy=get_retry(),
                   auth_provider=get_auth())

def get_session(cluster):
    return get_cluster().connect(config.CASSANDRA_KEYSPACE)

cluster = get_cluster()

session = get_session(cluster)
