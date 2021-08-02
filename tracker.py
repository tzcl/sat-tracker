#!/usr/bin/env python3

"""
This is a script that tracks the trajectory of a satellite over time.

Input: satellite ID (either NORAD ID or international code).
Output: an array containing satellite trajectory in terms of long/lat over time
"""

# TODO: upgrades to script
# - Determine the next rise/pass
#   - Look into findevents, compare against Stellarium
#   - Calculate timezone from lat/long???
# - Print asimuth/zenith to file

from argparse import ArgumentParser
from skyfield.api import load, wgs84
from datetime import datetime
import pytz
from collections import defaultdict
import pprint                   # FIXME: debug dictionary
import numpy as np

MELB_LAT = -37.814
MELB_LON = 144.96332

# Read satellite id from command line
parser = ArgumentParser()
parser.add_argument("id", help="satellite id to track")
parser.add_argument("lat", nargs="?", default=MELB_LAT,
                    help="ground station latitude")
parser.add_argument("lon", nargs="?", default=MELB_LON,
                    help="ground station longitude")
args = parser.parse_args()

sat_id = args.id
ground_lat = args.lat
ground_lon = args.lon

# Parse satellite id
#  International ids are of the form YYYY-NNNA, e.g., 2017-073A
#  International ids may be the same for multiple satellites
#  NORAD ids are 5 digit numbers
is_norad = not sat_id[-1].isalpha()
sat_offs = 0
if not is_norad:
    # Use the letter on the end of id to determine satellite
    sat_offs = ord(sat_id[-1]) - ord('A')
    sat_id = sat_id[:-1]

# Load TLE and parse into EarthSatellite
request_type = 'CATNR' if is_norad else 'INTDES'
url = f'https://celestrak.com/satcat/tle.php?{request_type}={sat_id}'
filename = f'{request_type}-{sat_id}.txt'
satellites = load.tle_file(url, filename=filename)
if not satellites:
    raise Exception("Failed to load satellites")
sat = satellites[sat_offs]

# Check epoch is valid
ts = load.timescale()

t = ts.now()
days = t - sat.epoch

# Redownload the TLE if necessary
if abs(days) > 14:
    satellites = load.tle_file(url, filename=filename, reload=True)
    sat = satellites[sat_offs]

# Calculate distance
ground_station = wgs84.latlon(ground_lat, ground_lon)
diff = sat - ground_station

tz = pytz.timezone('Australia/Melbourne')

t0 = ts.from_datetime(datetime(2021, 8, 3, tzinfo=tz))
t1 = ts.from_datetime(datetime(2021, 8, 5, tzinfo=tz))

# Keep track of events
when = defaultdict(list)

t, events = sat.find_events(ground_station, t0, t1)
for ti, event in zip(t, events):
    name = ('rise', 'culminate', 'set')[event]
    when[name].append(ti)

first_rise = when['rise'][0].astimezone(tz)
first_set = when['set'][0].astimezone(tz)
seconds = (first_set - first_rise).total_seconds()

start = when['rise'][0]
end = when['set'][0]

whole = start.whole
start_fraction = start.tt_fraction
end_fraction = end.whole - start.whole + end.tt_fraction
fraction = np.linspace(start_fraction, end_fraction, int(seconds))
times = ts.tt_jd(whole, fraction)

print(times)

topocentric = diff.at(times)
for t, p in zip(times, topocentric):
    dt = t.astimezone(tz)
    alt, az, distance = p.altaz()
    print(dt.strftime("%Y %D %H:%M:%S"))
    print("Altitude:", alt)
    print("Azimuth:", az)
    print("Distance: {:.1f} km".format(distance.km))
