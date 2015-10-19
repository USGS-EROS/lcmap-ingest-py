-- data center
CREATE KEYSPACE lcmap WITH REPLICATION = { 'class' : 'NetworkTopologyStrategy', 'DC1' : 1};
