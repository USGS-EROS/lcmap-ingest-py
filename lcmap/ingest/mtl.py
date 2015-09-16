"""
   mtl.py
   ~~~~~~

   Extract relevant metadata, nothing else.

   The MTL contains a scene center acquisition date and time. The time
   is important because it disambiguates data acquired on the same date
   in different scenes. Overlap between scenes on the same day should
   be saved but without a precise time this data cannot be saved by
   Cassandra.

   Even though resolving this ambiguity technically isn't the tiling's
   responsibility, the tiling module can do something to help. Be aware
   that each pixel may be acquired at a different time though, so relying
   on this precise time for scientific purposes requires additional
   consideration.

"""

import re
import dateutil, pytz

class MTL:

    def __init__(self, path):
        text = open(path).read()
        pair = re.findall('(\S+) = (\S+)', text)
        self.data = dict((key, value) for (key, value) in pair)

    @property
    def acquisition_datetime(self):
        d = self.data.get("DATE_ACQUIRED").replace('"','')
        t = self.data.get("SCENE_CENTER_TIME").replace('"','')
        dt = dateutil.parser.parse("%s %s" % (d, t))

        return dt.replace(tzinfo=pytz.UTC)

    @property
    def scene_id(self):
        return self.data.get("LANDSAT_SCENE_ID", "").replace('"', "")
