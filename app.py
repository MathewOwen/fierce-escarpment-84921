from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import openai
import os

app = Flask(__name__)

# Set OpenAI API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")  # Change this to use a valid environment variable

# Root route (home page)
@app.route('/')
def home():
    return "Welcome to the Darmklachten App! Use /scrape to get test data or /recommend to get test recommendations based on symptoms."

# Scrape route
@app.route('/scrape', methods=['GET'])
def scrape_darmklachten():
    url = "https://www.darmklachten.nl/"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to retrieve data from the website.'}), 500

    soup = BeautifulSoup(response.content, 'html.parser')

    # Adjust the selectors based on the actual structure of the site
    test_data = []
    for section in soup.select('.test-item'):  # Ensure this selector matches the actual HTML structure
        title = section.select_one('h2').get_text(strip=True)
        description = section.select_one('p').get_text(strip=True)
        test_data.append({'title': title, 'description': description})

    return jsonify({'tests': test_data})

# Recommendation route using OpenAI for smart recommendations based on symptoms and description
@app.route('/recommend', methods=['POST'])
def recommend_test():
    data = request.json
    symptoms = data.get('symptoms', '').lower()
    description = data.get('description', '').lower()

    # Simple check for missing input
    if not symptoms or not description:
        return jsonify({'error': 'Please provide both symptoms and description.'}), 400

    # Load test data (you can either scrape this or use a static list)
    scraped_data = [
        {"title": "Darmparasieten Test", "description": "Voor klachten zoals diarree, opgeblazen gevoel."},
        {"title": "Glutenintolerantie Test", "description": "Voor klachten gerelateerd aan gluten."},
        # Add more tests here...
    ]

    # Build a prompt for OpenAI to help with test recommendation based on symptoms and description
    prompt = f"Based on the symptoms '{symptoms}' and the description '{description}', recommend the best test from the following list: {scraped_data}"

    try:
        response = openai.Completion.create(
            engine="text-davinci-003",  # Ensure this model is appropriate for your needs
            prompt=prompt,
            max_tokens=100,
            temperature=0.7
        )

        # Get the recommendation from the OpenAI API response
        recommendation = response.choices[0].text.strip()

        # If the OpenAI model does not return a recommendation, fall back to scraped data logic
        if not recommendation:
            return jsonify({'recommendation': "Geen specifieke test gevonden", 'reason': "Neem contact op voor meer hulp."})

        return jsonify({'recommendation': recommendation, 'reason': 'Test is recommended based on input.'})

    except Exception as e:
        return jsonify({'error': f"Error during OpenAI processing: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))  # Use the PORT environment variable
    app.run(host='0.0.0.0', port=port)
