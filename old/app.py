from flask import Flask, render_template, request, jsonify, session
from vedastro import GeoLocation, Time, Calculate, PlanetName, HouseName, ZodiacName
import requests
import json
import os
from urllib.parse import quote
from dotenv import load_dotenv
import re
from timezonefinder import TimezoneFinder
from datetime import datetime
import pytz
from huggingface_hub import InferenceClient

# from transformers import pipeline

load_dotenv()

app = Flask(__name__)

# Set a secret key for session management

# Hugging Face API setup (replace with your token)
HF_API_TOKEN = os.environ['HF_API_TOKEN']

client = InferenceClient(
    provider="together",
    api_key=HF_API_TOKEN,
)

VED_API_KEY = os.environ['VED_API_KEY']
KARAN_API_KEY = os.environ['KARAN_API_KEY']
API_URL = "https://router.huggingface.co/together/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}
Calculate.SetAPIKey("0aRn6PrZof")

app.secret_key = os.environ.get('SECRET_KEY', KARAN_API_KEY)

# Load predefined interpretations
try:
    with open('interpretations.json', 'r') as f:
        INTERPRETATIONS = json.load(f)
except FileNotFoundError:
    # Provide fallback basic interpretations if file doesn't exist
    INTERPRETATIONS = {
        "Sun": {},
        "Moon": {},
        "Mars": {},
        "Mercury": {},
        "Jupiter": {},
        "Venus": {},
        "Saturn": {},
        "Rahu": {},
        "Ketu": {},
        "Ascendant": {}
    }
    print(
        "Warning: interpretations.json not found. Using empty interpretations."
    )

# Zodiac signs for reference
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Planet mapping - mapping PlanetName enum to display names
PLANET_DISPLAY_NAMES = {
    PlanetName.Sun: "Sun",
    PlanetName.Moon: "Moon",
    PlanetName.Mars: "Mars",
    PlanetName.Mercury: "Mercury",
    PlanetName.Jupiter: "Jupiter",
    PlanetName.Venus: "Venus",
    PlanetName.Saturn: "Saturn",
    PlanetName.Rahu: "Rahu",
    PlanetName.Ketu: "Ketu"
}

PLANET_SYMBOLS = {
    "Sun": "☉",
    "Moon": "☽",
    "Mars": "♂",
    "Mercury": "☿",
    "Jupiter": "♃",
    "Venus": "♀",
    "Saturn": "♄",
    "Rahu": "☊",
    "Ketu": "☋"
}


# Helper function to geocode a location
def geocode_location(location):
    try:
        encoded_location = quote(location)  # URL-encode the location
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_location}&format=json&limit=1"
        headers = {
            'User-Agent': 'VedicAstroAI/1.0'
        }  # Identify the app to the API
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]['display_name'], float(data[0]['lat']), float(
                    data[0]['lon'])
        return None, None, None  # Return None if no coordinates are found
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None, None, None


def get_timezone(latitude, longitude):
    obj = TimezoneFinder()
    timezone_name = obj.timezone_at(lng=longitude, lat=latitude)

    if timezone_name:
        tz = pytz.timezone(timezone_name)
        now = datetime.utcnow()
        offset_seconds = tz.utcoffset(now).total_seconds()
        offset_hours = int(offset_seconds // 3600)  # Get whole hours
        offset_minutes = int(abs(offset_seconds) % 3600) // 60  # Get minutes

        # Format as +hh:mm or -hh:mm
        sign = "+" if offset_hours >= 0 else "-"
        return f"{sign}{abs(offset_hours):02}:{offset_minutes:02}"

    return None


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/calculate', methods=['POST'])
def calculate_chart():
    try:
        # Extract form data
        date_str = request.form['date']  # Format: YYYY-MM-DD
        time_str = request.form['time']  # Format: HH:MM
        location = request.form['location']
        name = request.form['name']
        gender = request.form['gender']

        # Get latitude and longitude
        place_name, lat, lon = geocode_location(location)

        if lat is None or lon is None:
            return render_template(
                'home.html',
                error="Invalid location. Please enter a valid location.")

        # Format date and time for vedastro
        # Convert YYYY-MM-DD to DD/MM/YYYY
        day, month, year = date_str.split('-')[::-1]
        formatted_date = f"{day}/{month}/{year}"

        # Create Time and GeoLocation objects for vedastro
        geo_location = GeoLocation(place_name, lon, lat)

        # get the timezone based on the location
        timezone = get_timezone(lat, lon)


        birth_time = Time(f"{time_str} {formatted_date} +00:00",
                          geo_location)  # Assuming UTC

        # Get ascendant (House1)
        # After calculating house_data
        # Get ascendant (House1)
        house_data = Calculate.AllHouseData(HouseName.House1, birth_time)

        horoscopePredictions = Calculate.HoroscopePredictions(
            birth_time, "Empty")

        # Get the sign name directly
        asc_sign = house_data['HouseRasiSign']['Name']
        # If you need the sign number (1-12), find it in your SIGNS list
        asc_sign_num = SIGNS.index(
            asc_sign) + 1  # +1 to convert from 0-based to 1-based
        # Get the degrees
        asc_degree = float(
            house_data['HouseRasiSign']['DegreesIn']['TotalDegrees'])

        # Reasoning for ascendant
        asc_reasoning = (
            f"The Ascendant (Lagna) is calculated based on the exact time and location of birth. "
            f"At {date_str} {time_str} at latitude {lat}° and longitude {lon}°, the eastern horizon aligns with {asc_sign} "
            f"at {asc_degree:.2f} degrees. In Vedic astrology, this is the first house and sets the house system."
        )

        # Calculate planetary positions
        planets = []
        planet_list = [
            PlanetName.Sun, PlanetName.Moon, PlanetName.Mars,
            PlanetName.Mercury, PlanetName.Jupiter, PlanetName.Venus,
            PlanetName.Saturn, PlanetName.Rahu, PlanetName.Ketu
        ]

        for planet in planet_list:
            planet_data = Calculate.AllPlanetData(planet, birth_time)
            planet_name = PLANET_DISPLAY_NAMES[planet]

            # More defensive approach
            if 'PlanetRasiD1Sign' in planet_data and isinstance(
                    planet_data['PlanetRasiD1Sign'],
                    dict) and 'Name' in planet_data['PlanetRasiD1Sign']:
                sign = planet_data['PlanetRasiD1Sign']['Name']
            else:
                print(
                    f"Could not find sign name for {planet_name}, examining 'PlanetRasiD1Sign': {planet_data.get('PlanetRasiD1Sign', 'Key not found')}"
                )
                sign = "Unknown"

            # sign = SIGNS[sign_num - 1]
            sign_num = SIGNS.index(sign) + 1
            # degree = planet_data[0]['longitude']
            degree = float(
                planet_data['PlanetRasiD1Sign']['DegreesIn']['TotalDegrees'])

            # Calculate house (bhava) number based on whole sign system
            # In whole sign, house is based on offset from ascendant
            # house = ((sign_num - asc_sign_num) % 12) + 1
            house = ((sign_num - asc_sign_num) % 12) + 1
            # Predefined interpretation
            # interp = INTERPRETATIONS.get(planet_name, {}).get(sign, {}).get(
            #     str(house), "No specific interpretation available.")
            # lookup using planet name and sign name as Suninvirgo for example

            interpretation_key = f"{planet_name}In{sign}"
            interp = next((yoga["Description"] for yoga in horoscopePredictions
                           if yoga["Name"] == interpretation_key), "")

            # If no specific planet-in-sign interpretation found, check for planet-in-house
            if not interp:
                house_key = f"{planet_name}InHouse{house}"
                interp = next((yoga["Description"]
                               for yoga in horoscopePredictions
                               if yoga["Name"] == house_key),
                              "No specific interpretation available.")

            planets.append({
                'name':
                planet_name,
                'sign':
                sign,
                'degree':
                degree,
                'house':
                house,
                'interpretation':
                interp,
                'reasoning':
                (f"{planet_name} is at {degree:.2f}° in {sign}. In the whole sign house system, "
                 f"since the Ascendant is {asc_sign}, {sign} becomes the {house}th house."
                 )
            })

        chart_data = {
            'ascendant':
            asc_sign,
            'asc_degree':
            asc_degree,
            'asc_reasoning':
            asc_reasoning,
            'planets':
            planets,
            'birth_details':
            f"Birth: {date_str} {time_str}, Lat: {lat}°, Lon: {lon}°"
        }

        try:
            # Panchanga Table
            panchanga_table = Calculate.PanchangaTable(birth_time)

            # Lagna Sign Name
            lagna_sign_name = Calculate.LagnaSignName(birth_time)

            # Bhinnashtakavarga Chart
            bhinnashtakavarga = Calculate.BhinnashtakavargaChart(birth_time)

            # Gulika Longitude
            gulika_longitude = Calculate.GulikaLongitude(birth_time)
        except Exception as chart_error:
            print(f"Error calculating additional charts: {chart_error}")
            panchanga_table = {}
            lagna_sign_name = {}
            bhinnashtakavarga = {}
            gulika_longitude = {}

        # Update chart_data with additional charts
        chart_data.update({
            'panchanga_table': panchanga_table,
            'lagna_sign_name': lagna_sign_name,
            'bhinnashtakavarga': bhinnashtakavarga,
            'gulika_longitude': gulika_longitude
        })

        session['birth_time'] = str(birth_time)  # Store birth_time in session
        session['chart_data'] = chart_data  # Store chart_data in session

        return render_template('chart.html',
                               chart=chart_data,
                               SIGNS=SIGNS,
                               PLANET_SYMBOLS=PLANET_SYMBOLS)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error calculating chart: {error_details}")
        return render_template('home.html',
                               error=f"Error calculating chart: {str(e)}")


@app.route('/query', methods=['POST'])
def handle_query():
    try:
        data = request.json
        if not data or 'chart' not in data or 'question' not in data:
            return jsonify({
                'response': "Error: Invalid request data",
                'reasoning': "Missing chart or question data"
            }), 400

        chart = data['chart']
        question = data['question'].strip().lower()

        # Get the horoscope predictions for reference
        birth_details = chart.get('birth_details', '')
        # Parse birth details to recreate Time and GeoLocation objects
        try:
            # Example format: "Birth: 2000-01-01 12:00, Lat: 40.0°, Lon: -74.0°"
            birth_parts = birth_details.split(', ')
            date_time_str = birth_parts[0].replace('Birth: ', '')
            lat = float(birth_parts[1].replace('Lat: ', '').replace('°', ''))
            lon = float(birth_parts[2].replace('Lon: ', '').replace('°', ''))

            # Recreate objects needed for API call
            geo_location = GeoLocation("Query Location", lon, lat)

            # Convert date format if needed
            date_str, time_str = date_time_str.split(' ')
            day, month, year = date_str.split('-')[::-1]
            formatted_date = f"{day}/{month}/{year}"

            birth_time = Time(f"{time_str} {formatted_date} +00:00",
                              geo_location)
            horoscopePredictions = Calculate.HoroscopePredictions(
                birth_time, "Empty")
        except Exception as e:
            print(f"Error recreating birth time: {e}")
            horoscopePredictions = []

        # Handle predefined queries
        if "sun sign" in question:
            sun = next((p for p in chart['planets'] if p['name'] == 'Sun'),
                       None)
            if sun:
                response = f"Your Sun sign is {sun['sign']}."
                reasoning = "The Sun sign is determined by the zodiac sign the Sun occupies at your birth time."
            else:
                response = "Could not determine your Sun sign."
                reasoning = "Sun position data is missing from the chart."
        elif "ascendant" in question or "rising sign" in question:
            asc_key = f"{chart['ascendant']}Rising"
            asc_interp = next(
                (yoga["Description"]
                 for yoga in horoscopePredictions if yoga["Name"] == asc_key),
                "")

            if asc_interp:
                response = f"Your Ascendant is {chart['ascendant']}. {asc_interp}"
            else:
                response = f"Your Ascendant is {chart['ascendant']}. This shapes your personality and how others perceive you."

            reasoning = f"The Ascendant in {chart['ascendant']} shapes your personality and life approach."
        elif any(planet.lower() in question
                 for planet in [p['name'].lower() for p in chart['planets']]):
            # Find which planet is being asked about
            planet_names = [p['name'].lower() for p in chart['planets']]
            asked_planet = next((p for p in planet_names if p in question),
                                None)

            if asked_planet:
                planet_info = next((p for p in chart['planets']
                                    if p['name'].lower() == asked_planet),
                                   None)
                if planet_info:
                    response = f"Your {planet_info['name']} is in {planet_info['sign']} in the {planet_info['house']}th house. {planet_info['interpretation']}"
                    reasoning = planet_info['reasoning']
                else:
                    response = f"Could not find information about {asked_planet} in your chart."
                    reasoning = "The planet data might be missing from the chart."
            else:
                response = "I'm not sure which planet you're asking about."
                reasoning = "Please specify a planet name clearly in your question."
        elif "yoga" in question or "prediction" in question:
            # Find relevant yogas from horoscopePredictions
            relevant_yogas = [
                yoga for yoga in horoscopePredictions
                if not yoga["Name"].endswith("InHouse")
                and not yoga["Name"].endswith("Rising") and not any(
                    yoga["Name"].startswith(f"{p}In") for p in [
                        "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
                        "Saturn", "Rahu", "Ketu"
                    ])
            ]

            if relevant_yogas:
                yoga_descriptions = [
                    f"{yoga['Name']}: {yoga['Description']}"
                    for yoga in relevant_yogas[:3]
                ]
                response = "Based on your chart, here are some key yogas (planetary combinations) that apply to you:\n\n" + "\n\n".join(
                    yoga_descriptions)
                reasoning = "These yogas are determined by the relative positions of planets in your birth chart."
            else:
                response = "I couldn't find any specific yogas in your chart data."
                reasoning = "The horoscope prediction data might not contain yoga information."
        else:
            # Use Hugging Face model for general queries
            prompt = generate_prompt(chart, question)
            response_data = query_hf_api(prompt)

            # Handle possible errors or unexpected responses from the API
            if isinstance(response_data, dict) and 'error' in response_data:
                response = f"API Error: {response_data['error']}"
                reasoning = "The AI model encountered an error processing your question."
            elif len(response_data) > 0:
                response = response_data
                reasoning = (
                    f"This response is generated by an AI model trained on general text, adapted to your chart: "
                    f"Ascendant in {chart['ascendant']}, planets positioned as shown earlier."
                )
            else:
                response = "Could not generate a response from the AI model."
                reasoning = "The AI model returned an unexpected response format."

        return jsonify({'response': response, 'reasoning': reasoning})
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Query error: {error_details}")
        return jsonify({
            'response': f"Error: {str(e)}",
            'reasoning': "Something went wrong with the query."
        }), 400


def generate_prompt(chart, question):
    prompt = (
        "In Vedic astrology, based on the following birth chart:\n"
        f"Ascendant: {chart['ascendant']} at {chart['asc_degree']:.2f}°\n")
    for planet in chart['planets']:
        prompt += f"{planet['name']}: {planet['sign']} at {planet['degree']:.2f} in house {planet['house']}\n"
    prompt += f"Question: {question}\nAnswer in a concise tone:"
    return prompt


def query_hf_api(prompt):
    try:
        # Use the defined API_URL from your code
        # api_url = API_URL  # "https://router.huggingface.co/together/v1/chat/completions"
        # payload = {
        #     "model": "deepseek-ai/DeepSeek-R1",
        #     "messages": [{
        #         "role": "user",
        #         "content": prompt
        #     }],  # prompt as a string
        #     "max_tokens": 1200,
        #     "stream": False  # Use boolean, not string 'false'
        # }
        # print(
        #     f"Sending request to {api_url} with payload: {json.dumps(payload, indent=2)}"
        # )

        # response = requests.post(
        #     api_url,
        #     headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
        #     json=payload)
        # response.raise_for_status()

        messages = [{"role": "user", "content": prompt}]

        completion = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-R1",
            messages=messages,
            max_tokens=500,
        )

        response_json = completion.choices[0].message['content']
        # parse <think> </think> and give only text outside of it
        # response_json = re.sub(r'<think>.*?</think>', '', response_json)

        response_json = re.sub(r'<think>.*?</think>\s*',
                               '',
                               response_json,
                               flags=re.DOTALL)

        print(f"API Response: {json.dumps(response_json, indent=2)}")
        return response_json
    except requests.exceptions.RequestException as e:
        print(f"HF API request error: {e}")
        return {"error": str(e)}


@app.template_filter('get_planet_symbol')
def get_planet_symbol_filter(planet_name):
    symbols = {
        "Sun": "☉",
        "Moon": "☽",
        "Mars": "♂",
        "Mercury": "☿",
        "Jupiter": "♃",
        "Venus": "♀",
        "Saturn": "♄",
        "Rahu": "☊",
        "Ketu": "☋"
    }
    return symbols.get(planet_name, planet_name)


@app.route('/daily', methods=['GET'])
def daily_horoscope():
    # Get the user's birth chart from session or request
    if 'birth_time' not in session and 'chart_data' not in session:
        return redirect(
            url_for('home', message="Please create your birth chart first"))
    
    geo_location = None
    birth_time = None

    # Either use stored birth time or recreate it
    if 'chart_data' in session:
        # Recreate birth time from stored chart data
        chart_data = session['chart_data']
        birth_details = chart_data.get('birth_details', '')
        # Parse birth details to recreate Time and GeoLocation objects
        try:
            birth_parts = birth_details.split(', ')
            date_time_str = birth_parts[0].replace('Birth: ', '')
            lat = float(birth_parts[1].replace('Lat: ', '').replace('°', ''))
            lon = float(birth_parts[2].replace('Lon: ', '').replace('°', ''))

            geo_location = GeoLocation("Birth Location", lon, lat)
            date_str, time_str = date_time_str.split(' ')
            day, month, year = date_str.split('-')[::-1]
            formatted_date = f"{day}/{month}/{year}"

            birth_time = Time(f"{time_str} {formatted_date} +00:00",
                              geo_location)
        except Exception as e:
            return render_template(
                'home.html', error=f"Error recreating birth time: {str(e)}")

    # Calculate current transits
    current_time = datetime.utcnow()
    # get utc offset
    utc_offset = get_timezone(geo_location.latitude, geo_location.longitude)



    current_time = Time(f"{current_time.strftime('%H:%M:%S')} {current_time.strftime('%d/%m/%Y')} {utc_offset}", geo_location)
    

    # Get transit positions for all planets
    transit_planets = []
    for planet in [
            PlanetName.Sun, PlanetName.Moon, PlanetName.Mars,
            PlanetName.Mercury, PlanetName.Jupiter, PlanetName.Venus,
            PlanetName.Saturn, PlanetName.Rahu, PlanetName.Ketu
    ]:
        transit_data = Calculate.AllPlanetData(planet, current_time)
        planet_name = PLANET_DISPLAY_NAMES[planet]

        if 'PlanetRasiD1Sign' in transit_data and isinstance(
                transit_data['PlanetRasiD1Sign'],
                dict) and 'Name' in transit_data['PlanetRasiD1Sign']:
            sign = transit_data['PlanetRasiD1Sign']['Name']
        else:
            sign = "Unknown"

        degree = float(
            transit_data['PlanetRasiD1Sign']['DegreesIn']['TotalDegrees'])

        # Get birth chart position
        birth_planet_data = Calculate.AllPlanetData(planet, birth_time)
        birth_sign = birth_planet_data['PlanetRasiD1Sign']['Name']

        # Calculate transit aspects to natal planets
        aspects = []
        for natal_planet in [
                PlanetName.Sun, PlanetName.Moon, PlanetName.Mars,
                PlanetName.Mercury, PlanetName.Jupiter, PlanetName.Venus,
                PlanetName.Saturn, PlanetName.Rahu, PlanetName.Ketu
        ]:
            if natal_planet != planet:  # Skip comparing a planet to itself
                natal_data = Calculate.AllPlanetData(natal_planet, birth_time)
                natal_degree = float(natal_data['PlanetRasiD1Sign']
                                     ['DegreesIn']['TotalDegrees'])
                natal_sign_num = SIGNS.index(
                    natal_data['PlanetRasiD1Sign']['Name'])

                transit_sign_num = SIGNS.index(sign)

                # Calculate the angular difference
                total_natal_deg = natal_sign_num * 30 + natal_degree
                total_transit_deg = transit_sign_num * 30 + degree

                angle_diff = (total_transit_deg - total_natal_deg) % 360

                # Check for major aspects (conjunction, opposition, trine, square, sextile)
                aspect_type = None
                if 0 <= angle_diff <= 10 or 350 <= angle_diff <= 360:
                    aspect_type = "conjunction"
                elif 170 <= angle_diff <= 190:
                    aspect_type = "opposition"
                elif 110 <= angle_diff <= 130:
                    aspect_type = "trine"
                elif 80 <= angle_diff <= 100:
                    aspect_type = "square"
                elif 50 <= angle_diff <= 70:
                    aspect_type = "sextile"

                if aspect_type:
                    aspects.append({
                        "planet": PLANET_DISPLAY_NAMES[natal_planet],
                        "aspect_type": aspect_type,
                        "angle": round(angle_diff, 2)
                    })

        # Generate interpretation for this transit
        interpretation = generate_transit_interpretation(
            planet_name, sign, aspects)

        transit_planets.append({
            "name": planet_name,
            "sign": sign,
            "degree": degree,
            "natal_sign": birth_sign,
            "aspects": aspects,
            "interpretation": interpretation
        })

    # Generate overall daily horoscope
    daily_message = generate_daily_horoscope(transit_planets, birth_time)

    return render_template(
        'daily.html',
        transit_planets=transit_planets,
        daily_message=daily_message,
        current_date=current_time,
        PLANET_SYMBOLS=PLANET_SYMBOLS)


def generate_transit_interpretation(planet, sign, aspects):
    """Generate an interpretation for a transit planet position."""
    # Basic template interpretations - in production, use more detailed ones or AI
    templates = {
        "Sun":
        f"The Sun in {sign} brings focus to your identity and ego expression. It's a time to shine in {sign} related areas.",
        "Moon":
        f"The Moon in {sign} colors your emotional landscape today. You may feel the {sign} qualities strongly in your reactions.",
        "Mercury":
        f"Mercury in {sign} influences how you think and communicate. Expect your mental processes to take on {sign} characteristics.",
        "Venus":
        f"Venus in {sign} affects your relationships and what you find beautiful. {sign} energy dominates your social connections.",
        "Mars":
        f"Mars in {sign} directs your energy and drive. You're motivated by {sign} principles and may act with {sign} characteristics.",
        "Jupiter":
        f"Jupiter in {sign} expands your opportunities in {sign}-related areas. Growth and learning come through these themes.",
        "Saturn":
        f"Saturn in {sign} creates structure and possibly limitations in {sign} areas. Important lessons come through these themes.",
        "Rahu":
        f"Rahu (North Node) in {sign} points to your karmic direction. You're being pushed to develop {sign} qualities.",
        "Ketu":
        f"Ketu (South Node) in {sign} shows what you're releasing. You may need to let go of outdated {sign} patterns."
    }

    base_interpretation = templates.get(
        planet,
        f"{planet} in {sign} influences your chart in ways specific to these energies."
    )

    # Add aspect interpretations if any
    if aspects:
        aspect_text = "\n\nSignificant aspects today:"
        for aspect in aspects[:3]:  # Limit to 3 most significant aspects
            aspect_text += f"\n- {planet} makes a {aspect['aspect_type']} to your natal {aspect['planet']}, "

            if aspect['aspect_type'] == "conjunction":
                aspect_text += f"intensifying {aspect['planet']} themes in your life."
            elif aspect['aspect_type'] == "opposition":
                aspect_text += f"creating tension or awareness around {aspect['planet']} themes."
            elif aspect['aspect_type'] == "trine":
                aspect_text += f"bringing ease and flow to {aspect['planet']} areas."
            elif aspect['aspect_type'] == "square":
                aspect_text += f"challenging you to grow through {aspect['planet']} lessons."
            elif aspect['aspect_type'] == "sextile":
                aspect_text += f"offering opportunities related to {aspect['planet']} themes."

        base_interpretation += aspect_text

    return base_interpretation


def generate_daily_horoscope(transits, birth_time):
    """Generate an overall daily horoscope based on all transits."""
    # Get user's moon sign as it's important in Vedic astrology
    moon_data = Calculate.AllPlanetData(PlanetName.Moon, birth_time)
    moon_sign = moon_data['PlanetRasiD1Sign']['Name']

    # Get user's ascendant
    asc_data = Calculate.AllHouseData(HouseName.House1, birth_time)
    asc_sign = asc_data['HouseRasiSign']['Name']

    # Create personalized horoscope intro
    intro = f"Daily Vedic Forecast for {asc_sign} Ascendant and {moon_sign} Moon"

    # Find the most significant transit aspects (simplistic approach - can be improved)
    significant_aspects = []
    for transit in transits:
        for aspect in transit['aspects']:
            if aspect['aspect_type'] in ['conjunction', 'opposition']:
                significant_aspects.append({
                    'transit_planet': transit['name'],
                    'aspect_type': aspect['aspect_type'],
                    'natal_planet': aspect['planet']
                })

    # Generate message based on transits and aspects
    message = (f"{intro}\n\n"
               f"Today, the cosmic energies are particularly focused on your ")

    # Highlight important houses based on where the Sun and Moon are transiting
    sun_transit = next((t for t in transits if t['name'] == 'Sun'), None)
    moon_transit = next((t for t in transits if t['name'] == 'Moon'), None)

    house_themes = {
        1: "self, identity, and personal projects",
        2: "finances, possessions, and values",
        3: "communication, siblings, and short trips",
        4: "home, family, and emotional foundations",
        5: "creativity, romance, and self-expression",
        6: "work, health, and daily routines",
        7: "relationships, partnerships, and contracts",
        8: "transformation, shared resources, and the deeper aspects of life",
        9: "higher learning, philosophy, and long-distance travel",
        10: "career, public image, and life direction",
        11: "friendships, groups, and future aspirations",
        12: "spirituality, unconscious patterns, and private matters"
    }

    # Calculate which houses the Sun and Moon are transiting (would need more logic)
    # This is a simplified placeholder - in real app, calculate based on ascendant
    sun_house = (SIGNS.index(sun_transit['sign']) -
                 SIGNS.index(asc_sign)) % 12 + 1
    moon_house = (SIGNS.index(moon_transit['sign']) -
                  SIGNS.index(asc_sign)) % 12 + 1

    message += f"{house_themes.get(sun_house, 'various areas of life')} and {house_themes.get(moon_house, 'emotional landscape')}. "

    # Add details about significant aspects if any
    if significant_aspects:
        aspect = significant_aspects[
            0]  # Just use the first one for simplicity
        message += f"The transit of {aspect['transit_planet']} making a {aspect['aspect_type']} to your natal {aspect['natal_planet']} "

        if aspect['aspect_type'] == 'conjunction':
            message += f"brings intense focus to matters related to {aspect['natal_planet']} in your chart. "
        elif aspect['aspect_type'] == 'opposition':
            message += f"creates dynamic tension that can lead to important realizations about {aspect['natal_planet']} themes. "

    # Add general advice
    message += "\n\nToday is favorable for: "

    # Based on Moon's sign, give appropriate advice
    moon_element_map = {
        "Aries": "fire",
        "Leo": "fire",
        "Sagittarius": "fire",
        "Taurus": "earth",
        "Virgo": "earth",
        "Capricorn": "earth",
        "Gemini": "air",
        "Libra": "air",
        "Aquarius": "air",
        "Cancer": "water",
        "Scorpio": "water",
        "Pisces": "water"
    }

    moon_element = moon_element_map.get(moon_transit['sign'], "unknown")

    if moon_element == "fire":
        message += "Taking initiative, creative projects, and physical activity. Channel your energy constructively."
    elif moon_element == "earth":
        message += "Practical matters, financial planning, and completing tasks. Ground yourself in the physical world."
    elif moon_element == "air":
        message += "Communication, social connections, and intellectual pursuits. Express your ideas and connect with others."
    elif moon_element == "water":
        message += "Emotional healing, intuitive work, and nurturing relationships. Honor your feelings and inner wisdom."

    return message


@app.route('/compatibility', methods=['GET', 'POST'])
def compatibility():
    if request.method == 'GET':
        return render_template('compatibility_form.html')

    try:
        # First person's data (could be from session if user is logged in)
        partner_name = request.form['partner_name']
        date1_str = request.form['date1']
        time1_str = request.form['time1']
        location1 = request.form['location1']

        # Second person's data
        # date2_str = request.form['date2']
        # time2_str = request.form['time2']
        # location2 = request.form['location2'] 
        partner_name2 = None
        date2_str, time2_str, location2 = None, None, None
        place2_name = None
        lat2, lon2 = None, None
        birth_time2 = None
        local = None
        # get date 2, time 2 and location 2 from the session if available
        if date2_str is None and time2_str is None and location2 is None:
            chart_data = session['chart_data']
            birth_time2 = session['birth_time']
            birth_details = chart_data.get('birth_details', '')
            lat2, lon2, location2 = None, None, None
            if chart_data:
                birth_parts = birth_details.split(', ')
                date_time_str = birth_parts[0].replace('Birth: ', '')
                date2_str = date_time_str.split(' ')[0]
                time2_str = date_time_str.split(' ')[1]
                lat2 = float(birth_parts[1].replace('Lat: ', '').replace('°', ''))
                lon2 = float(birth_parts[2].replace('Lon: ', '').replace('°', ''))
                location2 = GeoLocation("Birth Location", lon2, lat2)
                partner_name2 = chart_data.get('ascendant', None)
                local = True
        

        # # Second person's data
        # chart_data = session['chart_data']
        # birth_details = chart_data.get('birth_details', '')
        # lat2, lon2, location2 = None, None, None
        # if chart_data:
        #     birth_parts = birth_details.split(', ')
        #     date_time_str = birth_parts[0].replace('Birth: ', '')
        #     date2_str = date_time_str.split(' ')[0]
        #     time2_str = date_time_str.split(' ')[1]
        #     lat2 = float(birth_parts[1].replace('Lat: ', '').replace('°', ''))
        #     lon2 = float(birth_parts[2].replace('Lon: ', '').replace('°', ''))
        #     location2 = GeoLocation("Birth Location", lon2, lat2)


        #     print(date2_str, time2_str, location2)
        
        # Validate input
        if not date1_str or not time1_str or not location1 or not date2_str or not time2_str or not location2:
            return render_template('compatibility_form.html',
                                   error="Please fill out all fields.")
        
        if partner_name is None or partner_name2 is None:
            return render_template('compatibility_form.html',
                                   error="Please fill out all fields.")


        # Process first person's location
        place1_name, lat1, lon1 = geocode_location(location1)
        if lat1 is None or lon1 is None:
            return render_template('compatibility_form.html',
                                   error="Invalid first location.")
        
        if lat2 is None or lon2 is None:
            return render_template('compatibility_form.html',
                                   error="Invalid second location.")
        
        if location2 is None:
            place2_name, lat2, lon2 = geocode_location(location2)


        # Format dates for vedastro
        day1, month1, year1 = date1_str.split('-')[::-1]
        formatted_date1 = f"{day1}/{month1}/{year1}"

        if birth_time2 is None:
            day2, month2, year2 = date2_str.split('-')[::-1]
            formatted_date2 = f"{day2}/{month2}/{year2}"

        # Create Time and GeoLocation objects
        geo_location1 = GeoLocation(place1_name, lon1, lat1)
        utc_offset1 = get_timezone(lat1, lon1)
        birth_time1 = Time(f"{time1_str} {formatted_date1} {utc_offset1}",
                           geo_location1)
        if local is True:
            geo_location2 = location2
        else: 
            geo_location2 = GeoLocation(place2_name, lon2, lat2)

        if birth_time2 is None:
            utc_offset2 = get_timezone(lat2, lon2)
            birth_time2 = Time(f"{time2_str} {formatted_date2} {utc_offset2}",
                            geo_location2)

        # Calculate compatibility
        compatibility_result = calculate_compatibility(birth_time1,
                                                       birth_time2)
        
        print(compatibility_result)


        return render_template('compatibility_form.html',
                               compatibility=compatibility_result,
                               person1={
                                   "date": date1_str,
                                   "time": time1_str,
                                   "location": place1_name
                               },
                               person2={
                                   "date": date2_str,
                                   "time": time2_str,
                                   "location": location2
                               })

    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error calculating compatibility: {error_details}")
        return render_template('compatibility_form.html',
                               error=f"Error: {str(e)}")


def calculate_compatibility(birth_time1, birth_time2):

    return Calculate.MatchReport(birth_time1, birth_time2)
    """Calculate compatibility between two birth charts."""
    # Initialize compatibility scores
    compatibility = {
        "overall_score": 0,
        "emotional_compatibility": 0,
        "communication_compatibility": 0,
        "physical_compatibility": 0,
        "spiritual_compatibility": 0,
        "longevity_potential": 0,
        "areas": []
    }

    # Get moon signs (very important in Vedic compatibility)
    moon1_data = Calculate.AllPlanetData(PlanetName.Moon, birth_time1)
    moon2_data = Calculate.AllPlanetData(PlanetName.Moon, birth_time2)

    moon1_sign = moon1_data['PlanetRasiD1Sign']['Name']
    moon2_sign = moon2_data['PlanetRasiD1Sign']['Name']

    # Calculate Moon Sign Compatibility (Guna Milan / Ashtakoot)
    moon1_nakshatra = Calculate.Nakshatra(PlanetName.Moon, birth_time1)
    moon2_nakshatra = Calculate.Nakshatra(PlanetName.Moon, birth_time2)

    # In production, implement the full 36-point Guna Milan system
    # This is a simplified version
    nadi_points = 8 if moon1_nakshatra['Pada'] != moon2_nakshatra['Pada'] else 0

    # Calculate moon sign distance (important for emotional compatibility)
    moon1_index = SIGNS.index(moon1_sign)
    moon2_index = SIGNS.index(moon2_sign)
    moon_distance = (moon2_index - moon1_index) % 12

    # Vedic astrology considers certain distances harmonious
    harmonious_distances = [3, 5, 7, 9, 11]  # Trine, sextile, etc.
    if moon_distance in harmonious_distances:
        emotional_score = 80 + (moon_distance * 2
                                )  # Higher score for more harmonious aspects
    elif moon_distance == 0:  # Same sign
        emotional_score = 70  # Good but can be too similar
    elif moon_distance == 6:  # Opposition
        emotional_score = 50  # Can be challenging but balancing
    else:
        emotional_score = 40 + (moon_distance * 3)  # Other aspects

    emotional_score = min(100, emotional_score)  # Cap at 100
    compatibility["emotional_compatibility"] = emotional_score

    # Communication compatibility (Mercury)
    mercury1_data = Calculate.AllPlanetData(PlanetName.Mercury, birth_time1)
    mercury2_data = Calculate.AllPlanetData(PlanetName.Mercury, birth_time2)

    mercury1_sign = mercury1_data['PlanetRasiD1Sign']['Name']
    mercury2_sign = mercury2_data['PlanetRasiD1Sign']['Name']

    mercury1_index = SIGNS.index(mercury1_sign)
    mercury2_index = SIGNS.index(mercury2_sign)
    mercury_distance = (mercury2_index - mercury1_index) % 12

    if mercury_distance in [0, 3, 4, 5, 9]:  # Harmonious for communication
        communication_score = 80 + (mercury_distance * 2)
    elif mercury_distance == 6:  # Opposition can be good for debate but may lead to arguments
        communication_score = 60
    else:
        communication_score = 50 + (mercury_distance * 2)

    communication_score = min(100, communication_score)
    compatibility["communication_compatibility"] = communication_score

    # Physical compatibility (Mars and Venus)
    venus1_data = Calculate.AllPlanetData(PlanetName.Venus, birth_time1)
    mars2_data = Calculate.AllPlanetData(PlanetName.Mars, birth_time2)

    venus1_sign = venus1_data['PlanetRasiD1Sign']['Name']
    mars2_sign = mars2_data['PlanetRasiD1Sign']['Name']

    # For heterosexual compatibility traditionally: venus of person 1 and mars of person 2
    # In a full app, you would check relationship type and adjust accordingly
    venus1_index = SIGNS.index(venus1_sign)
    mars2_index = SIGNS.index(mars2_sign)

    venus_mars_distance = (mars2_index - venus1_index) % 12

    if venus_mars_distance in [1, 3, 5, 7, 9, 11]:  # Harmonious aspects
        physical_score = 80 + (venus_mars_distance * 1.5)
    elif venus_mars_distance == 0:  # Conjunction - strong attraction
        physical_score = 90
    else:
        physical_score = 50 + (venus_mars_distance * 3)

    physical_score = min(100, physical_score)
    compatibility["physical_compatibility"] = physical_score

    # Spiritual compatibility (Jupiter and Saturn)
    jupiter1_data = Calculate.AllPlanetData(PlanetName.Jupiter, birth_time1)
    jupiter2_data = Calculate.AllPlanetData(PlanetName.Jupiter, birth_time2)

    jupiter1_sign = jupiter1_data['PlanetRasiD1Sign']['Name']
    jupiter2_sign = jupiter2_data['PlanetRasiD1Sign']['Name']

    jupiter1_index = SIGNS.index(jupiter1_sign)
    jupiter2_index = SIGNS.index(jupiter2_sign)

    jupiter_distance = (jupiter2_index - jupiter1_index) % 12

    if jupiter_distance in [0, 5, 9]:  # Harmonious for spiritual values
        spiritual_score = 85 + (jupiter_distance * 1.5)
    else:
        spiritual_score = 60 + (jupiter_distance * 2)

    spiritual_score = min(100, spiritual_score)
    compatibility["spiritual_compatibility"] = spiritual_score

    # Calculate overall score (weighted average)
    overall_score = ((emotional_score * 0.35) + (communication_score * 0.25) +
                     (physical_score * 0.2) + (spiritual_score * 0.2))

    compatibility["overall_score"] = round(overall_score)

    # Add Mangal Dosha (Mars affliction) check
    mars1_data = Calculate.AllPlanetData(PlanetName.Mars, birth_time1)
    mars1_house = (SIGNS.index(mars1_data['PlanetRasiD1Sign']['Name']) -
                   SIGNS.index(
                       Calculate.AllHouseData(HouseName.House1, birth_time1)
                       ['HouseRasiSign']['Name'])) % 12 + 1

    mars2_data = Calculate.AllPlanetData(PlanetName.Mars, birth_time2)
    mars2_house = (SIGNS.index(mars2_data['PlanetRasiD1Sign']['Name']) -
                   SIGNS.index(
                       Calculate.AllHouseData(HouseName.House1, birth_time2)
                       ['HouseRasiSign']['Name'])) % 12 + 1

    mangal_dosha_houses = [1, 4, 7, 8, 12]

    person1_mangal_dosha = mars1_house in mangal_dosha_houses
    person2_mangal_dosha = mars2_house in mangal_dosha_houses

    # In traditional matching, if both have it or neither has it, they're compatible
    mangal_compatible = (person1_mangal_dosha == person2_mangal_dosha)

    if not mangal_compatible:
        # Reduce overall score if Mangal Dosha is not compatible
        compatibility["overall_score"] = max(
            50, compatibility["overall_score"] - 15)
        compatibility["areas"].append({
            "title": "Mangal Dosha (Mars) Concern",
            "description":
            "There may be challenges due to Mars placement. One person has Mangal Dosha and the other doesn't, which traditionally suggests potential conflicts.",
            "score": 40
        })

    # Add areas of strength and weakness
    if compatibility["emotional_compatibility"] >= 75:
        compatibility["areas"].append({
            "title":
            "Strong Emotional Connection",
            "description":
            f"The Moon signs ({moon1_sign} and {moon2_sign}) are harmoniously placed, suggesting a natural emotional understanding.",
            "score":
            compatibility["emotional_compatibility"]
        })
    elif compatibility["emotional_compatibility"] <= 60:
        compatibility["areas"].append({
            "title":
            "Emotional Adjustment Needed",
            "description":
            f"The Moon signs ({moon1_sign} and {moon2_sign}) may create emotional misunderstandings. Patience and communication will be important.",
            "score":
            compatibility["emotional_compatibility"]
        })

    if compatibility["communication_compatibility"] >= 75:
        compatibility["areas"].append({
            "title":
            "Excellent Communication",
            "description":
            f"Mercury positions suggest you understand each other's thought processes naturally.",
            "score":
            compatibility["communication_compatibility"]
        })

    if compatibility["physical_compatibility"] >= 80:
        compatibility["areas"].append({
            "title":
            "Strong Physical Attraction",
            "description":
            "The Mars-Venus connection indicates a powerful physical chemistry.",
            "score":
            compatibility["physical_compatibility"]
        })

    # Set longevity potential based on overall compatibility
    if compatibility["overall_score"] >= 80:
        compatibility["longevity_potential"] = "Excellent"
    elif compatibility["overall_score"] >= 70:
        compatibility["longevity_potential"] = "Very Good"
    elif compatibility["overall_score"] >= 60:
        compatibility["longevity_potential"] = "Good"
    elif compatibility["overall_score"] >= 50:
        compatibility["longevity_potential"] = "Fair"
    else:
        compatibility["longevity_potential"] = "Challenging"

    return compatibility


@app.route('/dashas', methods=['GET'])
def dasha_periods():
    # Get the user's birth chart from session or request
    if 'birth_time' not in session and 'chart_data' not in session:
        return redirect(
            url_for('home', message="Please create your birth chart first"))

    # Either use stored birth time or recreate it
    if 'birth_time' in session:
        birth_time = session['birth_time']
    else:
        # Recreate birth time from stored chart data
        chart_data = session['chart_data']
        birth_details = chart_data.get('birth_details', '')
        # Parse birth details to recreate Time and GeoLocation objects
        try:
            birth_parts = birth_details.split(', ')
            date_time_str = birth_parts[0].replace('Birth: ', '')
            lat = float(birth_parts[1].replace('Lat: ', '').replace('°', ''))
            lon = float(birth_parts[2].replace('Lon: ', '').replace('°', ''))

            geo_location = GeoLocation("Birth Location", lon, lat)
            date_str, time_str = date_time_str.split(' ')
            day, month, year = date_str.split('-')[::-1]
            formatted_date = f"{day}/{month}/{year}"

            birth_time = Time(f"{time_str} {formatted_date} +00:00",
                              geo_location)
        except Exception as e:
            return render_template(
                'home.html', error=f"Error recreating birth time: {str(e)}")

    # Calculate Vimshottari Dasha periods
    try:
        # Get moon nakshatra for Vimshottari Dasha calculation
        moon_nakshatra = Calculate.Nakshatra(PlanetName.Moon, birth_time)
        nakshatra_name = moon_nakshatra['Name']
        nakshatra_lord = moon_nakshatra['Lord']
        nakshatra_pada = moon_nakshatra['Pada']

        # Calculate dasha balance
        dasha_balance = Calculate.VimshottariDashaBalance(birth_time)

        # Calculate current dasha
        current_date = Time.Now()
        current_mahadasha = Calculate.VimshottariDashaCurrent(
            birth_time, current_date)

        # Import datetime for date calculations
        import datetime
        from dateutil.relativedelta import relativedelta

        # Calculate all dasha periods
        birth_date = birth_time.GetGregorianDateTime()
        dashas = []

        # Define dasha lords and their durations in years
        dasha_lords = {
            "Ketu": 7,
            "Venus": 20,
            "Sun": 6,
            "Moon": 10,
            "Mars": 7,
            "Rahu": 18,
            "Jupiter": 16,
            "Saturn": 19,
            "Mercury": 17
        }

        # Get starting lord based on nakshatra
        nakshatra_to_lord = {
            "Ashwini": "Ketu",
            "Bharani": "Venus",
            "Krittika": "Sun",
            "Rohini": "Moon",
            "Mrigashira": "Mars",
            "Ardra": "Rahu",
            "Punarvasu": "Jupiter",
            "Pushya": "Saturn",
            "Ashlesha": "Mercury",
            "Magha": "Ketu",
            "Purva Phalguni": "Venus",
            "Uttara Phalguni": "Sun",
            "Hasta": "Moon",
            "Chitra": "Mars",
            "Swati": "Rahu",
            "Vishakha": "Jupiter",
            "Anuradha": "Saturn",
            "Jyeshtha": "Mercury",
            "Mula": "Ketu",
            "Purva Ashadha": "Venus",
            "Uttara Ashadha": "Sun",
            "Shravana": "Moon",
            "Dhanishta": "Mars",
            "Shatabhisha": "Rahu",
            "Purva Bhadrapada": "Jupiter",
            "Uttara Bhadrapada": "Saturn",
            "Revati": "Mercury"
        }

        starting_lord = nakshatra_to_lord.get(nakshatra_name)

        # Find the position in the sequence
        lords_sequence = [
            "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter",
            "Saturn", "Mercury"
        ]
        start_idx = lords_sequence.index(starting_lord)

        # Calculate start date considering dasha balance
        remaining_years = dasha_balance['Years']
        remaining_months = dasha_balance['Months']
        remaining_days = dasha_balance['Days']

        # Calculate first dasha end date
        first_dasha_end = birth_date + relativedelta(years=remaining_years,
                                                     months=remaining_months,
                                                     days=remaining_days)
        first_lord = starting_lord
        first_total_years = dasha_lords[first_lord]

        # Calculate first dasha start date
        first_dasha_start = first_dasha_end - relativedelta(
            years=first_total_years)

        # Add first dasha
        dashas.append({
            'lord':
            first_lord,
            'start_date':
            first_dasha_start.strftime('%Y-%m-%d'),
            'end_date':
            first_dasha_end.strftime('%Y-%m-%d'),
            'duration':
            f"{first_total_years} years",
            'is_current':
            first_dasha_start <= datetime.datetime.now() <= first_dasha_end
        })

        # Calculate subsequent dashas
        current_date = first_dasha_end
        for i in range(1, 9):  # 9 mahadashas total
            lord_idx = (start_idx + i) % 9
            lord = lords_sequence[lord_idx]
            duration_years = dasha_lords[lord]

            dasha_end = current_date + relativedelta(years=duration_years)

            dashas.append({
                'lord':
                lord,
                'start_date':
                current_date.strftime('%Y-%m-%d'),
                'end_date':
                dasha_end.strftime('%Y-%m-%d'),
                'duration':
                f"{duration_years} years",
                'is_current':
                current_date <= datetime.datetime.now() <= dasha_end
            })

            current_date = dasha_end

        # Calculate antardashas (sub-periods) for current mahadasha
        current_lord = current_mahadasha['Mahadasha']['Lord']
        current_start = datetime.datetime.strptime(
            current_mahadasha['Mahadasha']['StartDate'], '%d/%m/%Y')
        current_end = datetime.datetime.strptime(
            current_mahadasha['Mahadasha']['EndDate'], '%d/%m/%Y')
        current_duration_years = dasha_lords[current_lord]

        antardashas = []
        antardasha_start = current_start

        # Cycle through all 9 lords for antardashas
        for i in range(9):
            lord_idx = lords_sequence.index(current_lord)
            antardasha_lord_idx = (lord_idx + i) % 9
            antardasha_lord = lords_sequence[antardasha_lord_idx]

            # Calculate proportion of mahadasha
            antardasha_proportion = dasha_lords[
                antardasha_lord] / 120  # 120 is sum of all dasha years
            antardasha_duration_days = current_duration_years * 365 * antardasha_proportion

            antardasha_end = antardasha_start + datetime.timedelta(
                days=antardasha_duration_days)

            if antardasha_end > current_end:
                antardasha_end = current_end

            antardashas.append({
                'lord':
                antardasha_lord,
                'start_date':
                antardasha_start.strftime('%Y-%m-%d'),
                'end_date':
                antardasha_end.strftime('%Y-%m-%d'),
                'is_current':
                antardasha_start <= datetime.datetime.now() <= antardasha_end
            })

            if antardasha_end >= current_end:
                break

            antardasha_start = antardasha_end

        # Check for pratyantardashas (sub-sub periods) if needed
        current_antardasha = next((a for a in antardashas if a['is_current']),
                                  None)
        pratyantardashas = []

        if current_antardasha:
            antardasha_lord = current_antardasha['lord']
            antardasha_start = datetime.datetime.strptime(
                current_antardasha['start_date'], '%Y-%m-%d')
            antardasha_end = datetime.datetime.strptime(
                current_antardasha['end_date'], '%Y-%m-%d')
            antardasha_duration = (antardasha_end - antardasha_start).days

            pratyantardasha_start = antardasha_start

            for i in range(9):
                lord_idx = lords_sequence.index(antardasha_lord)
                pratyantardasha_lord_idx = (lord_idx + i) % 9
                pratyantardasha_lord = lords_sequence[pratyantardasha_lord_idx]

                pratyantardasha_proportion = dasha_lords[
                    pratyantardasha_lord] / 120
                pratyantardasha_duration = antardasha_duration * pratyantardasha_proportion

                pratyantardasha_end = pratyantardasha_start + datetime.timedelta(
                    days=pratyantardasha_duration)

                if pratyantardasha_end > antardasha_end:
                    pratyantardasha_end = antardasha_end

                pratyantardashas.append({
                    'lord':
                    pratyantardasha_lord,
                    'start_date':
                    pratyantardasha_start.strftime('%Y-%m-%d'),
                    'end_date':
                    pratyantardasha_end.strftime('%Y-%m-%d'),
                    'is_current':
                    pratyantardasha_start <= datetime.datetime.now() <=
                    pratyantardasha_end
                })

                if pratyantardasha_end >= antardasha_end:
                    break

                pratyantardasha_start = pratyantardasha_end

        # Get interpretations for current dasha periods
        interpretations = {
            "Ketu":
            "Spiritual growth, detachment, sudden changes, and unexpected events.",
            "Venus":
            "Relationships, marriage, comforts, luxury, arts, and sensual pleasures.",
            "Sun":
            "Authority, leadership, father figures, career advancement, and recognition.",
            "Moon": "Emotions, mother, nurturing, changes, and the public.",
            "Mars":
            "Energy, courage, conflicts, siblings, technical skills, and property.",
            "Rahu":
            "Ambition, obsession, foreign influence, innovation, and unconventional paths.",
            "Jupiter":
            "Wisdom, education, children, finances, and spiritual growth.",
            "Saturn":
            "Discipline, delays, hard work, longevity, and career challenges.",
            "Mercury": "Communication, intelligence, business, and education."
        }

        # Find the current active periods
        current_mahadasha_info = next((d for d in dashas if d['is_current']),
                                      None)
        current_antardasha_info = next(
            (a for a in antardashas if a['is_current']), None)
        current_pratyantardasha_info = next(
            (p for p in pratyantardashas if p['is_current']), None)

        # Create more detailed interpretation for current periods
        current_interpretation = ""
        if current_mahadasha_info and current_antardasha_info:
            mahadasha_lord = current_mahadasha_info['lord']
            antardasha_lord = current_antardasha_info['lord']

            current_interpretation = f"You are currently in {mahadasha_lord}-{antardasha_lord} period. "
            current_interpretation += f"The main influence ({mahadasha_lord}) brings {interpretations[mahadasha_lord]} "
            current_interpretation += f"While the sub-influence ({antardasha_lord}) adds {interpretations[antardasha_lord]}"

            if current_pratyantardasha_info:
                pratyantardasha_lord = current_pratyantardasha_info['lord']
                current_interpretation += f" With subtle effects of {pratyantardasha_lord}: {interpretations[pratyantardasha_lord]}"

        return render_template(
            'dashas.html',
            birth_details=f"Birth: {birth_time.ToString()}",
            moon_nakshatra=nakshatra_name,
            nakshatra_pada=nakshatra_pada,
            dashas=dashas,
            antardashas=antardashas,
            pratyantardashas=pratyantardashas,
            current_mahadasha=current_mahadasha_info,
            current_antardasha=current_antardasha_info,
            current_pratyantardasha=current_pratyantardasha_info,
            interpretation=current_interpretation,
            planet_interpretations=interpretations)

    except Exception as e:
        return render_template(
            'home.html', error=f"Error calculating dasha periods: {str(e)}")


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
