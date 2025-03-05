from flask import Flask, render_template, request, jsonify
from vedastro import GeoLocation, Time, Calculate, PlanetName, HouseName, ZodiacName
import requests
import json
import os
from urllib.parse import quote
from dotenv import load_dotenv
import re
# from transformers import pipeline

load_dotenv()

app = Flask(__name__)

# Hugging Face API setup (replace with your token)
HF_API_TOKEN = os.environ['HF_API_TOKEN']
VED_API_KEY = os.environ['VED_API_KEY']
KARAN_API_KEY = os.environ['KARAN_API_KEY']
API_URL = "https://router.huggingface.co/together/v1/chat/completions"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}
Calculate.SetAPIKey("0aRn6PrZof")

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
        api_url = API_URL  # "https://router.huggingface.co/together/v1/chat/completions"
        payload = {
            "model": "deepseek-ai/DeepSeek-R1",
            "messages": [{
                "role": "user",
                "content": prompt
            }],  # prompt as a string
            "max_tokens": 1200,
            "stream": False  # Use boolean, not string 'false'
        }
        print(
            f"Sending request to {api_url} with payload: {json.dumps(payload, indent=2)}"
        )

        response = requests.post(
            api_url,
            headers={"Authorization": f"Bearer {HF_API_TOKEN}"},
            json=payload)
        response.raise_for_status()

        response_json = response.json()
        response_json = response_json['choices'][0]['message']['content']
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


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
