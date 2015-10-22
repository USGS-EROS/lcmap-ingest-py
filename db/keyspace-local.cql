-- Local
CREATE KEYSPACE lcmap WITH REPLICATION = { 'class' : 'SimpleStrategy', 'replication_factor': '1'} AND durable_writes = true;
