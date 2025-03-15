from skyfield.api import load, Topos
from skyfield import almanac
import datetime
import math

# Load Skyfield data (ephemeris)
planets = load('de421.bsp')  # Use DE421 for general accuracy
earth = planets['earth']
moon = planets['moon']
sun = planets['sun']
mercury = planets['mercury barycenter']
venus = planets['venus barycenter']
mars = planets['mars barycenter']
jupiter = planets['jupiter barycenter']
saturn = planets['saturn barycenter']

# Define major aspects (in degrees) with a 1-degree orb
major_aspects = [0, 60, 90, 120, 180]  # Conjunction, Sextile, Square, Trine, Opposition
orb = 1.0  # Typical orb for VOC calculation

# Zodiac sign boundaries (approximate ecliptic longitude in degrees)
zodiac_signs = {
    'Aries': 0, 'Taurus': 30, 'Gemini': 60, 'Cancer': 90, 'Leo': 120, 'Virgo': 150,
    'Libra': 180, 'Scorpio': 210, 'Sagittarius': 240, 'Capricorn': 270, 'Aquarius': 300, 'Pisces': 330
}



# Function to compute ecliptic longitude
def get_ecliptic_longitude(body, time):
    astrometric = earth.at(time).observe(body)
    lon, _, _ = astrometric.ecliptic_latlon()
    return lon.degrees % 360  # Normalize to 0-360°

# Function to determine zodiac sign from longitude
def get_zodiac_sign(longitude):
    for sign, start in zodiac_signs.items():
        if start <= longitude < (start + 30):
            return sign
    return 'Pisces'  # Edge case for 330-360°

# Function to check if an aspect exists within orb
def is_aspect(angle, target_aspects, orb):
    return any(abs(angle - aspect) <= orb for aspect in target_aspects)

# Main VOC check function
def is_moon_void_of_course(time):
    # Get Moon's current position
    moon_lon = get_ecliptic_longitude(moon, time)
    current_sign = get_zodiac_sign(moon_lon)

    # List of planets to check aspects with
    planet_bodies = [sun, mercury, venus, mars, jupiter, saturn]
    planet_lons = [get_ecliptic_longitude(body, time) for body in planet_bodies]

    # Check current aspects
    has_current_aspect = False
    for planet_lon in planet_lons:
        angle = min((moon_lon - planet_lon) % 360, (planet_lon - moon_lon) % 360)
        if is_aspect(angle, major_aspects, orb):
            has_current_aspect = True
            break

    # If Moon has a current aspect, it’s not VOC
    if has_current_aspect:
        return False, current_sign, "Moon is currently making an aspect."

    # Check if Moon will make another aspect before leaving the sign
    # Approximate Moon speed: ~13.2 degrees/day, check next 2 days
    time_step = ts.utc(time.utc_datetime() + datetime.timedelta(hours=1))
    moon_lon_future = get_ecliptic_longitude(moon, time_step)
    future_sign = get_zodiac_sign(moon_lon_future)

    # If Moon hasn’t changed signs yet, check future aspects
    if current_sign == future_sign:
        for planet_lon in planet_lons:
            angle = min((moon_lon_future - planet_lon) % 360, (planet_lon - moon_lon_future) % 360)
            if is_aspect(angle, major_aspects, orb):
                return False, current_sign, "Moon will make an aspect before changing signs."


    # If no aspects now and none before sign change, Moon is VOC
    return True, current_sign, "Moon is void of course."


# on run of the program
def main():
    # Get current UTC time
    ts = load.timescale()
    time = ts.now()

    # Check if Moon is void of course
    is_voc, sign, message = is_moon_void_of_course(time)

    return is_voc, sign, message