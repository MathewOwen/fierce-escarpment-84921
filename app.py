from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

# Root route (home page)
@app.route('/')
def home():
    return "Welcome to the Darmklachten App! Use /scrape to get test data or /recommend to get test recommendations based on symptoms."

# Scrape route
@app.route('/scrape', methods=['GET'])
def scrape_darmklachten():
    url = "https://www.darmklachten.nl/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Adjust the selectors based on the actual structure of the site
    test_data = []
    for section in soup.select('.test-item'):  # Example selector
        title = section.select_one('h2').get_text(strip=True)
        description = section.select_one('p').get_text(strip=True)
        test_data.append({'title': title, 'description': description})

    return jsonify({'tests': test_data})

# Recommendation route
@app.route('/recommend', methods=['POST'])
def recommend_test():
    symptoms = request.json.get('symptoms', '').lower()
    description = request.json.get('description', '').lower()

    # Load test data (ideally, cache this from a scrape)
    scraped_data = [
        {"title": "Darmparasieten Test", "description": "Voor klachten zoals diarree, opgeblazen gevoel."},
        {"title": "Glutenintolerantie Test", "description": "Voor klachten gerelateerd aan gluten."},
        # Add more tests here...
    ]

    # Simple matching logic
    for test in scraped_data:
        if any(symptom in test['description'].lower() for symptom in symptoms.split(',')):
            return jsonify({'recommendation': test['title'], 'reason': test['description']})

    return jsonify({'recommendation': "Geen specifieke test gevonden", 'reason': "Neem contact op voor meer hulp."})

if __name__ == '__main__':
    app.run(debug=True)
