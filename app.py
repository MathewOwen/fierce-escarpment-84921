from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import openai
import os

app = Flask(__name__)

# Set OpenAI API key from environment variable
openai.api_key = os.getenv('OPENAI_API_KEY')

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
    for section in soup.select('.test-item'):  # Example selector, replace as needed
        title = section.select_one('h2').get_text(strip=True)
        description = section.select_one('p').get_text(strip=True)
        test_data.append({'title': title, 'description': description})

    return jsonify({'tests': test_data})

# Recommendation route using OpenAI for smart recommendations based on symptoms and description
@app.route('/recommend', methods=['POST'])
def recommend_test():
    # Get symptoms and description from the request body
    symptoms = request.json.get('symptoms', '').lower()
    description = request.json.get('description', '').lower()

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
        # OpenAI API call to analyze the symptoms and description
        response = openai.Completion.create(
            engine="text-davinci-003",  # You can use a different model based on your requirements
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
    app.run(debug=True)
