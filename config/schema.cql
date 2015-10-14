-- Local
CREATE KEYSPACE lcmap WITH REPLICATION = { 'class' : 'NetworkTopologyStrategy', 'DC1' : 1};

-- EC2
CREATE KEYSPACE lcmap WITH REPLICATION = { 'class' : 'NetworkTopologyStrategy', 'us-west-2' : 3 };

-- Tiles
CREATE TABLE lcmap.epsg_5070 (
    x int,
    y int,
    ubid text,
    acquired timestamp,
    data blob,

    -- by rule, all data contained in a row must be uniformly typed,
    -- ranged, filled, shaped, and scaled.
    -- ubid: mission, product, band number

    data_fill int static,
    data_range list<int> static,
    data_scale float static,
    data_shape list<int> static,
    data_type text static,
    source text,

    PRIMARY KEY ((x, y, ubid), acquired)

) WITH CLUSTERING ORDER BY (acquired DESC)
  AND COMPRESSION = { 'sstable_compression' : 'LZ4Compressor' }
  AND COMMENT = 'NAD83 / Conus Albers, uniformly projected and shaped tiles.';
