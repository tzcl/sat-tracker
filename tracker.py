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
from datetime import timedelta
import pytz
from collections import defaultdict
import numpy as np
import csv

MELB_LAT = -37.814
MELB_LON = 144.96332

MIN_ALT = 30

# Read satellite id from command line
parser = ArgumentParser()
parser.add_argument("id", help="satellite id to track")
parser.add_argument("lat", nargs="?", default=MELB_LAT,
                    help="ground station latitude")
parser.add_argument("lon", nargs="?", default=MELB_LON,
                    help="ground station longitude")
parser.add_argument("alt", nargs="?", default=MIN_ALT,
                    help="minimum altitude of satellite pass")
args = parser.parse_args()

sat_id = args.id
ground_lat = args.lat
ground_lon = args.lon
min_alt = args.alt

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

print("Getting satellite data...")

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

# NOTE: assume ground station is in Melbourne
# NOTE: (it's hard trying to work out city from lat/lon)
tz = pytz.timezone('Australia/Melbourne')

print(f"Calculating when {sat.name} will be visible...")

t0 = ts.now()
# TODO: hardcoded 1-day increment
t1 = ts.utc(t0.utc_datetime() + timedelta(days=1))

# Keep track of events
when = defaultdict(list)

t, events = sat.find_events(ground_station, t0, t1, altitude_degrees=min_alt)
for ti, event in zip(t, events):
    name = ('rise', 'culminate', 'set')[event]
    when[name].append(ti)

print("Generating pass data...")

# CSV header
HEADER = ["timestamp", "altitude", "azimuth"]
# CSV decimal places
PRECISION = 6


def pass_to_csv(t0, t1, vec, filename):
    """Calculate trajectory and store the output in a CSV file."""
    start = t0
    end = t1

    seconds = (end.utc_datetime() - start.utc_datetime()).total_seconds()

    whole = start.whole
    start_fraction = start.tt_fraction
    end_fraction = end.whole - start.whole + end.tt_fraction
    fraction = np.linspace(start_fraction, end_fraction, int(seconds))
    times = ts.tt_jd(whole, fraction)

    topocentric = vec.at(times)

    with open(filename, 'w', encoding='UTF8') as f:
        writer = csv.writer(f)
        writer.writerow(HEADER)

        for t, p in zip(times, topocentric):
            dt = t.astimezone(tz)
            timestamp = dt.strftime("%y/%m/%d-%H:%M:%S")
            alt, az, distance = p.altaz()

            data = [timestamp,
                    round(alt.degrees, PRECISION),
                    round(az.degrees, PRECISION)]
            writer.writerow(data)


# Iterate over satellite passes
num_passes = 0
for rise, set in zip(when['rise'], when['set']):
    num_passes += 1
    pass_to_csv(rise, set, diff, f"pass{num_passes}.csv")

print(f"Finished! Produced {num_passes} files"
      f"('pass1.csv', ..., 'pass{num_passes}.csv').")
