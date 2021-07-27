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

The script itself takes one argument, `id`, which can be a satellite's NORAD ID or its international code.

```
usage: tracker.py [-h] [--reload] id

positional arguments:
  id          satellite id to track

optional arguments:
  -h, --help  show this help message and exit
  --reload    force redownload of satellite TLE
```

## Output

Running the script for NOAA-20 (NORAD ID: 43013).

```
python tracker.py 43013
```

Output:
```
[#################################] 100% CATNR-43013.txt
Time (UTC): 2021-07-27 23:19:48
Altitude: -30deg 29' 33.7"
Azimuth: 199deg 24' 19.1"
Distance: 7939.9 km
Time (UTC): 2021-07-27 23:19:49
Altitude: -30deg 28' 30.2"
Azimuth: 199deg 21' 01.0"
Distance: 7937.1 km
Time (UTC): 2021-07-27 23:19:50
Altitude: -30deg 27' 26.1"
Azimuth: 199deg 17' 41.2"
Distance: 7934.2 km
Time (UTC): 2021-07-27 23:19:51
Altitude: -30deg 26' 22.3"
Azimuth: 199deg 14' 22.1"
Distance: 7931.4 km
...
```
