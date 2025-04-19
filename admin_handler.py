from flask import Flask, request, jsonify, redirect, url_for
import sqlite3
import json
import os
from pathlib import Path
from werkzeug.utils import secure_filename

# Database setup
def get_db_connection():
    conn = sqlite3.connect('portfolio.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create tables if they don't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personal_info (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            title TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT,
            location TEXT,
            intro_short TEXT NOT NULL,
            about_long TEXT NOT NULL,
            profile_image TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            level INTEGER NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experience (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            job_title TEXT NOT NULL,
            company TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,
            description TEXT NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS education (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            degree TEXT NOT NULL,
            institution TEXT NOT NULL,
            start_date TEXT NOT NULL,
            end_date TEXT,
            description TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS social_media (
            id INTEGER PRIMARY KEY,
            github TEXT,
            linkedin TEXT,
            twitter TEXT,
            instagram TEXT
        )
    ''')
    
    conn.commit()
    conn.close()

def save_personal_info(data):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if record exists
    cursor.execute("SELECT id FROM personal_info WHERE id = 1")
    if cursor.fetchone() is None:
        # Insert new record
        cursor.execute('''
            INSERT INTO personal_info (id, name, title, email, phone, location, intro_short, about_long, profile_image)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (1, data['name'], data['title'], data['email'], data['phone'], data['location'], 
              data['introShort'], data['aboutLong'], data['profileImage']))
    else:
        # Update existing record
        cursor.execute('''
            UPDATE personal_info 
            SET name = ?, title = ?, email = ?, phone = ?, location = ?, 
                intro_short = ?, about_long = ?, profile_image = ?
            WHERE id = 1
        ''', (data['name'], data['title'], data['email'], data['phone'], data['location'], 
              data['introShort'], data['aboutLong'], data['profileImage']))
    
    conn.commit()
    conn.close()

def save_skills(skills):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clear existing skills
    cursor.execute("DELETE FROM skills")
    
    # Insert new skills
    for i in range(len(skills['skillName'])):
        cursor.execute('''
            INSERT INTO skills (name, level)
            VALUES (?, ?)
        ''', (skills['skillName'][i], skills['skillLevel'][i]))
    
    conn.commit()
    conn.close()

def save_experience(experience):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clear existing experience
    cursor.execute("DELETE FROM experience")
    
    # Insert new experience
    for i in range(len(experience['jobTitle'])):
        cursor.execute('''
            INSERT INTO experience (job_title, company, start_date, end_date, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (experience['jobTitle'][i], experience['company'][i], 
              experience['jobStart'][i], experience['jobEnd'][i], 
              experience['jobDescription'][i]))
    
    conn.commit()
    conn.close()

def save_education(education):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Clear existing education
    cursor.execute("DELETE FROM education")
    
    # Insert new education
    for i in range(len(education['degree'])):
        cursor.execute('''
            INSERT INTO education (degree, institution, start_date, end_date, description)
            VALUES (?, ?, ?, ?, ?)
        ''', (education['degree'][i], education['institution'][i], 
              education['educationStart'][i], education['educationEnd'][i], 
              education['educationDescription'][i]))
    
    conn.commit()
    conn.close()

def save_social_media(social):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Check if record exists
    cursor.execute("SELECT id FROM social_media WHERE id = 1")
    if cursor.fetchone() is None:
        # Insert new record
        cursor.execute('''
            INSERT INTO social_media (id, github, linkedin, twitter, instagram)
            VALUES (?, ?, ?, ?, ?)
        ''', (1, social['github'], social['linkedin'], social['twitter'], social['instagram']))
    else:
        # Update existing record
        cursor.execute('''
            UPDATE social_media 
            SET github = ?, linkedin = ?, twitter = ?, instagram = ?
            WHERE id = 1
        ''', (social['github'], social['linkedin'], social['twitter'], social['instagram']))
    
    conn.commit()
    conn.close()

def get_portfolio_data():
    """Retrieve all portfolio data from the database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get personal info
    cursor.execute("SELECT * FROM personal_info WHERE id = 1")
    personal_info = cursor.fetchone()
    
    # Get skills
    cursor.execute("SELECT * FROM skills")
    skills = cursor.fetchall()
    
    # Get experience
    cursor.execute("SELECT * FROM experience ORDER BY start_date DESC")
    experience = cursor.fetchall()
    
    # Get education
    cursor.execute("SELECT * FROM education ORDER BY start_date DESC")
    education = cursor.fetchall()
    
    # Get social media
    cursor.execute("SELECT * FROM social_media WHERE id = 1")
    social_media = cursor.fetchone()
    
    conn.close()
    
    return {
        'personal_info': dict(personal_info) if personal_info else {},
        'skills': [dict(skill) for skill in skills],
        'experience': [dict(exp) for exp in experience],
        'education': [dict(edu) for edu in education],
        'social_media': dict(social_media) if social_media else {}
    }

def update_html_template():
    """Update the index.html with the latest data from the database"""
    data = get_portfolio_data()
    
    # Load the index.html template
    template_path = Path('index_template.html')
    
    # If template doesn't exist, create a backup of the current index.html as template
    if not template_path.exists():
        original_index = Path('index.html')
        if original_index.exists():
            with open(original_index, 'r', encoding='utf-8') as file:
                template_content = file.read()
            with open(template_path, 'w', encoding='utf-8') as file:
                file.write(template_content)
        else:
            return False
    
    # Read the template
    with open(template_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    
    # Replace placeholders with actual data
    if data['personal_info']:
        person = data['personal_info']
        html_content = html_content.replace('{{NAME}}', person.get('name', 'Your Name'))
        html_content = html_content.replace('{{TITLE}}', person.get('title', 'Web Developer'))
        html_content = html_content.replace('{{EMAIL}}', person.get('email', 'contact@example.com'))
        html_content = html_content.replace('{{PHONE}}', person.get('phone', ''))
        html_content = html_content.replace('{{LOCATION}}', person.get('location', ''))
        html_content = html_content.replace('{{SHORT_INTRO}}', person.get('intro_short', ''))
        html_content = html_content.replace('{{ABOUT_TEXT}}', person.get('about_long', ''))
    
    # Update skills section
    if 'skills-container' in html_content and data['skills']:
        skills_html = ''
        for skill in data['skills']:
            skills_html += f'''
            <div class="skill">
                <span>
                    {skill['name']}
                    <span class="skill-percent">{skill['level']}%</span>
                </span>
                <div class="bar">
                    <div class="progress" data-width="{skill['level']}%" style="width: 0%"></div>
                </div>
            </div>
            '''
        
        # Replace the placeholder with the generated HTML
        html_content = html_content.replace('<!-- {{SKILLS}} -->', skills_html)
    
    # Update experience section
    if 'experience-content' in html_content and data['experience']:
        exp_html = ''
        for exp in data['experience']:
            exp_html += f'''
            <div class="experience-item">
                <span class="date">{exp['start_date']} - {exp['end_date'] or 'Present'}</span>
                <h4>{exp['job_title']}</h4>
                <h5>{exp['company']}</h5>
                <p>{exp['description']}</p>
            </div>
            '''
        
        # Replace the placeholder with the generated HTML
        html_content = html_content.replace('<!-- {{EXPERIENCE}} -->', exp_html)
    
    # Update education section
    if 'education-content' in html_content and data['education']:
        edu_html = ''
        for edu in data['education']:
            edu_html += f'''
            <div class="education-item">
                <span class="date">{edu['start_date']} - {edu['end_date'] or 'Present'}</span>
                <h4>{edu['degree']}</h4>
                <h5>{edu['institution']}</h5>
                <p>{edu['description'] or ''}</p>
            </div>
            '''
        
        # Replace the placeholder with the generated HTML
        html_content = html_content.replace('<!-- {{EDUCATION}} -->', edu_html)
    
    # Update social media links
    if data['social_media']:
        social = data['social_media']
        if social.get('github'):
            html_content = html_content.replace('{{GITHUB_URL}}', social['github'])
        if social.get('linkedin'):
            html_content = html_content.replace('{{LINKEDIN_URL}}', social['linkedin'])
        if social.get('twitter'):
            html_content = html_content.replace('{{TWITTER_URL}}', social['twitter'])
        if social.get('instagram'):
            html_content = html_content.replace('{{INSTAGRAM_URL}}', social['instagram'])
    
    # Write the updated content to index.html
    with open('index.html', 'w', encoding='utf-8') as file:
        file.write(html_content)
    
    return True

# Add this to app.py to handle the form submission
def register_admin_routes(app):
    init_db()
    
    @app.route('/admin', methods=['GET'])
    def admin_page():
        return app.send_static_file('admin.html')
    
    @app.route('/api/portfolio-data', methods=['GET'])
    def get_data():
        try:
            return jsonify(get_portfolio_data())
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    @app.route('/api/save-portfolio', methods=['POST'])
    def save_portfolio():
        try:
            data = request.form
            
            # Extract and save personal info
            personal_info = {
                'name': data.get('name'),
                'title': data.get('title'),
                'email': data.get('email'),
                'phone': data.get('phone'),
                'location': data.get('location'),
                'introShort': data.get('introShort'),
                'aboutLong': data.get('aboutLong'),
                'profileImage': data.get('profileImage')
            }
            save_personal_info(personal_info)
            
            # Extract and process skill data
            skill_data = {
                'skillName': request.form.getlist('skillName[]'),
                'skillLevel': [int(level) for level in request.form.getlist('skillLevel[]')]
            }
            save_skills(skill_data)
            
            # Extract and process experience data
            experience_data = {
                'jobTitle': request.form.getlist('jobTitle[]'),
                'company': request.form.getlist('company[]'),
                'jobStart': request.form.getlist('jobStart[]'),
                'jobEnd': request.form.getlist('jobEnd[]'),
                'jobDescription': request.form.getlist('jobDescription[]')
            }
            save_experience(experience_data)
            
            # Extract and process education data
            education_data = {
                'degree': request.form.getlist('degree[]'),
                'institution': request.form.getlist('institution[]'),
                'educationStart': request.form.getlist('educationStart[]'),
                'educationEnd': request.form.getlist('educationEnd[]'),
                'educationDescription': request.form.getlist('educationDescription[]')
            }
            save_education(education_data)
            
            # Extract and save social media links
            social_media = {
                'github': data.get('github'),
                'linkedin': data.get('linkedin'),
                'twitter': data.get('twitter'),
                'instagram': data.get('instagram')
            }
            save_social_media(social_media)
            
            # Update the template with new data
            update_html_template()
            
            return jsonify({'success': True}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

# To use this in app.py, add:
# from admin_handler import register_admin_routes
# register_admin_routes(app) 