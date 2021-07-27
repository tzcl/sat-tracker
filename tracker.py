#!/usr/bin/env python3

"""
This is a script that tracks the trajectory of a satellite over time.

Input: satellite ID (either NORAD ID or international code).
Output: satellite trajectory in terms of long/lat over time.
"""

from argparse import ArgumentParser
from time import sleep
from skyfield.api import load, wgs84

# Read satellite id from command line
parser = ArgumentParser()
parser.add_argument("id", help="satellite id to track")
parser.add_argument('--reload',
                    help="force redownload of satellite TLE",
                    action="store_true")
args = parser.parse_args()

sat_id = args.id
reload_tle = args.reload

# Parse satellite id
# International ids are of the form YYYY-NNNA, e.g., 2017-073A
# International ids may be the same for multiple satellites
# NORAD ids are 5 digit numbers
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
satellites = load.tle_file(url, filename=filename, reload=reload_tle)
if not satellites:
    raise Exception("Failed to load satellites")
sat = satellites[sat_offs]

# Check epoch is valid
ts = load.timescale()

t = ts.now()
days = t - sat.epoch
if abs(days) > 14:
    print(f"WARNING: TLE may be out of date ({days} days away from epoch). "
          "Try running with '--reload'.")

# Calculate distance
melbourne = wgs84.latlon(-37.814, 144.96332)  # TODO: hardcoded!
diff = sat - melbourne

while True:
    t = ts.now()
    topocentric = diff.at(t)

    alt, az, distance = topocentric.altaz()
    print("Time (UTC):", t.utc_strftime("%Y-%m-%d %H:%M:%S"))
    print('Altitude:', alt)
    print('Azimuth:', az)
    print('Distance: {:.1f} km'.format(distance.km))

    sleep(1)
