from os.path import join, dirname
from dotenv import load_dotenv
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

import os
CASSANDRA_HOSTS = [os.environ.get("CASSANDRA_HOSTS")]
CASSANDRA_KEYSPACE = os.environ.get("CASSANDRA_KEYSPACE")
