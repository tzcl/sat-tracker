#!/usr/bin/env python3

from skyfield.api import load, wgs84
from datetime import datetime, timezone, timedelta

ts = load.timescale()

# Load TLE
url = 'https://celestrak.com/satcat/tle.php?INTDES=2009-005'
filename = 'NOAA-19.txt'
satellites = load.tle_file(url, filename=filename)
satellite = satellites[0]

# Calculate when it passes overhead
melbourne = wgs84.latlon(-37.814, 144.96332)
t0 = ts.utc(2021, 7, 23)
t1 = ts.utc(2021, 7, 24)
t, events = satellite.find_events(melbourne, t0, t1, altitude_degrees=0)
for ti, event in zip(t, events):
    name = ('above horizon', 'culminate', 'below horizon')[event]
    print(ti.utc_strftime('%Y %b %d %H:%M:%S'), name)


# Current position
t = ts.now()
geocentric = satellite.at(t)

subpoint = wgs84.subpoint(geocentric)
print('Latitude:', subpoint.latitude)
print('Longitude:', subpoint.longitude)
print('Height: {:.1f} km'.format(subpoint.elevation.km))

# Relative position
t = ts.now()
difference = satellite - melbourne
topocentric = difference.at(t)

alt, az, distance = topocentric.altaz()
print('Altitude:', alt)
print('Azimuth:', az)
print('Distance: {:.1f} km'.format(distance.km))

# Check if the satellite passes overhead
# Need to correct for timezone!
# AEST is 10 hours ahead, so need to subtract 10 to get UTC
one_day = ts.utc(2021, 7, 23, 20 - 10, range(0, 60))
topocentric = difference.at(one_day)

alt, az, distance = topocentric.altaz()
for count, time in enumerate(one_day):
    print("Time: ", time.utc_strftime("%Y-%m-%d %H:%M:%S"))
    print("Altitude:", alt.degrees[count])
    print("Azimuth:", az.degrees[count])
    print("Distance: {:.1f} km".format(distance.km[count]))

print("------------------------------------------------")
print(min(distance.km))
