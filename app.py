from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import sqlite3
import os
from dotenv import load_dotenv
from admin_handler import register_admin_routes
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='.', static_url_path='')
CORS(app)

# SQLite Configuration
DATABASE = 'portfolio.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

# Initialize database
def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

# Email configuration
def send_email_notification(contact_data):
    try:
        # Replace these with your email settings
        smtp_server = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "mishrautkarsh499@gmail.com"  # Your email
        sender_password = os.getenv("EMAIL_PASSWORD", "")  # Use environment variable for password
        recipient_email = "mishrautkarsh499@gmail.com"  # Where to receive notifications
        
        # Create message
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"New Contact Form Submission from {contact_data['name']}"
        
        # Email body
        body = f"""
        You have received a new message from your portfolio website:
        
        Name: {contact_data['name']}
        Email: {contact_data['email']}
        Subject: {contact_data.get('subject', 'No subject')}
        
        Message:
        {contact_data['message']}
        
        This message was sent automatically from your portfolio contact form.
        """
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Connect to server and send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        print(f"Email notification sent for contact from {contact_data['name']}")
        return True
    except Exception as e:
        print(f"Failed to send email notification: {str(e)}")
        return False

# API Routes
@app.route('/api/contact', methods=['POST'])
def contact():
    try:
        data = request.json
        name = data.get('name')
        email = data.get('email')
        message = data.get('message')
        subject = data.get('subject', '')
        
        if not all([name, email, message]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO contacts (name, email, message) VALUES (?, ?, ?)',
            (name, email, message)
        )
        
        conn.commit()
        conn.close()
        
        # Send email notification
        contact_data = {
            'name': name,
            'email': email,
            'subject': subject,
            'message': message
        }
        send_email_notification(contact_data)
        
        return jsonify({'message': 'Contact form submitted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# New route to view contacts in browser
@app.route('/admin/contacts', methods=['GET'])
def view_contacts():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM contacts ORDER BY created_at DESC')
        contacts = cursor.fetchall()
        
        conn.close()
        
        # Convert rows to dictionaries
        contacts_list = []
        for contact in contacts:
            contacts_list.append({
                'id': contact['id'],
                'name': contact['name'],
                'email': contact['email'],
                'message': contact['message'],
                'created_at': contact['created_at']
            })
        
        return render_template('contacts.html', contacts=contacts_list)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/download-resume', methods=['GET'])
def download_resume():
    try:
        # Try multiple possible locations for the resume file
        possible_paths = [
            os.path.join(os.path.dirname(__file__), 'assets', 'resume.pdf'),
            os.path.join(os.path.dirname(__file__), 'resume.pdf'),
        ]
        
        resume_path = None
        for path in possible_paths:
            if os.path.exists(path):
                resume_path = path
                break
        
        if not resume_path:
            print(f"Resume file not found. Checked paths: {possible_paths}")
            return jsonify({'error': 'Resume file not found'}), 404
        
        print(f"Serving resume from: {resume_path}")
        return send_file(resume_path, as_attachment=True)
    except Exception as e:
        error_msg = str(e)
        print(f"Error serving resume: {error_msg}")
        return jsonify({'error': error_msg}), 500

# Serve the main HTML file
@app.route('/')
def serve_index():
    return app.send_static_file('index.html')

# Register admin routes
register_admin_routes(app)

if __name__ == '__main__':
    init_db()
    # Create assets directory if it doesn't exist
    assets_dir = os.path.join(os.path.dirname(__file__), 'assets')
    os.makedirs(assets_dir, exist_ok=True)
    
    # Create templates directory if it doesn't exist
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    os.makedirs(templates_dir, exist_ok=True)
    
    print(f"Server starting with assets directory at: {assets_dir}")
    app.run(host='0.0.0.0', port=8000, debug=True) 