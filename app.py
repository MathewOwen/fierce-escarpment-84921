from dotenv import load_dotenv
load_dotenv()  # This loads the environment variables from the .env file
from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
import openai

# Initialize Flask app
app = Flask(__name__)

# OpenAI API Key for ChatGPT
openai.api_key = 'your-openai-api-key'

# Scrape route to get test data
@app.route('/scrape', methods=['GET'])
def scrape_tests():
    # Your WooCommerce site URL or API endpoint to fetch test data
    url = "https://your-woocommerce-site.com/products"
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # Scraping logic (adapt based on your actual product structure)
    test_data = []
    for product in soup.find_all('div', class_='product-item'):
        title = product.select_one('.product-title').text.strip()
        description = product.select_one('.product-description').text.strip()
        test_data.append({'title': title, 'description': description})

    return jsonify({'tests': test_data})

# Recommendation route
@app.route('/recommend', methods=['POST'])
def recommend_test():
    user_input = request.json.get('symptoms', '').lower()
    
    # Step 1: Use ChatGPT to process symptoms
    chatgpt_response = openai.Completion.create(
        model="gpt-4",
        prompt=f"Given the symptoms: {user_input}, recommend the best tests from the following list of tests and their descriptions:\n\n{scraped_data}",
        temperature=0.5,
        max_tokens=100
    )
    
    # Step 2: Process ChatGPT response to extract the recommendation
    chatgpt_recommendation = chatgpt_response.choices[0].text.strip()

    return jsonify({
        'recommendation': chatgpt_recommendation
    })

if __name__ == '__main__':
    app.run(debug=True)
