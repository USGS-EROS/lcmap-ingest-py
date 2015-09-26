--- Local
-- CREATE KEYSPACE lcmap WITH REPLICATION = { 'class' : 'NetworkTopologyStrategy', 'DC1' : 1};

--- EC2
-- CREATE KEYSPACE lcmap WITH REPLICATION = { 'class' : 'NetworkTopologyStrategy', 'us-west-2' : 3 };

CREATE TABLE lcmap.epsg_5070 (
    x int,
    y int,
    layer text,
    acquired timestamp,
    data blob,
    data_fill int static,
    data_range list<int> static,
    data_scale float static,
    data_shape list<int> static,
    data_type text static,
    source text,
    PRIMARY KEY ((x, y, layer), acquired)
) WITH CLUSTERING ORDER BY (acquired DESC)
    AND bloom_filter_fp_chance = 0.01
    AND caching = '{"keys":"ALL", "rows_per_partition":"NONE"}'
    AND comment = ''
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy'}
    AND compression = {'chunk_length_kb': '64', 'sstable_compression': 'org.apache.cassandra.io.compress.SnappyCompressor'}
    AND dclocal_read_repair_chance = 0.1
    AND default_time_to_live = 0
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND read_repair_chance = 0.0
    AND speculative_retry = '99.0PERCENTILE';

CREATE TABLE lcmap.tile_groups (
    table_name text,
    projection text static,
    pixel_units text static,
    pixel_x float static,
    pixel_x_offset float static,
    pixel_y float static,
    pixel_y_offset float static,
    resample_method text static,
    band text,
    satellite text,
    instrument text,
    product text,
    category text,
    long_name text,
    short_name text,
    spectrum list<float>,
    data_fill int,
    data_range list<int>,
    data_scale float,
    data_type text,
    data_units text,
    class_values map<int, text>,
    PRIMARY KEY (table_name, band)
) WITH CLUSTERING ORDER BY (band ASC)
    AND bloom_filter_fp_chance = 0.01
    AND caching = '{"keys":"ALL", "rows_per_partition":"NONE"}'
    AND comment = ''
    AND compaction = {'class': 'org.apache.cassandra.db.compaction.SizeTieredCompactionStrategy'}
    AND compression = {'sstable_compression': 'org.apache.cassandra.io.compress.LZ4Compressor'}
    AND dclocal_read_repair_chance = 0.1
    AND default_time_to_live = 0
    AND gc_grace_seconds = 864000
    AND max_index_interval = 2048
    AND memtable_flush_period_in_ms = 0
    AND min_index_interval = 128
    AND read_repair_chance = 0.0
    AND speculative_retry = '99.0PERCENTILE';

CREATE INDEX tile_groups_satellite ON lcmap.tile_groups (satellite);

CREATE INDEX tile_groups_category ON lcmap.tile_groups (category);

INSERT INTO lcmap.tile_groups(table_name, pixel_x, pixel_y, pixel_x_offset, pixel_y_offset, pixel_units, resample_method)
VALUES ('epsg_5070', 30, -30, 0, 0, 'meters', 'nearest neighbor');

INSERT INTO lcmap.tile_groups(table_name, projection)
VALUES ('epsg_5070', 'PROJCS["NAD83 / Conus Albers",GEOGCS["NAD83",DATUM["North_American_Datum_1983",SPHEROID["GRS 1980",6378137,298.257222101,AUTHORITY["EPSG","7019"]],TOWGS84[1,1,-1,0,0,0,0],AUTHORITY["EPSG","6269"]],PRIMEM["Greenwich",0,AUTHORITY["EPSG","8901"]],UNIT["degree",0.0174532925199433,AUTHORITY["EPSG","9122"]],AUTHORITY["EPSG","4269"]],PROJECTION["Albers_Conic_Equal_Area"],PARAMETER["standard_parallel_1",29.5],PARAMETER["standard_parallel_2",45.5],PARAMETER["latitude_of_center",23],PARAMETER["longitude_of_center",-96],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1,AUTHORITY["EPSG","9001"]],AXIS["X",EAST],AXIS["Y",NORTH],AUTHORITY["EPSG","5070"]]');

INSERT INTO lcmap.tile_groups (table_name, band, product, category, satellite, instrument)
VALUES ('epsg_5070', 'LC8SR:band 1 surface reflectance', 'sr_refl', 'image', 'LANDSAT_8', 'OLI_TIRS');
INSERT INTO lcmap.tile_groups (table_name, band, short_name, long_name)
VALUES ('epsg_5070', 'LC8SR:band 1 surface reflectance', 'LC8SR', 'band 1 surface reflectance');
INSERT INTO lcmap.tile_groups (table_name, band, data_fill, data_range, data_scale, data_type, data_units)
VALUES ('epsg_5070', 'LC8SR:band 1 surface reflectance', -9999, [-2000, 16000], 0.000100, 'int16', 'reflectance');

INSERT INTO lcmap.tile_groups (table_name, band, product, category, satellite, instrument)
VALUES ('epsg_5070', 'LC8SR:band 2 surface reflectance', 'sr_refl', 'image', 'LANDSAT_8', 'OLI_TIRS');
INSERT INTO lcmap.tile_groups (table_name, band, short_name, long_name)
VALUES ('epsg_5070', 'LC8SR:band 2 surface reflectance', 'LC8SR', 'band 2 surface reflectance');
INSERT INTO lcmap.tile_groups (table_name, band, data_fill, data_range, data_scale, data_type, data_units)
VALUES ('epsg_5070', 'LC8SR:band 2 surface reflectance', -9999, [-2000, 16000], 0.000100, 'int16', 'reflectance');

INSERT INTO lcmap.tile_groups (table_name, band, product, category, satellite, instrument)
VALUES ('epsg_5070', 'LC8SR:band 3 surface reflectance', 'sr_refl', 'image', 'LANDSAT_8', 'OLI_TIRS');
INSERT INTO lcmap.tile_groups (table_name, band, short_name, long_name)
VALUES ('epsg_5070', 'LC8SR:band 3 surface reflectance', 'LC8SR', 'band 3 surface reflectance');
INSERT INTO lcmap.tile_groups (table_name, band, data_fill, data_range, data_scale, data_type, data_units)
VALUES ('epsg_5070', 'LC8SR:band 3 surface reflectance', -9999, [-2000, 16000], 0.000100, 'int16', 'reflectance');

INSERT INTO lcmap.tile_groups (table_name, band, product, category, satellite, instrument)
VALUES ('epsg_5070', 'LC8SR:band 4 surface reflectance', 'sr_refl', 'image', 'LANDSAT_8', 'OLI_TIRS');
INSERT INTO lcmap.tile_groups (table_name, band, short_name, long_name)
VALUES ('epsg_5070', 'LC8SR:band 4 surface reflectance', 'LC8SR', 'band 4 surface reflectance');
INSERT INTO lcmap.tile_groups (table_name, band, data_fill, data_range, data_scale, data_type, data_units)
VALUES ('epsg_5070', 'LC8SR:band 4 surface reflectance', -9999, [-2000, 16000], 0.000100, 'int16', 'reflectance');

INSERT INTO lcmap.tile_groups (table_name, band, product, category, satellite, instrument)
VALUES ('epsg_5070', 'LC8SR:band 5 surface reflectance', 'sr_refl', 'image', 'LANDSAT_8', 'OLI_TIRS');
INSERT INTO lcmap.tile_groups (table_name, band, short_name, long_name)
VALUES ('epsg_5070', 'LC8SR:band 5 surface reflectance', 'LC8SR', 'band 5 surface reflectance');
INSERT INTO lcmap.tile_groups (table_name, band, data_fill, data_range, data_scale, data_type, data_units)
VALUES ('epsg_5070', 'LC8SR:band 5 surface reflectance', -9999, [-2000, 16000], 0.000100, 'int16', 'reflectance');

INSERT INTO lcmap.tile_groups (table_name, band, product, category, satellite, instrument)
VALUES ('epsg_5070', 'LC8SR:band 6 surface reflectance', 'sr_refl', 'image', 'LANDSAT_8', 'OLI_TIRS');
INSERT INTO lcmap.tile_groups (table_name, band, short_name, long_name)
VALUES ('epsg_5070', 'LC8SR:band 6 surface reflectance', 'LC8SR', 'band 6 surface reflectance');
INSERT INTO lcmap.tile_groups (table_name, band, data_fill, data_range, data_scale, data_type, data_units)
VALUES ('epsg_5070', 'LC8SR:band 6 surface reflectance', -9999, [-2000, 16000], 0.000100, 'int16', 'reflectance');

INSERT INTO lcmap.tile_groups (table_name, band, product, category, satellite, instrument)
VALUES ('epsg_5070', 'LC8SR:band 7 surface reflectance', 'sr_refl', 'image', 'LANDSAT_8', 'OLI_TIRS');
INSERT INTO lcmap.tile_groups (table_name, band, short_name, long_name)
VALUES ('epsg_5070', 'LC8SR:band 7 surface reflectance', 'LC8SR', 'band 7 surface reflectance');
INSERT INTO lcmap.tile_groups (table_name, band, data_fill, data_range, data_scale, data_type, data_units)
VALUES ('epsg_5070', 'LC8SR:band 7 surface reflectance', -9999, [-2000, 16000], 0.000100, 'int16', 'reflectance');

INSERT INTO lcmap.tile_groups (table_name, band, product, category, satellite, instrument)
VALUES ('epsg_5070', 'LC8SR:surface reflectance cloud mask', 'sr_refl', 'qa', 'LANDSAT_8', 'OLI_TIRS');
INSERT INTO lcmap.tile_groups (table_name, band, short_name, long_name)
VALUES ('epsg_5070', 'LC8SR:surface reflectance cloud mask', 'LC8SR', 'surface reflectance cloud mask');
INSERT INTO lcmap.tile_groups (table_name, band, data_fill, data_range, data_type, data_units)
VALUES ('epsg_5070', 'LC8SR:surface reflectance cloud mask', 0, NULL,'uint8', 'bitmap');
INSERT INTO lcmap.tile_groups (table_name, band, class_values)
VALUES ('epsg_5070',
        'LC8SR:surface reflectance cloud mask',
        { 0:'cirrus cloud',
          1:'cloud',
          2:'adjacent to cloud',
          3:'cloud shadow',
          4:'aerosol',
          5:'aerosol',
          6:'unused',
          7:'internal test' });

INSERT INTO lcmap.tile_groups (table_name, band, product, category, satellite, instrument)
VALUES ('epsg_5070', 'LC8CFMASK:cfmask_band', 'cfmask', 'qa', 'LANDSAT_8', 'OLI_TIRS');
INSERT INTO lcmap.tile_groups (table_name, band, short_name, long_name)
VALUES ('epsg_5070', 'LC8CFMASK:cfmask_band', 'LC8CFMASK', 'cfmask_band');
INSERT INTO lcmap.tile_groups (table_name, band, data_fill, data_range, data_type, data_units)
VALUES ('epsg_5070', 'LC8CFMASK:cfmask_band', 255, [0,4], 'uint8', 'quality/feature classification');
INSERT INTO lcmap.tile_groups (table_name, band, class_values)
VALUES ('epsg_5070',
        'LC8CFMASK:cfmask_band',
        { 0:'clear',
          1:'water',
          2:'cloud_shadow',
          3:'snow',
          4:'cloud',
          255:'fill' });


INSERT INTO lcmap.tile_groups (table_name, band, product, category, satellite, instrument)
VALUES ('epsg_5070', 'LC8CFMASK:cfmask_conf_band', 'cfmask', 'qa', 'LANDSAT_8', 'OLI_TIRS');
INSERT INTO lcmap.tile_groups (table_name, band, short_name, long_name)
VALUES ('epsg_5070', 'LC8CFMASK:cfmask_conf_band', 'LC8CFMASK', 'cfmask_conf_band');
INSERT INTO lcmap.tile_groups (table_name, band, data_fill, data_range, data_type, data_units)
VALUES ('epsg_5070', 'LC8CFMASK:cfmask_conf_band', 255, [0,3], 'uint8', 'quality/feature classification');
INSERT INTO lcmap.tile_groups (table_name, band, class_values)
VALUES ('epsg_5070',
        'LC8CFMASK:cfmask_conf_band',
        { 0:'none',
          1:'less than or equal to 12.5 Percent Cloud Confidence',
          2:'greater than 12.5 and less than or equal to 22.5 Percent Cloud Confidence',
          3:'greater than 22.5 Percent Cloud Confidence',
          255: 'fill' });


