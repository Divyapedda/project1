from flask import Flask, request, render_template, url_for
import sqlite3
import os
import cv2
import numpy as np

app = Flask(__name__)

# Ensure the uploads directory exists
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Database setup (for simplicity, using SQLite)
def init_db():
    conn = sqlite3.connect('clothes.db')
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS clothes (
        id INTEGER PRIMARY KEY,
        colour TEXT,
        pattern TEXT,
        size TEXT,
        length TEXT,
        material TEXT,
        image_path TEXT)
    ''')
    # Add some example data
    c.executemany('''
    INSERT INTO clothes (colour, pattern, size, length, material, image_path)
    VALUES (?, ?, ?, ?, ?, ?)
    ''', [
        ('red', 'striped', 'medium', 'short', 'cotton', 'static/images/red_striped_shirt_medium.jpg'),
        ('blue', 'plain', 'large', 'long', 'polyester', 'static/images/blue_plain_shirt_long.jpg'),
        ('black', 'plain', 'medium', 'long', 'cotton', 'static/images/black_plain_shirt.jpg'),
        ('white', 'striped', 'large', 'short', 'polyester', 'static/images/white_striped_shirt.jpg'),
        ('yellow', 'plain', 'medium', 'medium', 'cotton', 'static/images/yellow_plain_shirt.jpg'),
        ('purple', 'checked', 'small', 'short', 'wool', 'static/images/purple_checked_shirt.jpg'),
        ('orange', 'striped', 'large', 'long', 'polyester', 'static/images/orange_striped_shirt.jpg'),
        ('pink', 'plain', 'medium', 'medium', 'cotton', 'static/images/pink_plain_shirt.jpg'),
        ('brown', 'checked', 'small', 'long', 'wool', 'static/images/brown_checked_shirt.jpg'),
        ('grey', 'plain', 'large', 'short', 'polyester', 'static/images/grey_plain_shirt.jpg'),
        ('navy', 'striped', 'medium', 'long', 'cotton', 'static/images/navy_striped_shirt.jpg'),
        ('teal', 'plain', 'small', 'medium', 'polyester', 'static/images/teal_plain_shirt.jpg'),
        ('maroon', 'checked', 'large', 'short', 'wool', 'static/images/maroon_checked_shirt.jpg'),
        ('beige', 'striped', 'medium', 'medium', 'cotton', 'static/images/beige_striped_shirt.jpg')
    ])
    conn.commit()
    conn.close()

# Function to analyze the image and extract key features
def analyze_image(image_path):
    # Dummy function for image analysis (real implementation would use ML)
    image = cv2.imread(image_path)
    features = {
        'colour': 'blue',  # Example output
        'pattern': 'plain',
        'size': 'medium',
        'length': 'long',
        'material': 'cotton'
    }
    return features

# Function to get recommendations based on user preferences and image analysis
def get_recommendations(user_preferences, image_features, num_recommendations):
    conn = sqlite3.connect('clothes.db')
    c = conn.cursor()
    query = 'SELECT * FROM clothes WHERE '
    conditions = []
    params = []
    for key, values in user_preferences.items():
        if values:
            conditions.append(f"{key} IN ({','.join('?' for _ in values)})")
            params.extend(values)
    if conditions:
        query += ' AND '.join(conditions)
    else:
        query = query.replace(' WHERE ', '')
    c.execute(query, params)
    results = c.fetchall()
    conn.close()
    return results[:num_recommendations]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/suggestions', methods=['POST'])
def suggestions():
    user_preferences = {
        'colour': request.form.getlist('colour'),
        'pattern': request.form.getlist('pattern'),
        'size': request.form.getlist('size'),
        'length': request.form.getlist('length'),
        'material': request.form.getlist('material')
    }
    image = request.files['image']
    image_path = os.path.join(UPLOAD_FOLDER, image.filename)
    image.save(image_path)
    image_features = analyze_image(image_path)
    num_recommendations = int(request.form['recommendations'])
    recommendations = get_recommendations(user_preferences, image_features, num_recommendations)
    return render_template('suggestions.html', recommendations=recommendations)

if __name__ == '__main__':
    init_db()
    app.run(debug=True)