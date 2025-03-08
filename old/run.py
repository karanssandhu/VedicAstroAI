from flask import Flask, request, jsonify, render_template
from vedastro import *
from geopy.geocoders import Nominatim
from datetime import datetime

app = Flask(__name__)
geolocator = Nominatim(user_agent="vedic_astro_app")


# Helper function to get coordinates from location
def get_coordinates(location):
    try:
        loc = geolocator.geocode(location)
        return loc.longitude, loc.latitude
    except:
        return 0, 0  # Default to 0,0 if geocoding fails


# Helper function for personalized insights
def generate_insights(chart):
    insights = []
    asc_sign = chart['ascendant']['sign']
    insights.append(
        f"Your ascendant is in {asc_sign}, influencing your personality.")
    for planet in chart['planets']:
        name = planet['name']
        sign = planet['sign']
        insights.append(
            f"{name} in {sign} affects your {get_house_meaning(planet['house'])}."
        )
    return insights


def get_house_meaning(house):
    meanings = {
        1: "self",
        2: "wealth",
        3: "communication",
        4: "home",
        5: "creativity",
        6: "health",
        7: "relationships",
        8: "transformation",
        9: "philosophy",
        10: "career",
        11: "friendships",
        12: "spirituality"
    }
    return meanings.get(house, "life areas")


# Helper function for daily horoscope insights
def generate_transit_insights(birth_chart, transits):
    insights = []
    for transit in transits:
        for natal in birth_chart['planets']:
            aspect = get_aspect(transit['longitude'], natal['longitude'])
            if aspect:
                insights.append(
                    f"Transiting {transit['name']} {aspect} your natal {natal['name']}."
                )
    return insights


def get_aspect(long1, long2):
    diff = abs(long1 - long2) % 360
    if diff in [0, 180, 120, 60]:
        return {
            0: 'conjunct',
            180: 'opposite',
            120: 'trine',
            60: 'sextile'
        }[diff]
    return None


# Routes
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/calculate_chart', methods=['POST'])
def calculate_chart():
    data = request.json
    birth_date = data['date']  # "DD/MM/YYYY"
    birth_time = data['time']  # "HH:MM"
    birth_location = data['location']
    timezone = data['timezone']  # "+HH:MM"

    # Get coordinates
    lon, lat = get_coordinates(birth_location)
    geolocation = GeoLocation(birth_location, lon, lat)

    # Create Time object
    time_str = f"{birth_time} {birth_date} {timezone}"
    birth_time_obj = Time(time_str, geolocation)

    # Calculate planet and house data
    planet_data = Calculate.AllPlanetData(PlanetName.All, birth_time_obj)
    house_data = Calculate.AllHouseData(HouseName.All, birth_time_obj)

    # Format chart data
    chart_data = {
        'planets': [{
            'name': p.Name,
            'longitude': p.Longitude,
            'sign': p.Sign,
            'house': p.House
        } for p in planet_data],
        'houses': [{
            'name': h.Name,
            'cusp': h.Cusp
        } for h in house_data],
        'ascendant': {
            'sign': house_data[0].Sign,
            'longitude': house_data[0].Cusp
        }  # House1 is ascendant
    }
    return jsonify(chart_data)


@app.route('/daily_horoscope', methods=['POST'])
def daily_horoscope():
    data = request.json
    birth_chart = data['birth_chart']
    current_time = datetime.now().strftime("%H:%M %d/%m/%Y +00:00")
    current_geolocation = GeoLocation("Current", 0, 0)  # Global transits
    current_time_obj = Time(current_time, current_geolocation)

    transits = Calculate.AllPlanetData(PlanetName.All, current_time_obj)
    transit_data = [{
        'name': p.Name,
        'longitude': p.Longitude,
        'sign': p.Sign
    } for p in transits]

    insights = generate_transit_insights(birth_chart, transit_data)
    return jsonify({'insights': insights})


@app.route('/compatibility', methods=['POST'])
def compatibility():
    data = request.json
    chart1 = data['chart1']
    chart2 = data['chart2']

    moon1 = next(p for p in chart1['planets'] if p['name'] == 'Moon')['sign']
    moon2 = next(p for p in chart2['planets'] if p['name'] == 'Moon')['sign']

    compatible_signs = {
        'Aries': ['Leo', 'Sagittarius'],
        'Taurus': ['Virgo', 'Capricorn'],
        # Simplified; add more pairs as needed
    }
    score = 80 if moon2 in compatible_signs.get(moon1, []) else 50
    insight = f"Moon signs {moon1} and {moon2}: {'Harmonious' if score == 80 else 'Adjustments needed'}."

    return jsonify({'score': score, 'insight': insight})


# if __name__ == '__main__':
#     app.run(debug=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
