create keyspace lcmap with replication = { 'class' : 'NetworkTopologyStrategy', 'us-west-2' : 2 };

create table tiles (
  projection  text,
  extent_x    int,
  extent_y    int,
  layer       text,
  acquired_at timestamp,
  type        text,
  data        blob,
  primary key ((projection, extent_x, extent_y), layer, acquired_at)
);
