from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import openai

app = Flask(__name__)

# OpenAI API Key (from the .env file)
openai.api_key = os.getenv("OPENAI_API_KEY")

# Scrape Darmklachten.nl for test data
def scrape_darmklachten():
    url = "https://www.darmklachten.nl/"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    test_data = []
    
    for section in soup.select('.test-item'):
        title = section.select_one('h2').get_text(strip=True)
        description = section.select_one('p').get_text(strip=True)
        test_data.append({'title': title, 'description': description})
    
    return test_data

# Recommendation route
@app.route('/recommend', methods=['POST'])
def recommend_test():
    symptoms = request.json.get('symptoms', '').lower()
    description = request.json.get('description', '').lower()
    
    # Scrape the data for available tests
    scraped_data = scrape_darmklachten()

    # Construct the query for OpenAI
    query = f"Given the symptoms: {symptoms} and the description: {description}, recommend the best test from the following options: {scraped_data}"
    
    # Get OpenAI's recommendation
    openai_response = openai.Completion.create(
        engine="text-davinci-003",  # You can use a more suitable OpenAI model if needed
        prompt=query,
        max_tokens=150
    )
    
    recommendation = openai_response.choices[0].text.strip()
    
    # Simple matching logic for testing based on scraped data
    for test in scraped_data:
        if symptoms in test['description'].lower():
            return jsonify({'recommendation': test['title'], 'reason': test['description']})

    return jsonify({'recommendation': "Geen specifieke test gevonden", 'reason': "Neem contact op voor meer hulp."})

if __name__ == '__main__':
    app.run(debug=True)
