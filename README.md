## Info

This repository contains code used to evaluate different approaches taken
to store time-series oriented, analysis ready Landsat imagery.

## More Information

This project is hosted by the US Geological Survey (USGS) Earth Resources
Observation and Science (EROS) Land Change Monitoring, Assessment, and
Projection (LCMAP) Project. For questions regarding this source code, please
contact the Landsat Contact Us page and specify USGS LCMAP in the "Regarding"
section. https://landsat.usgs.gov/contactus.php

## Cassandra Setup

### Clustering

Setting up Cassandra clusters is beyond the scope of this README. However, if
you are just testing this on a single host, you can use the
[ccm tool](https://github.com/pcmanus/ccm). ``make`` targets are provided in
this project to set up a local cluster for testing.  Simply run the following:

```bash
$ make ccm
```

If you are running a local cluster of more than one node with ccm, you will
need to make sure that you have network interface aliases set up (usually off
of the loopback device).

### Schemas
Before running the ingest script, you need to have the keyspace and schema set
up. If you are running Cassandra on EC2, use this command:

```bash
$ cqlsh -f config/keyspace-ec2.cql
```

If running with a datacenter setup:

```bash
$ cqlsh -f config/keyspace-dc.cql
```

Otherwise, use this:

```bash
$ cqlsh -f config/keyspace-local.cql
```

Then, to load the schema into Cassandra, do the following:

```bash
$ cqlsh -f config/schema.cql
```

## Ingest Usage

Ingest takes an ESPA scene archive and saves tiles to a Cassandra database.
Create a .env file to specify your database configuration parameters.

### Basic

Ingest a single file, logging all output to standard out.

```
$ ./scripts/ingest /data/Landsat/some-scene.tar.gz
```

Ingest a bunch of files at once:

```
$ ./scripts/ingest /data/Landsat/*01234*.tar.gz
```

### Advanced

You can run ingest in parallel on groups of files, logging all output to a file,
using a temporary directory of your choice to hold decompressed scenes.

```
$ export TEMP=/data/tmp
$ mkdir
nohup python ingest "/data/Landsat/*045026*" > logs/045026.log &
nohup python ingest "/data/Landsat/*045027*" > logs/045027.log &
nohup python ingest "/data/Landsat/*045028*" > logs/045028.log &
nohup python ingest "/data/Landsat/*045029*" > logs/045029.log &
nohup python ingest "/data/Landsat/*046026*" > logs/046026.log &
nohup python ingest "/data/Landsat/*046027*" > logs/046027.log &
nohup python ingest "/data/Landsat/*046028*" > logs/046028.log &
nohup python ingest "/data/Landsat/*046029*" > logs/046029.log &
```

## Installation

### With ``pip``

```
pip install git+https://github.com/USGS-EROS/lcmap-ingest-py.git@master
```

### Development

If you would like to evaluate how this will work when installed, you should
use this instead of the usual `install` command.

```
python setup.py develop
```

### Testing

To run the unit tests, simply run ``nosetests`` in the project directory:

```bash
$ nosetests
```

If you would like to run the tests against different versions of Python, there
is a ``tox.ini`` file set up for that. Make sure you have ``tox`` installed:

```bash
$ pip install tox
```

And then simply execute it:

```bash
$ tox
```

This will execute against Python 2.7, Python 3.4, and pypy environments.
