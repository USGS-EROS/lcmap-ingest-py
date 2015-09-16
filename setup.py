from setuptools import setup, find_packages

setup(
    name = "LCMAP",
    version = "0.0.1a0",
    packages = find_packages(
        exclude=[".env"]
    ),
    install_requires=[
        'cassandra-driver',
        'click',
        'GDAL',
        'numpy',
        'beautifulsoup4',
        'lxml',
        'python-dateutil',
        'pytz',
    ],
    scripts = ['scripts/ingest'],
    author = "Jonathan Morton, Kevin Impecoven",
    author_email = "jmorton@example.com",
    description = "USGS LCMAP tools for ingesting and accessing Landsat data stored in Cassandra",
    license = "TBD",
    keywords = "usgs lcmap api cassandra",
    url = "https://github.com/USGS-EROS/lcmap-py",
)