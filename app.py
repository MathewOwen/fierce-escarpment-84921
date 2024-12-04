import os
from flask import Flask, jsonify, request
import openai
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)

# OpenAI API key from environment
openai.api_key = os.getenv("OPENAI_API_KEY")

# Example test data (replace this with dynamic data from your website if needed)
TEST_DATA = [
    {"title": "Darmparasieten Test", "description": "Voor klachten zoals diarree, opgeblazen gevoel."},
    {"title": "Glutenintolerantie Test", "description": "Voor klachten gerelateerd aan gluten."},
    {"title": "Lactose-intolerantie Test", "description": "Voor klachten zoals buikpijn na melkproducten."},
    {"title": "IBS Test", "description": "Voor klachten zoals krampen, obstipatie, en diarree."},
]

def generate_embeddings(texts):
    """Generate embeddings using OpenAI's text-embedding-ada-002 model."""
    response = openai.Embedding.create(input=texts, model="text-embedding-ada-002")
    return [item['embedding'] for item in response['data']]

@app.route('/recommend', methods=['POST'])
def recommend_test():
    """Recommend a test based on user symptoms."""
    data = request.json
    symptoms = data.get('symptoms', '')

    if not symptoms:
        return jsonify({'error': 'Symptoms are required for recommendation'}), 400

    try:
        # Generate embeddings for symptoms and test descriptions
        texts = [symptoms] + [test['description'] for test in TEST_DATA]
        embeddings = generate_embeddings(texts)
        
        symptom_embedding = np.array(embeddings[0]).reshape(1, -1)
        test_embeddings = np.array(embeddings[1:])
        
        # Compute cosine similarities
        similarities = cosine_similarity(symptom_embedding, test_embeddings).flatten()
        best_match_idx = np.argmax(similarities)
        best_test = TEST_DATA[best_match_idx]

        return jsonify({
            'recommendation': best_test,
            'similarity_score': float(similarities[best_match_idx]),
        })

    except Exception as e:
        return jsonify({'error': f"An error occurred: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
