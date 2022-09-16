import os
import logging
import numpy as np
import netCDF4


def configure_logging():
    """Prepare the logging file
    """
    logger = logging.getLogger("alborex_logger")
    logger.setLevel(logging.DEBUG)
    # Format for our loglines
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # Setup console logging
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    # Setup file logging as well
    fh = logging.FileHandler('/home/ctroupin/logs/alborexdata.log')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    return logger


def add_map_grid(m, coordinates, dlon, dlat, **kwargs):
    """Add x and y ticks (no line plotted for better visibility)
    """
    m.drawparallels(np.arange(round(coordinates[2]), coordinates[3], dlat), labels=[1, 0, 0, 0], **kwargs)
    m.drawmeridians(np.arange(round(coordinates[0]), coordinates[1], dlon), labels=[0, 0, 0, 1], **kwargs)


def load_lonloat_ctdleg(datafile):
    """Return coordinates from the file containing the information
    on the different legs
    """
    lon, lat = [], []
    with open(datafile) as f:
        line = f.readline().rsplit()
        while line:
            # print(line)
            lon.append(float(line[2]))
            lat.append(float(line[3]))
            line = f.readline().rsplit()
    return lon, lat


def read_lonlat_coast(filename, valex=999):
    """Return the coordinates of the contours
    as a list of lists (one list per contour)
    """
    with open(filename) as f:
        lonall, latall = [], []
        lon, lat = [], []
        line = f.readline().rsplit()
        while line:
            if float(line[0]) == valex:
                lonall.append(lon)
                latall.append(lat)
                lon, lat = [], []
            else:
                lon.append(float(line[0]))
                lat.append(float(line[1]))
            line = f.readline().rsplit()
    return lonall, latall

def load_sst_l2(filename):
    """
    Load the SST from netCDF L2 file obtained from
    https://oceancolor.gsfc.nasa.gov
    :param filename: name of the netCDF file
    :return: lon, lat, sst, sstflag, sstyear, sstday
    """
    if os.path.exists(filename):
        with netCDF4.Dataset(filename) as nc:
            # Read platform
            sat = nc.platform
            # Read time information
            # Assume all the measurements made the same day (and same year)
            year = nc.groups['scan_line_attributes'].variables['year'][0]
            day = nc.groups['scan_line_attributes'].variables['day'][0]
            # Read coordinates
            lon = nc.groups['navigation_data'].variables['longitude'][:]
            lat = nc.groups['navigation_data'].variables['latitude'][:]
            # Read geophysical variables
            try:
                sst = nc.groups['geophysical_data'].variables['sst'][:]
                sstqual = nc.groups['geophysical_data'].variables['qual_sst'][:]
            except KeyError:
                sst = nc.groups['geophysical_data'].variables['sst4'][:]
                sstqual = nc.groups['geophysical_data'].variables['qual_sst4'][:]
    else:
        lon, lat, sst, sstqual, year, day, sat = [], [], [], [], [], [], []
    return lon, lat, sst, sstqual, year, day, sat

