from email import message
from flask import Flask, render_template, request, jsonify, session, redirect, url_for, flash
from vedastro import GeoLocation, Time, Calculate, PlanetName, HouseName, ZodiacName
import requests
import json
import os
import re
from urllib.parse import quote
from timezonefinder import TimezoneFinder
from datetime import datetime, timedelta
import pytz
from huggingface_hub import InferenceClient
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from dotenv import load_dotenv
import uuid
from hugchat import hugchat
from hugchat.login import Login
# markdown
import markdown
from markdown.extensions.fenced_code import FencedCodeExtension
from skyfield.api import load, Topos
from skyfield import almanac
import math 
import voc



# Load environment variables
load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', os.urandom(24).hex())
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'sqlite:///vedic_astro.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

EMAIL = os.environ.get('emailHF')
PASSWD = os.environ.get('pswHF')

cookie_path_dir = f"./cookies/" # NOTE: trailing slash (/) is required to avoid errors
sign = Login(EMAIL, PASSWD)
cookies = sign.login(cookie_dir_path=cookie_path_dir, save_cookies=True)

chatbot = hugchat.ChatBot(cookies=cookies.get_dict()) 

chatbot.switch_llm(1)

# Setup API keys
HF_API_TOKEN = os.environ.get('HF_API_TOKEN')
VED_API_KEY = os.environ.get('VED_API_KEY', '0aRn6PrZof')  # Default key from old code

Calculate.SetAPIKey(VED_API_KEY)

# Setup Hugging Face client for AI responses
client = InferenceClient(
    provider="together",
    api_key=HF_API_TOKEN,
)

# Constants
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio",
    "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

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

SIGN_SYMBOLS = {
    "Aries": "♈",
    "Taurus": "♉",
    "Gemini": "♊",
    "Cancer": "♋",
    "Leo": "♌",
    "Virgo": "♍",
    "Libra": "♎",
    "Scorpio": "♏",
    "Sagittarius": "♐",
    "Capricorn": "♑",
    "Aquarius": "♒",
    "Pisces": "♓"
}

ELEMENT_MAP = {
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

MODALITY_MAP = {
    "Aries": "cardinal",
    "Cancer": "cardinal",
    "Libra": "cardinal",
    "Capricorn": "cardinal",
    "Taurus": "fixed",
    "Leo": "fixed",
    "Scorpio": "fixed",
    "Aquarius": "fixed",
    "Gemini": "mutable",
    "Virgo": "mutable",
    "Sagittarius": "mutable",
    "Pisces": "mutable"
}

PLANET_COLORS = {
    "Sun": "#FDB813",     # Golden yellow
    "Moon": "#F2F2F2",    # Silver white
    "Mars": "#CE2029",    # Red
    "Mercury": "#9DD9D2", # Light blue
    "Jupiter": "#4B0082", # Purple
    "Venus": "#FFBAD2",   # Pink
    "Saturn": "#2F4F4F",  # Dark grey
    "Rahu": "#696969",    # Grey
    "Ketu": "#A9A9A9"     # Light grey
}

PLANET_QUALITIES = {
    "Sun": ["vitality", "ego", "self", "father", "authority", "leadership"],
    "Moon": ["emotions", "mother", "home", "intuition", "nurturing", "subconscious"],
    "Mars": ["action", "desire", "energy", "brothers", "courage", "conflict"],
    "Mercury": ["communication", "intelligence", "siblings", "analysis", "learning", "speech"],
    "Jupiter": ["expansion", "wisdom", "growth", "fortune", "spirituality", "optimism"],
    "Venus": ["relationship", "beauty", "luxury", "art", "pleasure", "harmony"],
    "Saturn": ["discipline", "restriction", "responsibility", "delays", "maturity", "structure"],
    "Rahu": ["desire", "ambition", "obsession", "illusion", "innovation", "foreigner"],
    "Ketu": ["liberation", "spirituality", "detachment", "isolation", "psychic", "past lives"]
}

HOUSE_MEANINGS = {
    1: "Self, appearance, personality, approach to life",
    2: "Values, possessions, money, speech, family",
    3: "Communication, siblings, neighbors, short journeys",
    4: "Home, mother, emotions, real estate, inner security",
    5: "Creativity, children, romance, pleasure, entertainment",
    6: "Health, service, daily routine, debts, enemies",
    7: "Partnerships, marriage, contracts, business partners",
    8: "Transformation, sexuality, joint resources, occult",
    9: "Higher learning, philosophy, travel, beliefs, teaching",
    10: "Career, public image, authority, father, government",
    11: "Friends, hopes, wishes, social groups, gains",
    12: "Spirituality, isolation, hidden things, self-undoing"
}

# Database Models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    birth_time = db.Column(db.String(100))
    birth_chart = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    friends = db.relationship('Friend', backref='user', lazy=True)

class Friend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    friend_name = db.Column(db.String(100), nullable=False)
    compatibility_score = db.Column(db.Integer)
    birth_time = db.Column(db.String(100))
    birth_chart = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class JournalEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    entry_date = db.Column(db.DateTime, default=datetime.utcnow)
    moon_sign = db.Column(db.String(20))
    content = db.Column(db.Text)
    mood = db.Column(db.String(20))

class Transit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    transit_date = db.Column(db.DateTime, default=datetime.utcnow)
    transit_data = db.Column(db.Text)

class dasha(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    dasha_date = db.Column(db.DateTime, default=datetime.utcnow)
    dasha_data = db.Column(db.Text)

    
# Helper Functions
def geocode_location(location):
    try:
        encoded_location = quote(location)
        url = f"https://nominatim.openstreetmap.org/search?q={encoded_location}&format=json&limit=1"
        headers = {'User-Agent': 'VedicAstroAI/2.0'}
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
    try:
        obj = TimezoneFinder()
        timezone_name = obj.timezone_at(lng=longitude, lat=latitude)
        
        if timezone_name:
            tz = pytz.timezone(timezone_name)
            now = datetime.utcnow()
            offset_seconds = tz.utcoffset(now).total_seconds()
            offset_hours = int(offset_seconds // 3600)
            offset_minutes = int(abs(offset_seconds) % 3600) // 60
            
            sign = "+" if offset_hours >= 0 else "-"
            return f"{sign}{abs(offset_hours):02}:{offset_minutes:02}"
        
        return "+00:00"  # Default to UTC
    except Exception as e:
        print(f"Timezone error: {e}")
        return "+00:00"

def calculate_birth_chart(date_str, time_str, location, name="", gender=""):
    # Get latitude and longitude
    place_name, lat, lon = geocode_location(location)
    
    if lat is None or lon is None:
        return None, "Invalid location. Please enter a valid location."
    
    # Format date and time for vedastro
    year, month, day = date_str.split('-')
    formatted_date = f"{day}/{month}/{year}"
    
    # Get timezone based on location
    timezone = get_timezone(lat, lon)
    
    # Create Time and GeoLocation objects
    geo_location = GeoLocation(place_name, lon, lat)
    birth_time = Time(f"{time_str} {formatted_date} {timezone}", geo_location)
    
    
    # Get ascendant (House 1)
    house_data = Calculate.AllHouseData(HouseName.House1, birth_time)
    # print(house_data)
    # Get horoscope predictions
    horoscope_predictions = Calculate.HoroscopePredictions(birth_time, "Empty")
    
    # Get ascendant sign and degree
    asc_sign = house_data['HouseRasiSign']['Name']
    asc_degree = float(house_data['HouseRasiSign']['DegreesIn']['TotalDegrees'])
    
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
    all_planet_data = Calculate.AllPlanetData(PlanetName.All,birth_time)
    all_planet_data = {list(d.keys())[0]: list(d.values())[0] for d in all_planet_data}
    # convert all planet data to dict
    panchanga_table = Calculate.PanchangaTable(birth_time)
    nakshatra = panchanga_table
    for planet in planet_list:
        planet_data = all_planet_data[planet.value]
        planet_name = PLANET_DISPLAY_NAMES[planet]
        
        if 'PlanetRasiD1Sign' in planet_data and isinstance(planet_data['PlanetRasiD1Sign'], dict) and 'Name' in planet_data['PlanetRasiD1Sign']:
            sign = planet_data['PlanetRasiD1Sign']['Name']
        else:
            print(f"Could not find sign name for {planet_name}")
            sign = "Unknown"
        
        sign_num = SIGNS.index(sign) + 1
        degree = float(planet_data['PlanetRasiD1Sign']['DegreesIn']['TotalDegrees'])
        
        # Calculate house (based on whole sign system)
        house = ((sign_num - SIGNS.index(asc_sign) - 1) % 12) + 1
        
        # Get interpretation
        interpretation_key = f"{planet_name}In{sign}"
        interp = next((yoga["Description"] for yoga in horoscope_predictions if yoga["Name"] == interpretation_key), "")
        
        # If no specific planet-in-sign interpretation found, check for planet-in-house
        if not interp:
            house_key = f"{planet_name}InHouse{house}"
            interp = next((yoga["Description"] for yoga in horoscope_predictions if yoga["Name"] == house_key), "No specific interpretation available.")
        
        # Get nakshatra info
        
        # get nakshatra name
        


        # Determine if retrograde
        motion = planet_data.get('Motion', 'Direct')
        is_retrograde = motion == 'Retrograde'
        
        # Get dignity
        dignity = planet_data.get('Dignity', 'Neutral')
        
        # Calculate aspects to other planets
        aspects = []
        for other_planet in planet_list:
            if other_planet != planet:
                other_planet_data = all_planet_data[other_planet]
                other_sign = other_planet_data['PlanetRasiD1Sign']['Name']
                other_degree = float(other_planet_data['PlanetRasiD1Sign']['DegreesIn']['TotalDegrees'])
                
                # Calculate the angular difference
                total_deg = (SIGNS.index(sign) * 30) + degree
                other_total_deg = (SIGNS.index(other_sign) * 30) + other_degree
                
                angle_diff = (total_deg - other_total_deg) % 360
                
                # Check for major aspects
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
                        "planet": PLANET_DISPLAY_NAMES[other_planet],
                        "aspect_type": aspect_type,
                        "angle": round(angle_diff, 2)
                    })
        
        planets.append({
            'name': planet_name,
            'sign': sign,
            'degree': degree,
            'house': house,
            'interpretation': interp,
            'reasoning': (f"{planet_name} is at {degree:.2f}° in {sign}. In the whole sign house system, "
                         f"since the Ascendant is {asc_sign}, {sign} becomes the {house}th house."),
            'nakshatra': nakshatra["Nakshatra"],
            'nakshatra_lord': nakshatra["HoraLord"],
            'nakshatra_degree': nakshatra["IshtaKaala"]['DegreeMinuteSecond'],
            'is_retrograde': is_retrograde,
            'dignity': dignity,
            'aspects': aspects,
            'element': ELEMENT_MAP.get(sign, "unknown"),
            'modality': MODALITY_MAP.get(sign, "unknown"),
            'color': PLANET_COLORS.get(planet_name, "#000000"),
            'qualities': PLANET_QUALITIES.get(planet_name, [])
        })
    
    # Calculate Moon lunar day (tithi)
    try:
        lunar_day = panchanga_table['Tithi']['Name']
        lunar_day_num = panchanga_table['Tithi']['Day']
        lunar_month = panchanga_table['LunarMonth']
        lunar_year = datetime.now().year
    except Exception as e:
        print(f"Error calculating panchanga: {e}")
        lunar_day = "Unknown"
        lunar_day_num = 0
        lunar_month = "Unknown"
        lunar_year = "Unknown"
    
    # Check for Moon void of course (simplified)
    # A more accurate calculation would consider aspects to all planets
    moon_planet = next((p for p in planets if p['name'] == 'Moon'), None)
    if moon_planet:
        moon_sign = moon_planet['sign']
        moon_degree = moon_planet['degree']
        
        # Check if Moon is in last 5 degrees of sign (simplified void check)

        # Get Moon's current position
        is_void, current_sign, reasoning = voc.main()

        void_time_remaining = (30 - moon_degree) * 2  # Rough estimate: 2 hours per degree
        
        moon_void = {
            'is_void': is_void,
            'hours_remaining': void_time_remaining if is_void else 0,
            'description': "The Moon is void-of-course when it makes no more major aspects in its current sign. This period is best for reflection rather than initiation."
        }
    else:
        moon_void = {
            'is_void': False,
            'hours_remaining': 0,
            'description': "Could not calculate Moon void of course period."
        }
    
    # Calculate Dasha periods
    # try:
    if 1==1:
        # Get current Vimshottari dasha
        # datetime now
        current_date = datetime.now()
        levels = 1
        # Assuming current_mahadasha is the result of Calculate.DasaForNow(birth_time, 3)
        all_dasha = Calculate.DasaForLife(birth_time, levels, 24, 100)

        # Access the "DasaForNow" level
        dasa_data = parse_all_dashas(all_dasha, levels, current_date)

        # Get the first planet key (mahadasha)
        planet_key = list(dasa_data.keys())[0]

        # Get the first sub-planet key (antardasha) from SubDasas
        sub_planet_key = list(dasa_data[planet_key]["SubDasas"].keys())[0]

        
    # except Exception as e:
    #     print(f"Error calculating dashas: {e}")
    #     dashas = {
    #         'mahadasha': {'planet': 'Unknown', 'start_date': '', 'end_date': ''},
    #         'antardasha': {'planet': 'Unknown', 'start_date': '', 'end_date': ''}
    #     }
    
    # Calculate yogas (planetary combinations)
    try:
        # Extract significant yogas from horoscope predictions
        yogas = []
        for yoga in horoscope_predictions:
            # Filter out general planet-in-sign and planet-in-house predictions
            if not any(yoga["Name"].startswith(f"{planet}In") for planet in [
                        "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus",
                        "Saturn", "Rahu", "Ketu"]) and not yoga["Name"].endswith("Rising"):
                yogas.append({
                    'name': yoga["Name"],
                    'description': yoga["Description"]
                })
    except Exception as e:
        print(f"Error calculating yogas: {e}")
        yogas = []
    
    # Prepare chart data
    chart_data = {
        'user_name': name,
        'gender': gender,
        'birth_time_str': str(birth_time),
        'birth_details': f"Birth: {date_str} {time_str}, Lat: {lat}°, Lon: {lon}°",
        'place_name': place_name,
        'ascendant': asc_sign,
        'asc_degree': asc_degree,
        'asc_reasoning': asc_reasoning,
        'planets': planets,
        'lunar_day': lunar_day,
        'lunar_day_num': lunar_day_num,
        'lunar_month': lunar_month,
        'lunar_year': lunar_year,
        'moon_void': moon_void,
        'dashas': all_dasha,
        'yogas': yogas
    }
    
    return chart_data, None

def calculate_transits(birth_time, location):
    """Calculate current planetary transits and their effects on the birth chart."""
    # try:
    if 1==1:
        # try to get transit data from db 
        # get transit data from db
        if 'user_id' not in session:
            return {
                'transits': [],
                'timestamp': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                'daily_forecast': "Could not calculate transit information."
            }
        
        transit_data = Transit.query.filter_by(user_id=session['user_id']).order_by(Transit.transit_date.desc()).first()



        if transit_data and (datetime.utcnow() - transit_data.transit_date).days == 0:
            daily_forecast = ""
                    # Add daily forecast based on Moon and Sun positions
            transits = json.loads(transit_data.transit_data)

            moon_transit = next((t for t in transits if t['planet'] == 'Moon'), None)
            sun_transit = next((t for t in transits if t['planet'] == 'Sun'), None)
            
            if moon_transit and sun_transit:
                moon_element = ELEMENT_MAP.get(moon_transit['sign'], "unknown")
                sun_sign = sun_transit['sign']
                
                daily_forecast = f"Today with the Moon in {moon_transit['sign']} ({ELEMENT_MAP.get(moon_transit['sign'], 'unknown')} element), "
                
                if moon_element == "fire":
                    daily_forecast += "your emotions may be more passionate and energetic. It's a good day for action and initiative."
                elif moon_element == "earth":
                    daily_forecast += "you may feel more grounded and practical. Good day for tangible progress and stability."
                elif moon_element == "air":
                    daily_forecast += "your mind is active and communicative. Great day for social connections and intellectual pursuits."
                elif moon_element == "water":
                    daily_forecast += "your intuition is heightened and emotions are flowing. Nurture yourself and your close relationships."
                
                daily_forecast += f" With the Sun in {sun_sign}, the overall focus of this period is on {PLANET_QUALITIES['Sun'][0]} and {PLANET_QUALITIES['Sun'][1]}."
            else:
                daily_forecast = "Could not generate daily forecast due to missing transit data."
            
        
            return {
                'transits': json.loads(transit_data.transit_data),
                'timestamp': transit_data.transit_date.strftime("%Y-%m-%d %H:%M:%S UTC"),
                'daily_forecast': daily_forecast
            }
        
        else:
            # Get current time
            current_time = Time(datetime.now().strftime("%H:%M %d/%m/%Y +00:00"), location)
            
            # Extract birth chart data
            birth_chart_planets = []
            planets_data = Calculate.AllPlanetData(PlanetName.All, birth_time)
            # convert list to dict
            planets_data = {list(d.keys())[0]: list(d.values())[0] for d in planets_data}
            for planet in [PlanetName.Sun, PlanetName.Moon, PlanetName.Mars,
                        PlanetName.Mercury, PlanetName.Jupiter, PlanetName.Venus,
                        PlanetName.Saturn, PlanetName.Rahu, PlanetName.Ketu]:
                planet_data = planets_data[planet.value]
                planet_name = PLANET_DISPLAY_NAMES[planet]
                
                if 'PlanetRasiD1Sign' in planet_data and isinstance(planet_data['PlanetRasiD1Sign'], dict):
                    sign = planet_data['PlanetRasiD1Sign']['Name']
                    degree = float(planet_data['PlanetRasiD1Sign']['DegreesIn']['TotalDegrees'])
                    birth_chart_planets.append({
                        'name': planet_name,
                        'sign': sign,
                        'degree': degree,
                        'total_degrees': (SIGNS.index(sign) * 30) + degree
                    })
            
            # Calculate current transits
            transits = []
            all_transit_data = Calculate.AllPlanetData(PlanetName.All, current_time)
            all_transit_data = {list(d.keys())[0]: list(d.values())[0] for d in all_transit_data}
            # convert 
            for planet in [PlanetName.Sun, PlanetName.Moon, PlanetName.Mars,
                        PlanetName.Mercury, PlanetName.Jupiter, PlanetName.Venus,
                        PlanetName.Saturn, PlanetName.Rahu, PlanetName.Ketu]:
                transit_data = all_transit_data[planet.value]
                planet_name = PLANET_DISPLAY_NAMES[planet]
                
                if 'PlanetRasiD1Sign' in transit_data and isinstance(transit_data['PlanetRasiD1Sign'], dict):
                    sign = transit_data['PlanetRasiD1Sign']['Name']
                    degree = float(transit_data['PlanetRasiD1Sign']['DegreesIn']['TotalDegrees'])
                    total_degrees = (SIGNS.index(sign) * 30) + degree
                    
                    # Calculate aspects to natal planets
                    aspects = []
                    for natal_planet in birth_chart_planets:
                        angle_diff = abs(total_degrees - natal_planet['total_degrees']) % 360
                        
                        # Define aspect types
                        aspect_type = None
                        if 0 <= angle_diff <= 10 or 350 <= angle_diff <= 360:
                            aspect_type = "conjunction"
                            effect = "strong"
                        elif 170 <= angle_diff <= 190:
                            aspect_type = "opposition"
                            effect = "challenging"
                        elif 110 <= angle_diff <= 130:
                            aspect_type = "trine"
                            effect = "harmonious"
                        elif 80 <= angle_diff <= 100:
                            aspect_type = "square"
                            effect = "tense"
                        elif 50 <= angle_diff <= 70:
                            aspect_type = "sextile"
                            effect = "favorable"
                        
                        if aspect_type:
                            aspects.append({
                                'natal_planet': natal_planet['name'],
                                'aspect_type': aspect_type,
                                'angle': round(angle_diff, 2),
                                'effect': effect,
                                'description': f"Transit {planet_name} is making a {aspect_type} to your natal {natal_planet['name']}, creating a {effect} influence."
                            })
                    
                    # Get interpretation for this transit
                    interpretation = f"{planet_name} is currently transiting through {sign} at {degree:.2f}°."
                    if planet_name == "Moon":
                        interpretation += f" The Moon changes signs every 2.5 days, influencing your emotions and subconscious."
                    elif planet_name == "Sun":
                        interpretation += f" The Sun transits through each sign for about a month, highlighting areas of focus and vitality."
                    elif planet_name in ["Jupiter", "Saturn"]:
                        interpretation += f" This is a significant long-term transit that shapes the {planet_name} themes in your life during this period."
                    
                    # Add significance for outer planets
                    significance = "minor" if planet_name in ["Moon", "Mercury", "Venus"] else "moderate" if planet_name in ["Sun", "Mars"] else "major"
                    
                    transits.append({
                        'planet': planet_name,
                        'sign': sign,
                        'degree': degree,
                        'symbol': PLANET_SYMBOLS[planet_name],
                        'sign_symbol': SIGN_SYMBOLS[sign],
                        'interpretation': interpretation,
                        'aspects': sorted(aspects, key=lambda x: x['effect'] == "strong" or x['effect'] == "challenging", reverse=True)[:3],
                        'significance': significance,
                        'color': PLANET_COLORS.get(planet_name, "#000000"),
                        'element': ELEMENT_MAP.get(sign, "unknown"),
                        'modality': MODALITY_MAP.get(sign, "unknown")
                    })
            
            # Add daily forecast based on Moon and Sun positions
            moon_transit = next((t for t in transits if t['planet'] == 'Moon'), None)
            sun_transit = next((t for t in transits if t['planet'] == 'Sun'), None)
            
            if moon_transit and sun_transit:
                moon_element = ELEMENT_MAP.get(moon_transit['sign'], "unknown")
                sun_sign = sun_transit['sign']
                
                daily_forecast = f"Today with the Moon in {moon_transit['sign']} ({ELEMENT_MAP.get(moon_transit['sign'], 'unknown')} element), "
                
                if moon_element == "fire":
                    daily_forecast += "your emotions may be more passionate and energetic. It's a good day for action and initiative."
                elif moon_element == "earth":
                    daily_forecast += "you may feel more grounded and practical. Good day for tangible progress and stability."
                elif moon_element == "air":
                    daily_forecast += "your mind is active and communicative. Great day for social connections and intellectual pursuits."
                elif moon_element == "water":
                    daily_forecast += "your intuition is heightened and emotions are flowing. Nurture yourself and your close relationships."
                
                daily_forecast += f" With the Sun in {sun_sign}, the overall focus of this period is on {PLANET_QUALITIES['Sun'][0]} and {PLANET_QUALITIES['Sun'][1]}."
            else:
                daily_forecast = "Could not generate daily forecast due to missing transit data."
            
            # Save transit data to database 
            new_transit = Transit(user_id=session['user_id'], transit_data=json.dumps(transits), transit_date=datetime.utcnow())
            db.session.add(new_transit)
            db.session.commit()


            return {
                'transits': transits,
                'timestamp': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                'daily_forecast': daily_forecast
            }
    # except Exception as e:
    #     print(f"Error calculating transits: {e}")
    #     return {
    #         'transits': [],
    #         'timestamp': datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
    #         'daily_forecast': "Could not calculate transit information."
    #     }

def calculate_compatibility(birth_time1, birth_time2):
    """Calculate astrological compatibility between two birth charts."""
    try:
        # Get match report from vedastro
        match_report = Calculate.MatchReport(birth_time1, birth_time2)
        
        # Build custom compatibility scores
        compatibility = {
            'overall_score': 0,
            'emotional_compatibility': 0,
            'communication_compatibility': 0,
            'physical_compatibility': 0,
            'spiritual_compatibility': 0,
            'longevity_potential': "",
            'areas': []
        }
        
        # Get moon signs (very important in Vedic compatibility)
        moon1_data = Calculate.AllPlanetData(PlanetName.Moon, birth_time1)
        moon2_data = Calculate.AllPlanetData(PlanetName.Moon, birth_time2)
        
        moon1_sign = moon1_data['PlanetRasiD1Sign']['Name']
        moon2_sign = moon2_data['PlanetRasiD1Sign']['Name']
        
        # Calculate moon sign distance (important for emotional compatibility)
        moon1_index = SIGNS.index(moon1_sign)
        moon2_index = SIGNS.index(moon2_sign)
        moon_distance = (moon2_index - moon1_index) % 12
        
        # Calculate nakshatra compatibility
        moon1_nakshatra = Calculate.Nakshatra(PlanetName.Moon, birth_time1)
        moon2_nakshatra = Calculate.Nakshatra(PlanetName.Moon, birth_time2)
        
        # Calculate ashtakuta scores (traditional Vedic compatibility system)
        # This is a simplified version
        varna_score = match_report.get('Varna', 0)
        vasya_score = match_report.get('Vasya', 0) 
        tara_score = match_report.get('Tara', 0)
        yoni_score = match_report.get('Yoni', 0)
        graha_maitri_score = match_report.get('GrahaMaitri', 0)
        gana_score = match_report.get('Gana', 0)
        bhakut_score = match_report.get('Bhakut', 0)
        nadi_score = match_report.get('Nadi', 0)
        
        # Total possible score is 36, calculate percentage
        total_ashtakuta = (varna_score + vasya_score + tara_score + yoni_score + 
                          graha_maitri_score + gana_score + bhakut_score + nadi_score)
        ashtakuta_percentage = round((total_ashtakuta / 36) * 100)
        
        # Set overall score based on ashtakuta
        compatibility['overall_score'] = ashtakuta_percentage
        
        # Calculate emotional compatibility based on moon signs and nakshatras
               # Calculate emotional compatibility based on moon signs and nakshatras
        emotional_score = 0
        
        # Vedic astrology considers certain distances harmonious
        harmonious_distances = [3, 5, 7, 9, 11]  # Trine, sextile, etc.
        if moon_distance in harmonious_distances:
            emotional_score = 80 + (moon_distance * 2)  # Higher score for more harmonious aspects
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
        
        # Spiritual compatibility (Jupiter)
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
        
        # Add areas of strength and weakness
        if compatibility["emotional_compatibility"] >= 75:
            compatibility["areas"].append({
                "title": "Strong Emotional Connection",
                "description": f"The Moon signs ({moon1_sign} and {moon2_sign}) are harmoniously placed, suggesting a natural emotional understanding.",
                "score": compatibility["emotional_compatibility"]
            })
        elif compatibility["emotional_compatibility"] <= 60:
            compatibility["areas"].append({
                "title": "Emotional Adjustment Needed",
                "description": f"The Moon signs ({moon1_sign} and {moon2_sign}) may create emotional misunderstandings. Patience and communication will be important.",
                "score": compatibility["emotional_compatibility"]
            })
        
        if compatibility["communication_compatibility"] >= 75:
            compatibility["areas"].append({
                "title": "Excellent Communication",
                "description": "Mercury positions suggest you understand each other's thought processes naturally.",
                "score": compatibility["communication_compatibility"]
            })
        
        if compatibility["physical_compatibility"] >= 80:
            compatibility["areas"].append({
                "title": "Strong Physical Attraction",
                "description": "The Mars-Venus connection indicates a powerful physical chemistry.",
                "score": compatibility["physical_compatibility"]
            })
        
        return compatibility
    except Exception as e:
        print(f"Error calculating compatibility: {e}")
        return {
            'overall_score': 50,
            'emotional_compatibility': 50,
            'communication_compatibility': 50,
            'physical_compatibility': 50,
            'spiritual_compatibility': 50,
            'longevity_potential': "Could not calculate",
            'areas': [{
                "title": "Calculation Error",
                "description": f"Could not calculate detailed compatibility: {str(e)}",
                "score": 0
            }]
        }

def query_ai_model(prompt):
    """Query the AI model for insights."""
    try:
        # messages = [{"role": "user", "content": prompt}]
        
        # completion = client.chat.completions.create(
        #     model="deepseek-ai/DeepSeek-R1",
        #     messages=messages,
        #     max_tokens=500,
        # )
        
        # response_text = completion.choices[0].message['content']
        # response_text = re.sub(r'<think>.*?</think>\s*', '', response_text, flags=re.DOTALL)
        
        # return response_text
        message_result = chatbot.chat(prompt)
        message_str: str = message_result.wait_until_done()
        return message_str
    except Exception as e:
        print(f"AI model query error: {e}")
        return f"Could not generate AI response: {str(e)}"

def generate_ai_interpretation(chart_data, question=None):
    """Generate AI interpretation of a chart or answer a specific question."""
    try:
        # Create prompt with chart data
        prompt = "In Vedic astrology, based on the following birth chart:\n"
        prompt += f"Ascendant: {chart_data['ascendant']} at {chart_data['asc_degree']:.2f}°\n"
        
        for planet in chart_data['planets']:
            prompt += f"{planet['name']}: {planet['sign']} at {planet['degree']:.2f}° in house {planet['house']}"
            if planet.get('is_retrograde'):
                prompt += " (Retrograde)"
            prompt += "\n"
        
        # Add yogas if available
        if chart_data.get('yogas') and len(chart_data['yogas']) > 0:
            prompt += "\nSignificant yogas (planetary combinations):\n"
            for yoga in chart_data['yogas'][:3]:  # Limit to top 3
                prompt += f"- {yoga['name']}\n"
        
        # Add dasha information
        prompt += f"\nCurrent dasha periods: {chart_data['dashas']['mahadasha']['planet']} Mahadasha, {chart_data['dashas']['antardasha']['planet']} Antardasha\n"
        
        # If there's a specific question, add it
        if question:
            prompt += f"\nQuestion: {question}\n"
            prompt += "Provide a concise Vedic astrological interpretation for the above question, keep your answers relevant and to the point, think before you answer, do not repeat the question again in the response."
        else:
            prompt += "\nProvide a concise Vedic astrological reading of this chart in a concise tone keep your answers relevant and to the point, think before you answer, do not repeat the question again in the response."
        
        # Query the model
        response = query_ai_model(prompt)

        # convert markdown to html
        response = markdown.markdown(response)


        return response
    except Exception as e:
        print(f"Error generating AI interpretation: {e}")
        return f"Could not generate interpretation: {str(e)}"


def parse_all_dashas(dasa_response):
    # Extract DasaForLife from the response payload
    dasa_data = dasa_response["Payload"]["DasaForLife"]
    
    # Structure to hold all dashas
    all_dashas = []
    
    # Iterate through all mahadashas
    for planet_key, mahadasha in dasa_data.items():
        mahadasha_info = {
            "planet": mahadasha["Lord"],
            "start_date": mahadasha["Start"],
            "end_date": mahadasha["End"],
            "description": mahadasha["Description"],
            "nature": mahadasha["Nature"],
            "antardashas": []
        }
        
        # Add all antardashas (SubDasas) for this mahadasha
        for sub_planet_key, antardasha in mahadasha["SubDasas"].items():
            antardasha_info = {
                "planet": antardasha["Lord"],
                "start_date": antardasha["Start"],
                "end_date": antardasha["End"],
                "description": antardasha["Description"],
                "nature": antardasha["Nature"]
            }
            mahadasha_info["antardashas"].append(antardasha_info)
        
        all_dashas.append(mahadasha_info)

    return all_dashas
# Routes and Views
@app.route('/')
def home():
    """Homepage with birth chart form."""
    

    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate_chart():
    """Calculate and display birth chart."""
    try:
        # Extract form data
        date_str = request.form['date']
        time_str = request.form['time']
        location = request.form['location']
        name = request.form.get('name', '')
        gender = request.form.get('gender', '')
        
        # Calculate chart
        chart_data, error = calculate_birth_chart(date_str, time_str, location, name, gender)
        
        if error:
            return render_template('index.html', error=error)
        
        # Store chart data in session
        session['chart_data'] = json.dumps(chart_data)
        # also save the chart data in the database
        save_chart_data(chart_data)

        
        return render_template('chart.html', 
                              chart=chart_data,
                              SIGNS=SIGNS,
                              SIGN_SYMBOLS=SIGN_SYMBOLS,
                              PLANET_SYMBOLS=PLANET_SYMBOLS,
                              ELEMENT_MAP=ELEMENT_MAP,
                              MODALITY_MAP=MODALITY_MAP,
                              HOUSE_MEANINGS=HOUSE_MEANINGS)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error calculating chart: {error_details}")
        return render_template('index.html', error=f"Error calculating chart: {str(e)}")

@app.route('/chart')
def chart():
    """View a previously calculated birth chart."""
    if 'user_id' not in session:
        return redirect(url_for('home'))
    
    chart_data = User.query.filter_by(id=session['user_id']).first().birth_chart
    
    chart_data = json.loads(chart_data)
    return render_template('chart.html', 
                          chart=chart_data,
                          SIGNS=SIGNS,
                          SIGN_SYMBOLS=SIGN_SYMBOLS,
                          PLANET_SYMBOLS=PLANET_SYMBOLS,
                          ELEMENT_MAP=ELEMENT_MAP,
                          MODALITY_MAP=MODALITY_MAP,
                          HOUSE_MEANINGS=HOUSE_MEANINGS)

@app.route('/transits')
def transits():
    """Show current transits for the user's chart."""

    if 'user_id' not in session:
        print("User not logged in")
        return redirect(url_for('login'))
    
    # get user's chart data from db 
    
    try:
        chart_data = User.query.filter_by(id=session['user_id']).first()
        chart_data = json.loads(chart_data.birth_chart)
        
        # Recreate birth_time object
        date_str = chart_data['birth_details'].split('Birth: ')[1].split(',')[0].strip()
        time_str = chart_data['birth_details'].split(date_str)[1].split(',')[0].strip()
        lat = float(chart_data['birth_details'].split('Lat: ')[1].split('°')[0])
        lon = float(chart_data['birth_details'].split('Lon: ')[1].split('°')[0])
        
        geo_location = GeoLocation(chart_data['place_name'], lon, lat)
        
        year, month, day = date_str.split('-')
        formatted_date = f"{day}/{month}/{year}"
        
        timezone = get_timezone(lat, lon)
        birth_time = Time(f"{time_str} {formatted_date} {timezone}", geo_location)
        
        # Calculate transits
        transit_data = calculate_transits(birth_time, geo_location)
        
        # Generate AI interpretation
        transit_interpretation = generate_ai_interpretation(chart_data, "How are the current transits affecting this chart?")
        

        return render_template('transits.html',
                              chart=chart_data,
                              transits=transit_data,
                              SIGNS=SIGNS,
                              interpretation= transit_interpretation,
                              current_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                              PLANET_SYMBOLS=PLANET_SYMBOLS,
                              SIGN_SYMBOLS=SIGN_SYMBOLS)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error calculating transits: {error_details}")
        return redirect(url_for('home', error=f"Error calculating transits: {str(e)}"))

@app.route('/compatibility', methods=['GET', 'POST'])
def compatibility():
    """Calculate compatibility between two charts."""
    if request.method == 'GET':
        return render_template('compatibility.html')
    
    try:
        # Get user's chart data from session
        if 'chart_data' not in session:
            return render_template('compatibility.html', error="Please create your birth chart first")
        
        user_chart = json.loads(session['chart_data'])
        
        # Extract friend's data from form
        friend_name = request.form['friend_name']
        date_str = request.form['date']
        time_str = request.form['time']
        location = request.form['location']
        
        # Calculate friend's chart
        friend_chart_data, error = calculate_birth_chart(date_str, time_str, location, friend_name)
        
        if error:
            return render_template('compatibility.html', error=error)
        
        # Recreate birth time objects
        # User
        user_date = user_chart['birth_details'].split('Birth: ')[1].split(',')[0].strip()
        user_time = user_chart['birth_details'].split(user_date)[1].split(',')[0].strip()
        user_lat = float(user_chart['birth_details'].split('Lat: ')[1].split('°')[0])
        user_lon = float(user_chart['birth_details'].split('Lon: ')[1].split('°')[0])
        
        user_geo = GeoLocation(user_chart['place_name'], user_lon, user_lat)
        
        user_year, user_month, user_day = user_date.split('-')
        user_formatted_date = f"{user_day}/{user_month}/{user_year}"
        
        user_timezone = get_timezone(user_lat, user_lon)
        user_birth_time = Time(f"{user_time} {user_formatted_date} {user_timezone}", user_geo)
        
        # Friend
        friend_geo = GeoLocation(friend_chart_data['place_name'], 
                                float(friend_chart_data['birth_details'].split('Lon: ')[1].split('°')[0]),
                                float(friend_chart_data['birth_details'].split('Lat: ')[1].split('°')[0]))
        
        friend_year, friend_month, friend_day = date_str.split('-')
        friend_formatted_date = f"{friend_day}/{friend_month}/{friend_year}"
        
        friend_timezone = get_timezone(float(friend_chart_data['birth_details'].split('Lat: ')[1].split('°')[0]),
                                     float(friend_chart_data['birth_details'].split('Lon: ')[1].split('°')[0]))
        friend_birth_time = Time(f"{time_str} {friend_formatted_date} {friend_timezone}", friend_geo)
        
        # Calculate compatibility
        compatibility_data = calculate_compatibility(user_birth_time, friend_birth_time)
        
        # Generate AI interpretation
               # Generate AI interpretation
        compatibility_prompt = (
            f"In Vedic astrology, analyze the compatibility between these two charts:\n\n"
            f"Person 1 (User): Ascendant {user_chart['ascendant']}, "
            f"Sun in {next((p['sign'] for p in user_chart['planets'] if p['name'] == 'Sun'), 'Unknown')}, "
            f"Moon in {next((p['sign'] for p in user_chart['planets'] if p['name'] == 'Moon'), 'Unknown')}, "
            f"Venus in {next((p['sign'] for p in user_chart['planets'] if p['name'] == 'Venus'), 'Unknown')}\n\n"
            f"Person 2 (Friend - {friend_name}): Ascendant {friend_chart_data['ascendant']}, "
            f"Sun in {next((p['sign'] for p in friend_chart_data['planets'] if p['name'] == 'Sun'), 'Unknown')}, "
            f"Moon in {next((p['sign'] for p in friend_chart_data['planets'] if p['name'] == 'Moon'), 'Unknown')}, "
            f"Venus in {next((p['sign'] for p in friend_chart_data['planets'] if p['name'] == 'Venus'), 'Unknown')}\n\n"
            f"The compatibility score is {compatibility_data['overall_score']}%, with emotional compatibility at {compatibility_data['emotional_compatibility']}% "
            f"and communication compatibility at {compatibility_data['communication_compatibility']}%.\n\n"
            f"Provide a comprehensive Vedic astrological compatibility interpretation addressing strengths, challenges, and potential."
        )
        
        compatibility_interpretation = query_ai_model(compatibility_prompt)
        
        # Store friend's chart in database if user is logged in
        if 'user_id' in session:
            user_id = session['user_id']
            
            # Check if friend already exists
            existing_friend = Friend.query.filter_by(
                user_id=user_id, 
                friend_name=friend_name,
                birth_time=str(friend_birth_time)
            ).first()
            
            if not existing_friend:
                new_friend = Friend(
                    user_id=user_id,
                    friend_name=friend_name,
                    compatibility_score=compatibility_data['overall_score'],
                    birth_time=str(friend_birth_time),
                    birth_chart=json.dumps(friend_chart_data)
                )
                db.session.add(new_friend)
                db.session.commit()
        
        return render_template('compatibility_result.html',
                              user_chart=user_chart,
                              friend_chart=friend_chart_data,
                              friend_name=friend_name,
                              compatibility=compatibility_data,
                              interpretation=compatibility_interpretation,
                              PLANET_SYMBOLS=PLANET_SYMBOLS,
                              SIGN_SYMBOLS=SIGN_SYMBOLS)
    
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error calculating compatibility: {error_details}")
        return render_template('compatibility.html', error=f"Error calculating compatibility: {str(e)}")

@app.route('/query', methods=['POST'])
def handle_query():
    """Handle queries about the user's chart."""
    try:
        if 'user_id' not in session:
            return jsonify({'response': "Please log in to access this feature.", 'reasoning': "User not logged in."})

        # if 'chart_data' not in session:
        #     return jsonify({'response': "Please calculate your birth chart first.", 'reasoning': "No chart data in session."})
        
        data = request.json
        if not data or 'question' not in data:
            return jsonify({'response': "Error: Invalid request data", 'reasoning': "Missing question data"}), 400
        
        question = data['question'].strip()

        chart_data = User.query.filter_by(id=session['user_id']).first().birth_chart
        chart_data = json.loads(chart_data)

        # chart_data = json.loads(session['chart_data'])
        
        # Generate AI interpretation
        response = generate_ai_interpretation(chart_data, question)
        print(response)
        
        return jsonify({
            'response': response,
            'reasoning': f"Response generated based on your {chart_data['ascendant']} ascendant chart and the provided planetary positions."
        })
        
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Query error: {error_details}")
        return jsonify({
            'response': f"Error: {str(e)}",
            'reasoning': "Something went wrong processing your question."
        }), 400

@app.route('/daily')
def daily_horoscope():
    """Show daily transit information."""
    # if 'chart_data' not in session:
    #     return redirect(url_for('home', message="Please create your birth chart first"))
    
    try:
        
        user_id = session['user_id']

        chart_data = User.query.filter_by(id=user_id).first().birth_chart
        chart_data = json.loads(chart_data)
        
        # Recreate birth_time object
        date_str = chart_data['birth_details'].split('Birth: ')[1].split(',')[0].strip()
        time_str = chart_data['birth_details'].split(date_str)[1].split(',')[0].strip()
        lat = float(chart_data['birth_details'].split('Lat: ')[1].split('°')[0])
        lon = float(chart_data['birth_details'].split('Lon: ')[1].split('°')[0])
        
        geo_location = GeoLocation(chart_data['place_name'], lon, lat)
        
        year, month, day = date_str.split('-')
        formatted_date = f"{day}/{month}/{year}"
        
        timezone = get_timezone(lat, lon)
        birth_time = Time(f"{time_str} {formatted_date} {timezone}", geo_location)
        
        # Calculate transits
        transit_data = calculate_transits(birth_time, location=geo_location)
        # Generate daily forecast
        daily_prompt = (
            f"Based on the current transits for a person with {chart_data['ascendant']} Ascendant, "
            f"Sun in {next((p['sign'] for p in chart_data['planets'] if p['name'] == 'Sun'), 'Unknown')}, "
            f"and Moon in {next((p['sign'] for p in chart_data['planets'] if p['name'] == 'Moon'), 'Unknown')}, "
            f"provide a brief daily Vedic astrology forecast for today. "
            f"The current transits show Moon in {next((t['sign'] for t in transit_data['transits'] if t['planet'] == 'Moon'), 'Unknown')}, "
            f"Sun in {next((t['sign'] for t in transit_data['transits'] if t['planet'] == 'Sun'), 'Unknown')}. "
            f"Keep the response concise and focused on daily themes and advice."
        )
        
        daily_message = query_ai_model(daily_prompt)

        return render_template('daily.html',
                              chart=chart_data,
                              transits=transit_data,
                              SIGNS=SIGNS,
                              HOUSE_MEANINGS=HOUSE_MEANINGS,
                              daily_message=daily_message,
                              current_date=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC"),
                              PLANET_SYMBOLS=PLANET_SYMBOLS,
                              SIGN_SYMBOLS=SIGN_SYMBOLS)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error calculating daily horoscope: {error_details}")
        return redirect(url_for('home', error=f"Error calculating daily horoscope: {str(e)}"))

@app.route('/dashas')
def dasha_periods():
    """Show Vimshottari Dasha periods for the user's chart."""
    if 'user_id' not in session:
        return redirect(url_for('login', next=url_for('dashas')))


    
    try:
            
        chart_data = User.query.filter_by(id=session['user_id']).first().birth_chart
        chart_data = json.loads(chart_data)
        
        # Dashas are already calculated in chart_data
        mahadasha = chart_data['dashas']['mahadasha']  
        antardasha = chart_data['dashas']['antardasha']
        
        # Generate interpretation
        dasha_prompt = (
            f"In Vedic astrology, explain the effects of the current {mahadasha['planet']} Mahadasha and {antardasha['planet']} Antardasha "
            f"for a person with {chart_data['ascendant']} Ascendant, "
            f"Sun in {next((p['sign'] for p in chart_data['planets'] if p['name'] == 'Sun'), 'Unknown')}, "
            f"and Moon in {next((p['sign'] for p in chart_data['planets'] if p['name'] == 'Moon'), 'Unknown')}. "
            f"Provide information about the general themes of these dasha periods, their impact on life areas, and advice for navigating them."
        )
        
        dasha_interpretation = query_ai_model(dasha_prompt)
        
        return render_template('dashas.html',
                              chart=chart_data,
                              dasha_interpretation=dasha_interpretation,
                              PLANET_SYMBOLS=PLANET_SYMBOLS)
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error calculating dasha periods: {error_details}")
        return redirect(url_for('home', error=f"Error calculating dasha periods: {str(e)}"))

@app.route('/journal', methods=['GET', 'POST'])
def journal():
    """User's astrological journal for tracking moods and insights."""

    print(session.items())

    if 'user_id' not in session:
        return redirect(url_for('login', next=url_for('journal')))
    
    if request.method == 'POST':
        content = request.form['content']
        mood = request.form['mood']
        
        # Get current moon sign
        current_time = datetime.now()



        moon_data = Calculate.AllPlanetData(PlanetName.Moon, current_time)
        moon_sign = moon_data['PlanetRasiD1Sign']['Name']
        
        entry = JournalEntry(
            user_id=session['user_id'],
            content=content,
            mood=mood,
            moon_sign=moon_sign
        )
        
        db.session.add(entry)
        db.session.commit()
        
        flash('Journal entry added successfully!', 'success')
        return redirect(url_for('journal'))
    
    # Get user's entries
    entries = JournalEntry.query.filter_by(user_id=session['user_id']).order_by(JournalEntry.entry_date.desc()).all()
    
    # Get current moon sign for new entry
    current_time = Time(f"{datetime.now().strftime('%H:%M:%S')} {datetime.now().strftime('%d/%m/%Y')} UTC", GeoLocation('Greenwich', 0, 0))
    moon_data = Calculate.AllPlanetData(PlanetName.Moon, current_time)
    current_moon_sign = moon_data['PlanetRasiD1Sign']['Name']
    
    return render_template('journal.html', 
                          entries=entries,
                          current_moon_sign=current_moon_sign,
                          SIGN_SYMBOLS=SIGN_SYMBOLS)

# User authentication routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        
        # Check if user already exists
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return render_template('register.html', error="Username already exists")
        
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            return render_template('register.html', error="Email already in use")
        
        # Create new user
        hashed_password = generate_password_hash(password)
        new_user = User(username=username, email=email, password_hash=hashed_password)
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Registration successful! Please log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            session['username'] = user.username
            

            next_page = request.args.get('next', url_for('home'))
            return redirect(next_page)
        else:
            return render_template('login.html', error="Invalid username or password")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/profile')
def profile():
    
    # await to get the session items

    print(session.keys())
    print(session['user_id'])
    
    if 'user_id' not in session.keys():
        print("User not logged in, redirecting to login page")
        return redirect(url_for('login', next=url_for('profile')))
    
    user = User.query.get(session['user_id'])
    friends = Friend.query.filter_by(user_id=user.id).all()
    
    return render_template('profile.html', current_user=user, friends=friends)

@app.route('/save_chart', methods=['POST'])
def save_chart():
    if 'user_id' not in session or 'chart_data' not in session:
        return jsonify({'success': False, 'message': 'User not logged in or no chart data'}), 403
    
    user = User.query.get(session['user_id'])
    user.birth_chart = session['chart_data']
    user.birth_time = json.loads(session['chart_data']).get('birth_time_str', '')
    
    db.session.commit()
    
    return jsonify({'success': True, 'message': 'Chart saved to your profile'})


def save_chart_data(chart_data):
    if 'user_id' not in session:
        print("User not logged in, cannot save chart data")
        return
    user = User.query.get(session['user_id'])
    user.birth_chart = json.dumps(chart_data)
    user.birth_time = chart_data.get('birth_time_str', '')
    
    db.session.commit()

@app.template_filter('format_date')
def format_date_filter(date_str, format_str='%Y-%m-%d'):
    """Format a date string for templates."""
    try:
        if isinstance(date_str, datetime):
            return date_str.strftime(format_str)
        parts = date_str.split('/')
        if len(parts) == 3:
            day, month, year = parts
            dt = datetime(int(year), int(month), int(day))
            return dt.strftime(format_str)
        return date_str
    except:
        return date_str

# Initialize database
@app.before_request
def create_tables():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)