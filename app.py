import os
from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import openai
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

app = Flask(__name__)

openai.api_key = os.getenv("OPENAI_API_KEY")

@app.route('/')
def home():
    return "Welcome to the Smart Test Recommendation API!"

@app.route('/scrape', methods=['GET'])
def scrape_tests():
    url = "https://www.darmklachten.nl/"
    response = requests.get(url)

    if response.status_code != 200:
        return jsonify({'error': 'Failed to retrieve data from the website.'}), 500

    soup = BeautifulSoup(response.content, 'html.parser')
    test_data = []
    for section in soup.select('.test-item'):  # Adjust selector based on site structure
        title = section.select_one('h2').get_text(strip=True)
        description = section.select_one('p').get_text(strip=True)
        test_data.append({'title': title, 'description': description})
    
    return jsonify({'tests': test_data})

def generate_embeddings(texts):
    response = openai.Embedding.create(
        input=texts,
        model="text-embedding-ada-002"
    )
    return [r['embedding'] for r in response['data']]

@app.route('/recommend', methods=['POST'])
def recommend_test():
    data = request.json
    symptoms = data.get('symptoms', '').lower()
    if not symptoms:
        return jsonify({'error': 'Please provide symptoms.'}), 400

    scraped_data = [
        {"title": "Darmparasieten Test", "description": "Voor klachten zoals diarree, opgeblazen gevoel."},
        {"title": "Glutenintolerantie Test", "description": "Voor klachten gerelateerd aan gluten."},
        # Add more tests...
    ]

    try:
        # Combine symptoms and descriptions for embeddings
        texts = [symptoms] + [test['description'] for test in scraped_data]
        embeddings = generate_embeddings(texts)
        
        # Calculate cosine similarity
        symptom_embedding = np.array(embeddings[0]).reshape(1, -1)
        test_embeddings = np.array(embeddings[1:])
        similarities = cosine_similarity(symptom_embedding, test_embeddings).flatten()

        # Find the most relevant test
        best_match_idx = np.argmax(similarities)
        best_test = scraped_data[best_match_idx]
        return jsonify({'recommendation': best_test, 'similarity_score': similarities[best_match_idx]})
    
    except Exception as e:
        return jsonify({'error': f"Error during recommendation: {str(e)}"}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
