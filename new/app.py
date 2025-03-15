# # app.py
# from flask import Flask, render_template, request, redirect, url_for, session, flash
# import os
# from datetime import datetime

# app = Flask(__name__)
# app.secret_key = os.urandom(24)

# @app.route('/')
# def index():
#     if 'user_id' in session:
#         return redirect(url_for('dashboard'))
#     return render_template('index.html')

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         email = request.form.get('email')
#         password = request.form.get('password')
#         # Authentication would go here
#         session['user_id'] = email  # Simplified for demo
#         return redirect(url_for('dashboard'))
#     return render_template('login.html')

# @app.route('/signup', methods=['GET', 'POST'])
# def signup():
#     if request.method == 'POST':
#         name = request.form.get('name')
#         email = request.form.get('email')
#         password = request.form.get('password')
#         dob = request.form.get('dob')
#         birth_time = request.form.get('birth_time')
#         birth_place = request.form.get('birth_place')
        
#         # User creation would go here
#         session['user_id'] = email  # Simplified for demo
#         return redirect(url_for('dashboard'))
#     return render_template('signup.html')

# @app.route('/dashboard')
# def dashboard():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
    
#     # Placeholder data - would be calculated from actual birth info
#     user_data = {
#         'moon_sign': 'Taurus',
#         'ascendant': 'Leo',
#         'sun_sign': 'Aries',
#         'dashas': {
#             'current': 'Venus Mahadasha',
#             'remaining': '12 years, 3 months'
#         },
#         'planets': [
#             {'name': 'Sun', 'sign': 'Aries', 'house': 9, 'degrees': 15.23},
#             {'name': 'Moon', 'sign': 'Taurus', 'house': 10, 'degrees': 8.45},
#             {'name': 'Mercury', 'sign': 'Pisces', 'house': 8, 'degrees': 3.12},
#             {'name': 'Venus', 'sign': 'Aquarius', 'house': 7, 'degrees': 27.89},
#             {'name': 'Mars', 'sign': 'Capricorn', 'house': 6, 'degrees': 19.56},
#             {'name': 'Jupiter', 'sign': 'Sagittarius', 'house': 5, 'degrees': 5.67},
#             {'name': 'Saturn', 'sign': 'Scorpio', 'house': 4, 'degrees': 11.34},
#             {'name': 'Rahu', 'sign': 'Libra', 'house': 3, 'degrees': 22.78},
#             {'name': 'Ketu', 'sign': 'Aries', 'house': 9, 'degrees': 22.78}
#         ],
#         'daily_update': {
#             'date': datetime.now().strftime('%B %d, %Y'),
#             'transits': [
#                 'Moon enters Gemini',
#                 'Venus squares Mars',
#                 'Jupiter retrograde in Sagittarius'
#             ],
#             'forecast': 'Today brings intellectual stimulation and curiosity as the Moon transits Gemini. Communication flows easily, but Venus square Mars may create tension in relationships. Focus on balancing action with diplomacy.'
#         }
#     }
    
#     return render_template('dashboard.html', user_data=user_data)

# @app.route('/birth_chart')
# def birth_chart():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
    
#     # Placeholder data
#     chart_data = {
#         'ascendant': 'Leo',
#         'houses': {
#             1: {'sign': 'Leo', 'planets': ['None']},
#             2: {'sign': 'Virgo', 'planets': ['None']},
#             3: {'sign': 'Libra', 'planets': ['Rahu']},
#             4: {'sign': 'Scorpio', 'planets': ['Saturn']},
#             5: {'sign': 'Sagittarius', 'planets': ['Jupiter']},
#             6: {'sign': 'Capricorn', 'planets': ['Mars']},
#             7: {'sign': 'Aquarius', 'planets': ['Venus']},
#             8: {'sign': 'Pisces', 'planets': ['Mercury']},
#             9: {'sign': 'Aries', 'planets': ['Sun', 'Ketu']},
#             10: {'sign': 'Taurus', 'planets': ['Moon']},
#             11: {'sign': 'Gemini', 'planets': ['None']},
#             12: {'sign': 'Cancer', 'planets': ['None']}
#         }
#     }
    
#     return render_template('birth_chart.html', chart_data=chart_data)

# @app.route('/compatibility')
# def compatibility():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#     return render_template('compatibility.html')

# @app.route('/compatibility/result', methods=['POST'])
# def compatibility_result():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
    
#     partner_name = request.form.get('partner_name')
#     partner_dob = request.form.get('partner_dob')
#     partner_time = request.form.get('partner_time')
#     partner_place = request.form.get('partner_place')
    
#     # Placeholder data - would be calculated based on both birth charts
#     compatibility_data = {
#         'overall_score': 28,
#         'max_score': 36,
#         'percentage': 78,
#         'aspects': [
#             {'name': 'Varna (Class)', 'score': 1, 'max': 1, 'description': 'Social compatibility'},
#             {'name': 'Vashya (Dominance)', 'score': 2, 'max': 2, 'description': 'Mutual control and influence'},
#             {'name': 'Tara (Prosperity)', 'score': 3, 'max': 3, 'description': 'Mutual prosperity and well-being'},
#             {'name': 'Yoni (Physical)', 'score': 3, 'max': 4, 'description': 'Sexual compatibility'},
#             {'name': 'Graha Maitri (Planetary)', 'score': 5, 'max': 5, 'description': 'Friendship between lords of moon signs'},
#             {'name': 'Gana (Temperament)', 'score': 4, 'max': 6, 'description': 'Psychological compatibility'},
#             {'name': 'Bhakut (Social Harmony)', 'score': 6, 'max': 7, 'description': 'Long-term relationship harmony'},
#             {'name': 'Nadi (Health)', 'score': 4, 'max': 8, 'description': 'Health and genetic compatibility'}
#         ],
#         'recommendation': 'This match scores well in most categories, particularly in planetary friendship and social harmony. The lower score in health compatibility (Nadi) suggests potential challenges related to health or genetic factors. Overall, this is considered a favorable match in Vedic astrology with a good foundation for long-term harmony.',
#         'elements': {
#             'you': {'fire': 35, 'earth': 25, 'air': 15, 'water': 25},
#             'partner': {'fire': 20, 'earth': 30, 'air': 30, 'water': 20}
#         }
#     }
    
#     return render_template('compatibility_result.html', partner_name=partner_name, compatibility_data=compatibility_data)

# @app.route('/dashas')
# def dashas():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
    
#     # Placeholder dasha data
#     dasha_data = {
#         'current_mahadasha': {
#             'planet': 'Venus',
#             'start_date': 'May 12, 2018',
#             'end_date': 'May 12, 2038',
#             'description': 'Venus Mahadasha often brings harmony, creativity, and material comforts. This is generally a period of pleasure, relationships, and artistic expression. Financial gains and satisfying partnerships are likely during this 20-year cycle.'
#         },
#         'current_antardasha': {
#             'planet': 'Saturn',
#             'start_date': 'September 12, 2023',
#             'end_date': 'November 12, 2026',
#             'description': 'Venus-Saturn period combines pleasure with discipline. You may experience delayed but solid rewards, especially in career and finances. Relationships may face tests but can become stronger. Focus on patience and structured approach to creativity.'
#         },
#         'upcoming_antardashas': [
#             {
#                 'planet': 'Mercury',
#                 'start_date': 'November 12, 2026',
#                 'end_date': 'September 12, 2029',
#                 'duration': '2 years, 10 months'
#             },
#             {
#                 'planet': 'Ketu',
#                 'start_date': 'September 12, 2029',
#                 'end_date': 'November 12, 2030',
#                 'duration': '1 year, 2 months'
#             },
#             {
#                 'planet': 'Venus',
#                 'start_date': 'November 12, 2030',
#                 'end_date': 'January 12, 2034',
#                 'duration': '3 years, 2 months'
#             }
#         ],
#         'past_maharashas': [
#             {
#                 'planet': 'Moon',
#                 'start_date': 'May 12, 2008',
#                 'end_date': 'May 12, 2018',
#                 'duration': '10 years'
#             },
#             {
#                 'planet': 'Mars',
#                 'start_date': 'May 12, 2001',
#                 'end_date': 'May 12, 2008',
#                 'duration': '7 years'
#             }
#         ]
#     }
    
#     return render_template('dashas.html', dasha_data=dasha_data)

# @app.route('/transits')
# def transits():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
    
#     # Placeholder transit data
#     transit_data = {
#         'date': datetime.now().strftime('%B %d, %Y'),
#         'current_transits': [
#             {
#                 'planet': 'Sun',
#                 'sign': 'Pisces',
#                 'degrees': '15°23\'',
#                 'house': 8,
#                 'aspect': 'Conjunct natal Mercury'
#             },
#             {
#                 'planet': 'Moon',
#                 'sign': 'Gemini',
#                 'degrees': '8°45\'',
#                 'house': 11,
#                 'aspect': 'Trine natal Venus'
#             },
#             {
#                 'planet': 'Mercury',
#                 'sign': 'Pisces',
#                 'degrees': '3°12\'',
#                 'house': 8,
#                 'aspect': 'Conjunct natal Mercury'
#             },
#             {
#                 'planet': 'Venus',
#                 'sign': 'Aries',
#                 'degrees': '27°89\'',
#                 'house': 9,
#                 'aspect': 'Square natal Mars'
#             },
#             {
#                 'planet': 'Mars',
#                 'sign': 'Taurus',
#                 'degrees': '19°56\'',
#                 'house': 10,
#                 'aspect': 'Trine natal Saturn'
#             },
#             {
#                 'planet': 'Jupiter',
#                 'sign': 'Capricorn',
#                 'degrees': '5°67\'',
#                 'house': 6,
#                 'aspect': 'Sextile natal Jupiter'
#             },
#             {
#                 'planet': 'Saturn',
#                 'sign': 'Aquarius',
#                 'degrees': '11°34\'',
#                 'house': 7,
#                 'aspect': 'Square natal Moon'
#             },
#             {
#                 'planet': 'Rahu',
#                 'sign': 'Taurus',
#                 'degrees': '22°78\'',
#                 'house': 10,
#                 'aspect': 'Opposite natal Ketu'
#             },
#             {
#                 'planet': 'Ketu',
#                 'sign': 'Scorpio',
#                 'degrees': '22°78\'',
#                 'house': 4,
#                 'aspect': 'Opposite natal Rahu'
#             }
#         ],
#         'interpretation': 'With the Sun and Mercury in your 8th house of transformation, this is a time of deep introspection and potential revelations. The Moon in Gemini in your 11th house encourages social connections that may bring unexpected insights. Saturn\'s square to your natal Moon suggests emotional challenges that require patience and discipline. Jupiter\'s favorable aspect to its natal position offers growth opportunities in health and daily routines.'
#     }
    
#     upcoming_transits = [
#         {
#             'date': 'March 15, 2025',
#             'event': 'Mercury enters Aries',
#             'effect': 'Communication becomes more direct and assertive. Good time for initiating new intellectual projects.'
#         },
#         {
#             'date': 'March 20, 2025',
#             'event': 'Sun enters Aries (Equinox)',
#             'effect': 'Solar energy shifts to your 9th house, highlighting higher education, travel, and philosophical pursuits.'
#         },
#         {
#             'date': 'March 27, 2025',
#             'event': 'Venus enters Taurus',
#             'effect': 'Relationships stabilize and financial matters improve. Excellent period for investments and sensual pleasures.'
#         },
#         {
#             'date': 'April 2, 2025',
#             'event': 'Mars enters Gemini',
#             'effect': 'Energy becomes more scattered but versatile. Multiple projects may demand your attention simultaneously.'
#         }
#     ]
    
#     return render_template('transits.html', transit_data=transit_data, upcoming_transits=upcoming_transits)

# @app.route('/remedies')
# def remedies():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
    
#     # Placeholder remedies data
#     remedies_data = {
#         'challenging_planets': [
#             {
#                 'planet': 'Saturn',
#                 'position': 'Afflicting Moon in 4th house',
#                 'issues': 'Emotional insecurity, domestic challenges, property-related issues',
#                 'remedies': [
#                     'Recite Hanuman Chalisa on Saturdays',
#                     'Donate black sesame seeds to the needy',
#                     'Wear a Blue Sapphire (Neelam) after proper consultation',
#                     'Serve the elderly and practice meditation'
#                 ]
#             },
#             {
#                 'planet': 'Rahu',
#                 'position': '3rd house, aspecting 9th house',
#                 'issues': 'Obsessive thinking, communication problems, challenges with father or mentor',
#                 'remedies': [
#                     'Feed crows on Wednesdays',
#                     'Recite Durga Chalisa',
#                     'Wear a Hessonite (Gomed) gemstone',
#                     'Practice mindfulness meditation'
#                 ]
#             }
#         ],
#         'beneficial_planets': [
#             {
#                 'planet': 'Jupiter',
#                 'position': '5th house in own sign',
#                 'benefits': 'Wisdom, fortune, spiritual growth, success in education',
#                 'enhancement': [
#                     'Recite Vishnu Sahasranama on Thursdays',
#                     'Donate yellow items or sweets',
#                     'Wear a Yellow Sapphire (Pukhraj) gemstone',
#                     'Practice yoga and spiritual studies'
#                 ]
#             },
#             {
#                 'planet': 'Venus',
#                 'position': '7th house, well-placed',
#                 'benefits': 'Harmonious relationships, aesthetic sense, diplomatic skills',
#                 'enhancement': [
#                     'Recite Venus mantras on Fridays',
#                     'Donate white flowers or rice',
#                     'Wear a Diamond or White Sapphire',
#                     'Practice artistic activities and balanced lifestyle'
#                 ]
#             }
#         ],
#         'general_remedies': [
#             'Regular meditation to balance planetary energies',
#             'Yogic breathing exercises (Pranayama)',
#             'Maintain a clean and harmonious living environment',
#             'Practice gratitude and compassion daily'
#         ]
#     }
    
#     return render_template('remedies.html', remedies_data=remedies_data)

# @app.route('/settings')
# def settings():
#     if 'user_id' not in session:
#         return redirect(url_for('login'))
#     return render_template('settings.html')

# @app.route('/logout')
# def logout():
#     session.pop('user_id', None)
#     return redirect(url_for('index'))

# if __name__ == '__main__':
#     app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for, session, flash
from vedastro import GeoLocation, Time, Calculate, PlanetName, HouseName, ZodiacName
import psycopg2
from psycopg2.extras import RealDictCursor
import os
from urllib.parse import quote
from dotenv import load_dotenv
from timezonefinder import TimezoneFinder
import pytz
from datetime import datetime
from huggingface_hub import InferenceClient
import requests

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'default_secret_key')

# Supabase Database Connection
def get_db_connection():
    conn = psycopg2.connect(os.environ.get('SUPABASE_DB_URL'), cursor_factory=RealDictCursor)
    return conn

# Hugging Face API setup
HF_API_TOKEN = os.environ.get('HF_API_TOKEN')
client = InferenceClient(provider="together", api_key=HF_API_TOKEN)

# Vedastro API key
VED_API_KEY = os.environ.get('VED_API_KEY')
Calculate.SetAPIKey(VED_API_KEY)

# Zodiac signs for reference
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

# Planet display names and symbols
PLANET_DISPLAY_NAMES = {
    PlanetName.Sun: "Sun", PlanetName.Moon: "Moon", PlanetName.Mars: "Mars",
    PlanetName.Mercury: "Mercury", PlanetName.Jupiter: "Jupiter", PlanetName.Venus: "Venus",
    PlanetName.Saturn: "Saturn", PlanetName.Rahu: "Rahu", PlanetName.Ketu: "Ketu"
}

PLANET_SYMBOLS = {
    "Sun": "☉", "Moon": "☽", "Mars": "♂", "Mercury": "☿", "Jupiter": "♃",
    "Venus": "♀", "Saturn": "♄", "Rahu": "☊", "Ketu": "☋"
}

# Helper functions
def geocode_location(location):
    try:
        encoded_location = quote(location)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_location}&format=json&limit=1"
        headers = {'User-Agent': 'VedicAstroApp/1.0'}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            if data:
                return data[0]['display_name'], float(data[0]['lat']), float(data[0]['lon'])
        return None, None, None
    except Exception as e:
        print(f"Geocoding error: {e}")
        return None, None, None

def get_timezone(latitude, longitude):
    tf = TimezoneFinder()
    timezone_name = tf.timezone_at(lat=latitude, lng=longitude)
    if timezone_name:
        tz = pytz.timezone(timezone_name)
        offset = tz.utcoffset(datetime.utcnow()).total_seconds()
        hours = int(offset // 3600)
        minutes = int((abs(offset) % 3600) // 60)
        sign = "+" if hours >= 0 else "-"
        return f"{sign}{abs(hours):02}:{minutes:02}"
    return "+00:00"

def calculate_birth_chart(date_str, time_str, location):
    place_name, lat, lon = geocode_location(location)
    if not place_name:
        raise ValueError("Invalid location")
    
    day, month, year = date_str.split('-')[::-1]
    formatted_date = f"{day}/{month}/{year}"
    timezone = get_timezone(lat, lon)
    geo_location = GeoLocation(place_name, lon, lat)
    birth_time = Time(f"{time_str} {formatted_date} {timezone}", geo_location)

    house_data = Calculate.AllHouseData(HouseName.House1, birth_time)
    asc_sign = house_data['HouseRasiSign']['Name']

    planets = []
    planet_list = [PlanetName.Sun, PlanetName.Moon, PlanetName.Mars, PlanetName.Mercury,
                   PlanetName.Jupiter, PlanetName.Venus, PlanetName.Saturn, PlanetName.Rahu,
                   PlanetName.Ketu]
    asc_sign_num = SIGNS.index(asc_sign) + 1
    for planet in planet_list:
        planet_data = Calculate.AllPlanetData(planet, birth_time)
        sign = planet_data['PlanetRasiD1Sign']['Name']
        degree = float(planet_data['PlanetRasiD1Sign']['DegreesIn']['TotalDegrees'])
        sign_num = SIGNS.index(sign) + 1
        house = ((sign_num - asc_sign_num) % 12) + 1
        planets.append({
            'name': PLANET_DISPLAY_NAMES[planet],
            'sign': sign,
            'house': house,
            'degrees': degree
        })

    moon_sign = next(p for p in planets if p['name'] == 'Moon')['sign']
    sun_sign = next(p for p in planets if p['name'] == 'Sun')['sign']

    user_data = {
        'moon_sign': moon_sign,
        'ascendant': asc_sign,
        'sun_sign': sun_sign,
        'dashas': {'current': 'Venus Mahadasha', 'remaining': '12 years, 3 months'},
        'planets': planets,
        'daily_update': {
            'date': datetime.now().strftime('%B %d, %Y'),
            'transits': ['Moon enters Gemini', 'Venus squares Mars'],
            'forecast': 'Today brings intellectual stimulation...'
        }
    }
    return user_data, birth_time

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')  # In reality, Supabase Auth handles this
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT id, email FROM public.users WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        conn.close()
        if user:  # Simplified check; integrate Supabase Auth for real password validation
            session['user_id'] = str(user['id'])
            return redirect(url_for('dashboard'))
        flash('Invalid credentials')
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')  # Supabase Auth would handle this
        dob = request.form.get('dob')
        birth_time = request.form.get('birth_time')
        birth_place = request.form.get('birth_place')
        
        conn = get_db_connection()
        cur = conn.cursor()
        # Check if email already exists
        cur.execute("SELECT id FROM public.users WHERE email = %s", (email,))
        if cur.fetchone():
            flash('Email already exists')
        else:
            # Insert into public.users (id will come from auth.users via trigger)
            # For simplicity, manually inserting here; ideally use Supabase Auth signup
            cur.execute(
                "INSERT INTO public.users (email, name, birth_date, birth_time, birth_place) VALUES (%s, %s, %s, %s, %s) RETURNING id",
                (email, name, dob, birth_time, birth_place)
            )
            user_id = cur.fetchone()['id']
            conn.commit()
            session['user_id'] = str(user_id)
            return redirect(url_for('dashboard'))
        cur.close()
        conn.close()
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM public.users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    conn.close()
    try:
        user_data, birth_time = calculate_birth_chart(user['birth_date'], user['birth_time'], user['birth_place'])
        session['birth_time'] = str(birth_time)
        return render_template('dashboard.html', user_data=user_data)
    except Exception as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for('settings'))

@app.route('/birth_chart')
def birth_chart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM public.users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    conn.close()
    try:
        user_data, _ = calculate_birth_chart(user['birth_date'], user['birth_time'], user['birth_place'])
        asc_sign = user_data['ascendant']
        planets = user_data['planets']
        houses = {}
        for i in range(1, 13):
            house_sign_index = (SIGNS.index(asc_sign) + i - 1) % 12
            house_sign = SIGNS[house_sign_index]
            planets_in_house = [p['name'] for p in planets if p['house'] == i]
            houses[i] = {'sign': house_sign, 'planets': planets_in_house or ['None']}
        chart_data = {'ascendant': asc_sign, 'houses': houses}
        return render_template('birth_chart.html', chart_data=chart_data)
    except Exception as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for('dashboard'))

@app.route('/compatibility', methods=['GET', 'POST'])
def compatibility():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        partner_name = request.form.get('partner_name')
        date2_str = request.form.get('partner_dob')
        time2_str = request.form.get('partner_time')
        location2 = request.form.get('partner_place')
        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT * FROM public.users WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        cur.close()
        conn.close()
        
        place1_name, lat1, lon1 = geocode_location(user['birth_place'])
        day1, month1, year1 = user['birth_date'].split('-')[::-1]
        formatted_date1 = f"{day1}/{month1}/{year1}"
        timezone1 = get_timezone(lat1, lon1)
        geo_location1 = GeoLocation(place1_name, lon1, lat1)
        birth_time1 = Time(f"{user['birth_time']} {formatted_date1} {timezone1}", geo_location1)

        place2_name, lat2, lon2 = geocode_location(location2)
        day2, month2, year2 = date2_str.split('-')[::-1]
        formatted_date2 = f"{day2}/{month2}/{year2}"
        timezone2 = get_timezone(lat2, lon2)
        geo_location2 = GeoLocation(place2_name, lon2, lat2)
        birth_time2 = Time(f"{time2_str} {formatted_date2} {timezone2}", geo_location2)

        match_report = Calculate.MatchReport(birth_time1, birth_time2)
        compatibility_data = {
            'overall_score': match_report['TotalPoints'],
            'max_score': 36,
            'percentage': (match_report['TotalPoints'] / 36) * 100,
            'aspects': [
                {'name': 'Varna', 'score': match_report['VarnaPoints'], 'max': 1, 'description': 'Social compatibility'},
                {'name': 'Vashya', 'score': match_report['VashyaPoints'], 'max': 2, 'description': 'Mutual control'},
                {'name': 'Tara', 'score': match_report['TaraPoints'], 'max': 3, 'description': 'Prosperity'},
                {'name': 'Yoni', 'score': match_report['YoniPoints'], 'max': 4, 'description': 'Physical compatibility'},
                {'name': 'Graha Maitri', 'score': match_report['GrahaMaitriPoints'], 'max': 5, 'description': 'Planetary friendship'},
                {'name': 'Gana', 'score': match_report['GanaPoints'], 'max': 6, 'description': 'Temperament'},
                {'name': 'Bhakut', 'score': match_report['BhakootPoints'], 'max': 7, 'description': 'Social harmony'},
                {'name': 'Nadi', 'score': match_report['NadiPoints'], 'max': 8, 'description': 'Health compatibility'}
            ],
            'recommendation': 'A score above 18 is generally considered favorable in Vedic astrology.',
            'elements': {'you': {'fire': 35, 'earth': 25, 'air': 15, 'water': 25}, 'partner': {'fire': 20, 'earth': 30, 'air': 30, 'water': 20}}
        }
        return render_template('compatibility_result.html', partner_name=partner_name, compatibility_data=compatibility_data)
    return render_template('compatibility.html')

@app.route('/dashas')
def dashas():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM public.users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    conn.close()
    try:
        place_name, lat, lon = geocode_location(user['birth_place'])
        day, month, year = user['birth_date'].split('-')[::-1]
        formatted_date = f"{day}/{month}/{year}"
        timezone = get_timezone(lat, lon)
        geo_location = GeoLocation(place_name, lon, lat)
        birth_time = Time(f"{user['birth_time']} {formatted_date} {timezone}", geo_location)
        
        current_time = Time.Now()
        current_mahadasha = Calculate.VimshottariDashaCurrent(birth_time, current_time)
        dasha_data = {
            'current_mahadasha': {
                'planet': current_mahadasha['Mahadasha']['Lord'],
                'start_date': current_mahadasha['Mahadasha']['StartDate'],
                'end_date': current_mahadasha['Mahadasha']['EndDate'],
                'description': 'A period influenced by ' + current_mahadasha['Mahadasha']['Lord']
            },
            'current_antardasha': {
                'planet': current_mahadasha['Antardasha']['Lord'],
                'start_date': current_mahadasha['Antardasha']['StartDate'],
                'end_date': current_mahadasha['Antardasha']['EndDate'],
                'description': 'Sub-period under ' + current_mahadasha['Antardasha']['Lord']
            },
            'upcoming_antardashas': [],
            'past_mahadashas': []
        }
        return render_template('dashas.html', dasha_data=dasha_data)
    except Exception as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for('dashboard'))

@app.route('/transits')
def transits():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM public.users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    conn.close()
    try:
        place_name, lat, lon = geocode_location(user['birth_place'])
        day, month, year = user['birth_date'].split('-')[::-1]
        formatted_date = f"{day}/{month}/{year}"
        timezone = get_timezone(lat, lon)
        geo_location = GeoLocation(place_name, lon, lat)
        birth_time = Time(f"{user['birth_time']} {formatted_date} {timezone}", geo_location)
        current_time = Time.Now()

        transit_planets = []
        for planet in [PlanetName.Sun, PlanetName.Moon, PlanetName.Mars, PlanetName.Mercury,
                       PlanetName.Jupiter, PlanetName.Venus, PlanetName.Saturn, PlanetName.Rahu,
                       PlanetName.Ketu]:
            transit_data = Calculate.AllPlanetData(planet, current_time)
            sign = transit_data['PlanetRasiD1Sign']['Name']
            degree = float(transit_data['PlanetRasiD1Sign']['DegreesIn']['TotalDegrees'])
            natal_data = Calculate.AllPlanetData(planet, birth_time)
            natal_sign = natal_data['PlanetRasiD1Sign']['Name']
            transit_planets.append({
                'planet': PLANET_DISPLAY_NAMES[planet],
                'sign': sign,
                'degrees': f"{degree:.2f}°",
                'house': (SIGNS.index(sign) - SIGNS.index(natal_sign) % 12) + 1,
                'aspect': f"Transit in {sign}"
            })

        transit_data = {
            'date': datetime.now().strftime('%B %d, %Y'),
            'current_transits': transit_planets,
            'interpretation': 'Current planetary transits influence your natal chart.'
        }
        return render_template('transits.html', transit_data=transit_data, PLANET_SYMBOLS=PLANET_SYMBOLS)
    except Exception as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for('dashboard'))

@app.route('/remedies')
def remedies():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM public.users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    cur.close()
    conn.close()
    try:
        user_data, _ = calculate_birth_chart(user['birth_date'], user['birth_time'], user['birth_place'])
        moon_sign = user_data['moon_sign']
        remedies = {
            'Aries': ['Wear red coral', 'Recite Hanuman Chalisa'],
            'Taurus': ['Wear diamond', 'Worship Lakshmi'],
            'Gemini': ['Wear emerald', 'Recite Vishnu mantras'],
            # Add other signs as needed
        }
        remedies_data = {
            'challenging_planets': [
                {
                    'planet': 'Saturn',
                    'position': 'Afflicting Moon',
                    'issues': 'Emotional challenges',
                    'remedies': remedies.get(moon_sign, ['General meditation'])
                }
            ],
            'beneficial_planets': [
                {
                    'planet': 'Jupiter',
                    'position': 'Well-placed',
                    'benefits': 'Wisdom and growth',
                    'enhancement': ['Wear yellow sapphire', 'Recite Guru mantra']
                }
            ],
            'general_remedies': ['Meditation', 'Yoga']
        }
        return render_template('remedies.html', remedies_data=remedies_data)
    except Exception as e:
        flash(f"Error: {str(e)}")
        return redirect(url_for('dashboard'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM public.users WHERE id = %s", (session['user_id'],))
    user = cur.fetchone()
    if request.method == 'POST':
        name = request.form.get('name')
        dob = request.form.get('dob')
        birth_time = request.form.get('birth_time')
        birth_place = request.form.get('birth_place')
        cur.execute(
            "UPDATE public.users SET name = %s, birth_date = %s, birth_time = %s, birth_place = %s WHERE id = %s",
            (name, dob, birth_time, birth_place, session['user_id'])
        )
        conn.commit()
        flash('Settings updated')
    cur.close()
    conn.close()
    return render_template('settings.html', user=user)

if __name__ == '__main__':
    app.run(debug=True)