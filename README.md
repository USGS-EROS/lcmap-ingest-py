## Info

This repository contains code used to evaluate different approaches taken
to store time-series oriented, analysis ready Landsat imagery.

## More Information

This project is hosted by the US Geological Survey (USGS) Earth Resources Observation
and Science (EROS) Land Change Monitoring, Assessment, and Projection (LCMAP) Project.
For questions regarding this source code, please contact the Landsat Contact Us page
and specify USGS LCMAP in the "Regarding" section. https://landsat.usgs.gov/contactus.php


## Ingest Usage

Ingest takes an ESPA scene archive and saves tiles to a Cassandra database.
Create a .env file to specify your database configuration parameters.

### Basic

Ingest a single file, logging all output to standard out.

```
python ingest /data/Landsat/some-scene.tar.gz
```

You can run ingest in parallel on groups of files, logging all output to a file,
using a temporary directory of your choice to hold decompressed scenes.

### Advanced

```
export TEMP=/data/tmp
mkdir
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
