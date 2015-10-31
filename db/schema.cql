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

-- Job Management (Science Model Execution Tracking)
CREATE TABLE lcmap.job (
    job_id text PRIMARY KEY,
    status int,
    science_model_name text,
    execution_parameters text,
    result_keyspace text,
    result_table text,
    result_id text,

) WITH COMPRESSION = { 'sstable_compression' : 'LZ4Compressor' }
  AND COMMENT = 'Science model job results tracking and linking.';

-- Results table for sample model
CREATE TABLE lcmap.samplemodel (
    result_id text PRIMARY KEY,
    result text

) WITH COMPRESSION = { 'sstable_compression' : 'LZ4Compressor' }
  AND COMMENT = 'Sample model results table.';

