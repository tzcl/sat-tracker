# Satellite Tracker

A script that calculates satellite trajectory using [Skyfield](https://rhodesmill.org/skyfield/).

**Dependencies**
* `python3`
* `pip`
* `pipenv` (install using `pip install pipenv`)

## Installation

To install, navigate to your directory of choice and run the following commands.

```
git clone https://github.com/tzcl/sat-tracker.git
cd sat-tracker
pipenv install
```

## Usage

Before running the script, make sure to activate the virtual environment.

```
pipenv activate
```

The script itself takes one argument, `id`, which can be a satellite's NORAD ID or its international code. You can optionally specify the latitude and longitude of the ground station by passing them after the `id`. By default, the script uses Melbourne's latitude and longitude.

```
usage: tracker.py [-h] id [lat] [lon]

positional arguments:
  id          satellite id to track
  lat         ground station latitude
  lon         ground station longitude

optional arguments:
  -h, --help  show this help message and exit
```

## Output

The script will generate CSV files for each pass of the specified satellite over the next 24 hours (from the time the script was run).

Running the script for NOAA-20 (NORAD ID: 43013) with a ground station east of Melbourne.

```
python tracker.py 43013 -37.793611 145.086389
```

Output:
```
Getting satellite data...
[#################################] 100% CATNR-43013.txt
Calculating when NOAA 20 will be visible...
Generating pass data...
Finished! Produced 6 files ('pass1.csv', ..., 'pass6.csv').
```

pass1.csv:
```
timestamp,altitude,azimuth
08/09/21-23:54:49,0.0038,56.297977
08/09/21-23:54:50,0.055436,56.364814
08/09/21-23:54:51,0.107125,56.431882
08/09/21-23:54:52,0.158869,56.499183
08/09/21-23:54:53,0.210667,56.566719
...
```
