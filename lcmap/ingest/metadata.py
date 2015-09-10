from bs4 import BeautifulSoup
from dateutil import parser
import logging
import os
import math
import pytz

logger = logging.getLogger()


def parse(path):
    base_path = os.path.dirname(path)

    with open(path) as meta_file:
        soup = BeautifulSoup(meta_file)

        # parse the global info
        satellite = soup.find('satellite').text
        instrument = soup.find('instrument').text
        acquisition_date = parser.parse(soup.find('acquisition_date').text)
        acquisition_date.replace(tzinfo=pytz.UTC)
        bounding_coordinates = soup.find('bounding_coordinates')
        bounding_box = {
            'west': float(bounding_coordinates.find('west').text),
            'east': float(bounding_coordinates.find('east').text),
            'north': float(bounding_coordinates.find('north').text),
            'south': float(bounding_coordinates.find('south').text)
        }
        ul = soup.find('corner_point', location='UL')
        lr = soup.find('corner_point', location='LR')
        extent = {
            'ul': {
                'x': float(ul.get('x')),
                'y': float(ul.get('y'))
            },
            'lr': {
                'x': float(lr.get('x')),
                'y': float(lr.get('y'))
            }
        }

        # parse the band information
        bands = []
        for band in soup.find_all('band'):
            category = band.get('category')
            pixel_size = band.find('pixel_size')
            band_info = {
                'name': band.get('name'),
                'rows': int(band.get('nlines')),
                'cols': int(band.get('nsamps')),
                'units': band.find('data_units').text,
                'file_path': os.path.join(base_path, band.find('file_name').text),
                'pixel_size': {
                    'x': int(pixel_size.get('x')),
                    'y': int(pixel_size.get('y'))
                }
            }

            # add in the values that may not be included in every band
            fill_value = band.get('fill_value')
            if fill_value is not None:
                band_info['fill_value'] = float(fill_value)
            valid_range = band.find('valid_range')
            if valid_range is not None:
                band_info['valid_range'] = {
                    'min': float(valid_range.get('min')),
                    'max': float(valid_range.get('max'))
                }
            scale_factor = band.get('scale_factor')
            if scale_factor is not None:
                band_info['scale_factor'] = float(scale_factor)

            # append the band to the list
            bands.append(band_info)

    # assemble the result
    return {
        'info': {
            'satellite': satellite,
            'instrument': instrument,
            'acquisition_date': acquisition_date,
            'bounding_box': bounding_box,
            'extent': extent
        },
        'bands': bands
    }
