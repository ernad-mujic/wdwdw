#from flask import Flask, render_template

 

#app = Flask(__name__)

 

#@app.route('/')

#def index():

    #return render_template('index.html')

 

#@app.route('/qr-generator')

#def qr_generator():

    #return "QR Generator page coming soon!"

 

#@app.route('/ip-lookup')

#def ip_lookup():

    #return "IP Lookup page coming soon!"

 

#@app.route('/email-lookup')

#def email_lookup():

    #return "Email Lookup page coming soon!"

 

#@app.route('/about')

#def about():

    #return "About Me page coming soon!"

 

#if __name__ == '__main__':

    #app.run(debug=True)

#########################################################################################################################################

# updating this file to support QR code generation, ip lookup, email breach lookup using fake data, and about me page.
# Final project exercise five 4/23/25

#########################################################################################################################################

import base64
import io
import os
import qrcode
import requests
import hashlib
import json
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request

# Load environment variables
load_dotenv()

app = Flask(__name__)

# Simulated breach database for educational purposes
# In a real application, you would use the Have I Been Pwned API
SIMULATED_BREACHES = {
    "example@gmail.com": [
        {
            "name": "ExampleSite Breach",
            "date": "2023-05-15",
            "data_classes": ["Email addresses", "Passwords", "Names", "IP addresses"],
            "description": "In May 2023, ExampleSite suffered a data breach that exposed 3 million user records."
        },
        {
            "name": "FakeShop Security Incident",
            "date": "2022-11-03",
            "data_classes": ["Email addresses", "Password hashes", "Payment info"],
            "description": "FakeShop suffered a breach in November 2022 affecting 1.2 million customers."
        }
    ],
    "test@yahoo.com": [
        {
            "name": "MockService Data Leak",
            "date": "2024-01-22",
            "data_classes": ["Email addresses", "Names", "Phone numbers"],
            "description": "MockService experienced a data leak in January 2024 affecting 5 million users."
        }
    ]
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/qr-generator', methods=['GET', 'POST'])
def qr_generator():
    # QR code generator code from Exercise 2
    qr_code = None
    
    if request.method == 'POST':
        # Get form data
        content = request.form.get('content')
        size = int(request.form.get('size', 10))
        
        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=size,
            border=4,
        )
        qr.add_data(content)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to base64 for displaying in HTML
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        qr_code = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    return render_template('qr_generator.html', qr_code=qr_code)

@app.route('/ip-lookup', methods=['GET', 'POST'])
def ip_lookup():
    # IP lookup code from Exercise 3
    result = None
    error = None
    
    if request.method == 'POST':
        ip_address = request.form.get('ip_address')
        
        # AbuseIPDB API settings
        api_key = os.getenv('ABUSEIPDB_API_KEY')
        headers = {
            'Accept': 'application/json',
            'Key': api_key
        }
        params = {
            'ipAddress': ip_address,
            'maxAgeInDays': 90,
            'verbose': True
        }
        
        try:
            response = requests.get(
                'https://api.abuseipdb.com/api/v2/check', 
                headers=headers, 
                params=params
            )
            
            if response.status_code == 200:
                data = response.json()['data']
                
                # Format the last reported date if it exists
                last_reported = None
                if data.get('lastReportedAt'):
                    last_reported_date = datetime.fromisoformat(data['lastReportedAt'].replace('Z', '+00:00'))
                    last_reported = last_reported_date.strftime('%Y-%m-%d %H:%M:%S')
                
                result = {
                    'ip': data['ipAddress'],
                    'is_malicious': data['abuseConfidenceScore'] > 20,  # Consider >20% as potentially malicious
                    'abuse_score': data['abuseConfidenceScore'],
                    'isp': data.get('isp', 'Unknown'),
                    'domain': data.get('domain', 'Unknown'),
                    'country_code': data.get('countryCode', 'Unknown'),
                    'country_name': data.get('countryName', 'Unknown'),
                    'usage_type': data.get('usageType', 'Unknown'),
                    'reports': data.get('totalReports', 0),
                    'last_reported': last_reported
                }
            else:
                error = f"API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            error = f"An error occurred: {str(e)}"
    
    return render_template('ip_lookup.html', result=result, error=error)

@app.route('/email-lookup', methods=['GET', 'POST'])
def email_lookup():
    result = None
    error = None
    
    if request.method == 'POST':
        email = request.form.get('email').lower()
        
        try:
            # Check if email is in our simulated breach database
            if email in SIMULATED_BREACHES:
                result = {
                    'email': email,
                    'breached': True,
                    'breach_count': len(SIMULATED_BREACHES[email]),
                    'breaches': SIMULATED_BREACHES[email]
                }
            else:
                # For educational purposes, add some randomness to show a clean result sometimes
                import random
                if random.random() < 0.7:  # 70% chance of no breach
                    result = {
                        'email': email,
                        'breached': False
                    }
                else:
                    # Pretend we found a breach
                    result = {
                        'email': email,
                        'breached': True,
                        'breach_count': 1,
                        'breaches': [{
                            'name': 'RandomSite Data Breach',
                            'date': '2023-08-10',
                            'data_classes': ['Email addresses', 'Usernames'],
                            'description': 'In August 2023, RandomSite suffered a data breach affecting millions of users.'
                        }]
                    }
            
            # Note: In a real application, you would use code like this:
            """
            # Get API key from environment
            api_key = os.getenv('HIBP_API_KEY')
            
            # Call the Have I Been Pwned API
            headers = {
                'hibp-api-key': api_key,
                'User-Agent': 'SecurityToolkit-Flask-App'
            }
            response = requests.get(
                f'https://haveibeenpwned.com/api/v3/breachedaccount/{email}',
                headers=headers
            )
            
            if response.status_code == 200:
                breaches = response.json()
                result = {
                    'email': email,
                    'breached': True,
                    'breach_count': len(breaches),
                    'breaches': breaches
                }
            elif response.status_code == 404:
                result = {
                    'email': email,
                    'breached': False
                }
            else:
                error = f"API Error: {response.status_code} - {response.text}"
            """
            
        except Exception as e:
            error = f"An error occurred: {str(e)}"
    
    return render_template('email_lookup.html', result=result, error=error)

#@app.route('/about')
#def about():
    #return "About Me page coming soon!"
@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
