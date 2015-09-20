"""
   scene.py
   ~~~~~~~~

   Provide Scene class for working with ESPA archives.

   This module relies on gdal to perform format independent access to ESPA data
   but only ENVI and GeoTIFFs have been tested.

"""

import os, re, glob
import bs4, dateutil.parser, pytz
import gdal, numpy as np
import logging

from lcmap.ingest.band import Band
from lcmap.ingest.mtl import MTL

logger = logging.getLogger(__name__)

class Scene:

    def __init__(self, dirpath):
        self.dirpath = dirpath

        # most properties come from the XML metadata file...
        xml_glob = os.path.join(dirpath, '*.xml')
        xml_path = glob.glob(xml_glob)[0]
        self.xml = bs4.BeautifulSoup(open(xml_path), 'lxml')

        # ...however, for properties that are missing, use the MTL file.
        mtl_glob = os.path.join(dirpath, '*_MTL.txt')
        mtl_path = glob.glob(mtl_glob)[0]
        self.mtl = MTL(mtl_path)

    #
    # Properties from MTL, not found in XML.
    #

    @property
    def acquired(self):
        """Acquired time, inferred from scene center time.

        This might not be precisely when all pixels were acquired but it is
        better than a date without a time. Tiles acquired on the same date
        for the same extent but from different scenese will overwrite one
        another if they do not have a specified time.
        """
        return self.mtl.acquisition_datetime

    @property
    def name(self):
        """Unique identifier for the scene.

        Although the scene ID contains redundant information like the platorm
        and acquisition date, it is the most reliable way to refer to a scene."""
        return self.mtl.scene_id

    #
    # Properties from XML metadata
    #

    @property
    def bands(self):
        if hasattr(self, '_bands'):
            return self._bands
        else:
            self._bands = []
            for el in self.xml.find_all('band'):
                self._bands.append(Band.from_xml(el, self))
            return self._bands

    @property
    def instrument(self):
        return self.xml.find('instrument').text

    @property
    def satellite(self):
        return self.xml.find('satellite').text

    @property
    def solar(self):
        return self.xml.find('solar_angles').attrs