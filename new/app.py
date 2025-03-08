# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.urandom(24)

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Authentication would go here
        session['user_id'] = email  # Simplified for demo
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        dob = request.form.get('dob')
        birth_time = request.form.get('birth_time')
        birth_place = request.form.get('birth_place')
        
        # User creation would go here
        session['user_id'] = email  # Simplified for demo
        return redirect(url_for('dashboard'))
    return render_template('signup.html')

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Placeholder data - would be calculated from actual birth info
    user_data = {
        'moon_sign': 'Taurus',
        'ascendant': 'Leo',
        'sun_sign': 'Aries',
        'dashas': {
            'current': 'Venus Mahadasha',
            'remaining': '12 years, 3 months'
        },
        'planets': [
            {'name': 'Sun', 'sign': 'Aries', 'house': 9, 'degrees': 15.23},
            {'name': 'Moon', 'sign': 'Taurus', 'house': 10, 'degrees': 8.45},
            {'name': 'Mercury', 'sign': 'Pisces', 'house': 8, 'degrees': 3.12},
            {'name': 'Venus', 'sign': 'Aquarius', 'house': 7, 'degrees': 27.89},
            {'name': 'Mars', 'sign': 'Capricorn', 'house': 6, 'degrees': 19.56},
            {'name': 'Jupiter', 'sign': 'Sagittarius', 'house': 5, 'degrees': 5.67},
            {'name': 'Saturn', 'sign': 'Scorpio', 'house': 4, 'degrees': 11.34},
            {'name': 'Rahu', 'sign': 'Libra', 'house': 3, 'degrees': 22.78},
            {'name': 'Ketu', 'sign': 'Aries', 'house': 9, 'degrees': 22.78}
        ],
        'daily_update': {
            'date': datetime.now().strftime('%B %d, %Y'),
            'transits': [
                'Moon enters Gemini',
                'Venus squares Mars',
                'Jupiter retrograde in Sagittarius'
            ],
            'forecast': 'Today brings intellectual stimulation and curiosity as the Moon transits Gemini. Communication flows easily, but Venus square Mars may create tension in relationships. Focus on balancing action with diplomacy.'
        }
    }
    
    return render_template('dashboard.html', user_data=user_data)

@app.route('/birth_chart')
def birth_chart():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Placeholder data
    chart_data = {
        'ascendant': 'Leo',
        'houses': {
            1: {'sign': 'Leo', 'planets': ['None']},
            2: {'sign': 'Virgo', 'planets': ['None']},
            3: {'sign': 'Libra', 'planets': ['Rahu']},
            4: {'sign': 'Scorpio', 'planets': ['Saturn']},
            5: {'sign': 'Sagittarius', 'planets': ['Jupiter']},
            6: {'sign': 'Capricorn', 'planets': ['Mars']},
            7: {'sign': 'Aquarius', 'planets': ['Venus']},
            8: {'sign': 'Pisces', 'planets': ['Mercury']},
            9: {'sign': 'Aries', 'planets': ['Sun', 'Ketu']},
            10: {'sign': 'Taurus', 'planets': ['Moon']},
            11: {'sign': 'Gemini', 'planets': ['None']},
            12: {'sign': 'Cancer', 'planets': ['None']}
        }
    }
    
    return render_template('birth_chart.html', chart_data=chart_data)

@app.route('/compatibility')
def compatibility():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('compatibility.html')

@app.route('/compatibility/result', methods=['POST'])
def compatibility_result():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    partner_name = request.form.get('partner_name')
    partner_dob = request.form.get('partner_dob')
    partner_time = request.form.get('partner_time')
    partner_place = request.form.get('partner_place')
    
    # Placeholder data - would be calculated based on both birth charts
    compatibility_data = {
        'overall_score': 28,
        'max_score': 36,
        'percentage': 78,
        'aspects': [
            {'name': 'Varna (Class)', 'score': 1, 'max': 1, 'description': 'Social compatibility'},
            {'name': 'Vashya (Dominance)', 'score': 2, 'max': 2, 'description': 'Mutual control and influence'},
            {'name': 'Tara (Prosperity)', 'score': 3, 'max': 3, 'description': 'Mutual prosperity and well-being'},
            {'name': 'Yoni (Physical)', 'score': 3, 'max': 4, 'description': 'Sexual compatibility'},
            {'name': 'Graha Maitri (Planetary)', 'score': 5, 'max': 5, 'description': 'Friendship between lords of moon signs'},
            {'name': 'Gana (Temperament)', 'score': 4, 'max': 6, 'description': 'Psychological compatibility'},
            {'name': 'Bhakut (Social Harmony)', 'score': 6, 'max': 7, 'description': 'Long-term relationship harmony'},
            {'name': 'Nadi (Health)', 'score': 4, 'max': 8, 'description': 'Health and genetic compatibility'}
        ],
        'recommendation': 'This match scores well in most categories, particularly in planetary friendship and social harmony. The lower score in health compatibility (Nadi) suggests potential challenges related to health or genetic factors. Overall, this is considered a favorable match in Vedic astrology with a good foundation for long-term harmony.',
        'elements': {
            'you': {'fire': 35, 'earth': 25, 'air': 15, 'water': 25},
            'partner': {'fire': 20, 'earth': 30, 'air': 30, 'water': 20}
        }
    }
    
    return render_template('compatibility_result.html', partner_name=partner_name, compatibility_data=compatibility_data)

@app.route('/dashas')
def dashas():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Placeholder dasha data
    dasha_data = {
        'current_mahadasha': {
            'planet': 'Venus',
            'start_date': 'May 12, 2018',
            'end_date': 'May 12, 2038',
            'description': 'Venus Mahadasha often brings harmony, creativity, and material comforts. This is generally a period of pleasure, relationships, and artistic expression. Financial gains and satisfying partnerships are likely during this 20-year cycle.'
        },
        'current_antardasha': {
            'planet': 'Saturn',
            'start_date': 'September 12, 2023',
            'end_date': 'November 12, 2026',
            'description': 'Venus-Saturn period combines pleasure with discipline. You may experience delayed but solid rewards, especially in career and finances. Relationships may face tests but can become stronger. Focus on patience and structured approach to creativity.'
        },
        'upcoming_antardashas': [
            {
                'planet': 'Mercury',
                'start_date': 'November 12, 2026',
                'end_date': 'September 12, 2029',
                'duration': '2 years, 10 months'
            },
            {
                'planet': 'Ketu',
                'start_date': 'September 12, 2029',
                'end_date': 'November 12, 2030',
                'duration': '1 year, 2 months'
            },
            {
                'planet': 'Venus',
                'start_date': 'November 12, 2030',
                'end_date': 'January 12, 2034',
                'duration': '3 years, 2 months'
            }
        ],
        'past_maharashas': [
            {
                'planet': 'Moon',
                'start_date': 'May 12, 2008',
                'end_date': 'May 12, 2018',
                'duration': '10 years'
            },
            {
                'planet': 'Mars',
                'start_date': 'May 12, 2001',
                'end_date': 'May 12, 2008',
                'duration': '7 years'
            }
        ]
    }
    
    return render_template('dashas.html', dasha_data=dasha_data)

@app.route('/transits')
def transits():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Placeholder transit data
    transit_data = {
        'date': datetime.now().strftime('%B %d, %Y'),
        'current_transits': [
            {
                'planet': 'Sun',
                'sign': 'Pisces',
                'degrees': '15°23\'',
                'house': 8,
                'aspect': 'Conjunct natal Mercury'
            },
            {
                'planet': 'Moon',
                'sign': 'Gemini',
                'degrees': '8°45\'',
                'house': 11,
                'aspect': 'Trine natal Venus'
            },
            {
                'planet': 'Mercury',
                'sign': 'Pisces',
                'degrees': '3°12\'',
                'house': 8,
                'aspect': 'Conjunct natal Mercury'
            },
            {
                'planet': 'Venus',
                'sign': 'Aries',
                'degrees': '27°89\'',
                'house': 9,
                'aspect': 'Square natal Mars'
            },
            {
                'planet': 'Mars',
                'sign': 'Taurus',
                'degrees': '19°56\'',
                'house': 10,
                'aspect': 'Trine natal Saturn'
            },
            {
                'planet': 'Jupiter',
                'sign': 'Capricorn',
                'degrees': '5°67\'',
                'house': 6,
                'aspect': 'Sextile natal Jupiter'
            },
            {
                'planet': 'Saturn',
                'sign': 'Aquarius',
                'degrees': '11°34\'',
                'house': 7,
                'aspect': 'Square natal Moon'
            },
            {
                'planet': 'Rahu',
                'sign': 'Taurus',
                'degrees': '22°78\'',
                'house': 10,
                'aspect': 'Opposite natal Ketu'
            },
            {
                'planet': 'Ketu',
                'sign': 'Scorpio',
                'degrees': '22°78\'',
                'house': 4,
                'aspect': 'Opposite natal Rahu'
            }
        ],
        'interpretation': 'With the Sun and Mercury in your 8th house of transformation, this is a time of deep introspection and potential revelations. The Moon in Gemini in your 11th house encourages social connections that may bring unexpected insights. Saturn\'s square to your natal Moon suggests emotional challenges that require patience and discipline. Jupiter\'s favorable aspect to its natal position offers growth opportunities in health and daily routines.'
    }
    
    upcoming_transits = [
        {
            'date': 'March 15, 2025',
            'event': 'Mercury enters Aries',
            'effect': 'Communication becomes more direct and assertive. Good time for initiating new intellectual projects.'
        },
        {
            'date': 'March 20, 2025',
            'event': 'Sun enters Aries (Equinox)',
            'effect': 'Solar energy shifts to your 9th house, highlighting higher education, travel, and philosophical pursuits.'
        },
        {
            'date': 'March 27, 2025',
            'event': 'Venus enters Taurus',
            'effect': 'Relationships stabilize and financial matters improve. Excellent period for investments and sensual pleasures.'
        },
        {
            'date': 'April 2, 2025',
            'event': 'Mars enters Gemini',
            'effect': 'Energy becomes more scattered but versatile. Multiple projects may demand your attention simultaneously.'
        }
    ]
    
    return render_template('transits.html', transit_data=transit_data, upcoming_transits=upcoming_transits)

@app.route('/remedies')
def remedies():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Placeholder remedies data
    remedies_data = {
        'challenging_planets': [
            {
                'planet': 'Saturn',
                'position': 'Afflicting Moon in 4th house',
                'issues': 'Emotional insecurity, domestic challenges, property-related issues',
                'remedies': [
                    'Recite Hanuman Chalisa on Saturdays',
                    'Donate black sesame seeds to the needy',
                    'Wear a Blue Sapphire (Neelam) after proper consultation',
                    'Serve the elderly and practice meditation'
                ]
            },
            {
                'planet': 'Rahu',
                'position': '3rd house, aspecting 9th house',
                'issues': 'Obsessive thinking, communication problems, challenges with father or mentor',
                'remedies': [
                    'Feed crows on Wednesdays',
                    'Recite Durga Chalisa',
                    'Wear a Hessonite (Gomed) gemstone',
                    'Practice mindfulness meditation'
                ]
            }
        ],
        'beneficial_planets': [
            {
                'planet': 'Jupiter',
                'position': '5th house in own sign',
                'benefits': 'Wisdom, fortune, spiritual growth, success in education',
                'enhancement': [
                    'Recite Vishnu Sahasranama on Thursdays',
                    'Donate yellow items or sweets',
                    'Wear a Yellow Sapphire (Pukhraj) gemstone',
                    'Practice yoga and spiritual studies'
                ]
            },
            {
                'planet': 'Venus',
                'position': '7th house, well-placed',
                'benefits': 'Harmonious relationships, aesthetic sense, diplomatic skills',
                'enhancement': [
                    'Recite Venus mantras on Fridays',
                    'Donate white flowers or rice',
                    'Wear a Diamond or White Sapphire',
                    'Practice artistic activities and balanced lifestyle'
                ]
            }
        ],
        'general_remedies': [
            'Regular meditation to balance planetary energies',
            'Yogic breathing exercises (Pranayama)',
            'Maintain a clean and harmonious living environment',
            'Practice gratitude and compassion daily'
        ]
    }
    
    return render_template('remedies.html', remedies_data=remedies_data)

@app.route('/settings')
def settings():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('settings.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)