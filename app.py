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
    
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses
    except requests.exceptions.RequestException as e:
        return jsonify({"error": "Failed to fetch data from the website.", "details": str(e)}), 500
    
    soup = BeautifulSoup(response.content, 'html.parser')
    test_data = []

    # Adjust the selectors based on the actual structure of the site
    for section in soup.select('.test-item'):  # Example selector
        title = section.select_one('h2').get_text(strip=True)
        description = section.select_one('p').get_text(strip=True)
        test_data.append({'title': title, 'description': description})

    return jsonify({'tests': test_data})

# Recommendation route
@app.route('/recommend', methods=['POST'])
def recommend_test():
    data = request.get_json()  # Use get_json to safely get the request data
    symptoms = data.get('symptoms', '').lower()  # Default to empty string if not provided
    description = data.get('description', '').lower()

    if not symptoms:
        return jsonify({'error': "No symptoms provided."}), 400  # Return a bad request error if symptoms are missing

    # Load test data (ideally, cache this from a scrape or database)
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
    app.run(debug=False)  # Disable debug mode in production
