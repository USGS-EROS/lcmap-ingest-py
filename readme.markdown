## Info

This repository contains code used to evaluate different approaches taken
to store time-series oriented, analysis ready Landsat imagery.

## More Information

This project is hosted by the US Geological Survey (USGS) Earth Resources Observation
and Science (EROS) Land Change Monitoring, Assessment, and Projection (LCMAP) Project.
For questions regarding this source code, please contact the Landsat Contact Us page
and specify USGS LCMAP in the "Regarding" section. https://landsat.usgs.gov/contactus.php


## Example Usage

```
export TEMP=/data/tmp
nohup python ingest.py "/data/Landsat/*045026*" > 045026.log &
nohup python ingest.py "/data/Landsat/*045027*" > 045027.log &
nohup python ingest.py "/data/Landsat/*045028*" > 045028.log &
nohup python ingest.py "/data/Landsat/*045029*" > 045029.log &
nohup python ingest.py "/data/Landsat/*046026*" > 046026.log &
nohup python ingest.py "/data/Landsat/*046027*" > 046027.log &
nohup python ingest.py "/data/Landsat/*046028*" > 046028.log &
nohup python ingest.py "/data/Landsat/*046029*" > 046029.log &
```

## Installation

### With Pip

```
pip install git+https://github.com/USGS-EROS/lcmap-py.git@master
```

### Development

If you would like to evaluate how this will work when installed, you should
use this instead of the usual `install` command.

```
python setup.py develop
```