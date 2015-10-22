-- EC2
CREATE KEYSPACE lcmap WITH REPLICATION = { 'class' : 'NetworkTopologyStrategy', 'us-west-2' : 3 };
