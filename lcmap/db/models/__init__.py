# In order for models to connect to Cassandra a connection must be
# setup.

import cassandra.cqlengine.connection as connection
import lcmap.config as config
connection.setup(config.CASSANDRA_HOSTS, default_keyspace=config.CASSANDRA_KEYSPACE)
