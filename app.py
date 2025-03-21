from flask import Flask, request, jsonify, render_template
import openai
import os

app = Flask(__name__)

# Set your OpenAI API key (store it in an environment variable for security)
client = openai.OpenAI(api_key = os.getenv("OPENAI_API_KEY")) # Set this variable in your environment

def generate_description_openai(product_name, keywords, tone="neutral"):
    messages = [
        {
            "role": "system",
            "content": f"Generate a product description in {tone} tone with the following details:"
        },
        {
            "role": "user",
            "content": f"Name: {product_name}, Keywords: {', '.join(keywords)}"
        }
    ]

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # You can use "gpt-3.5-turbo" if preferred
            messages=messages,
            max_tokens=150
        )

        return response.choices[0].message.content.strip()

    except openai.OpenAIError as e:
        app.logger.error(f"OpenAI API error: {e}")
        return f"Error: {e}"

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/generate-description', methods=['POST'])
def generate_description_endpoint():
    try:
        product_name = request.json.get('product_name', '').strip()
        keywords_data = request.json.get('keywords', '')

        if not product_name:
            return jsonify({'error': 'Product name is required'}), 400

        if isinstance(keywords_data, str):
            keywords = [kw.strip() for kw in keywords_data.split(',') if kw.strip()]
        elif isinstance(keywords_data, list):
            keywords = [kw.strip() for kw in keywords_data if kw.strip()]
        else:
            return jsonify({'error': 'Keywords must be a string or a list'}), 400

        tone = request.json.get('tone', 'neutral')

        description = generate_description_openai(product_name, keywords, tone)
        
        return jsonify({'description': description})

    except Exception as e:
        app.logger.error(f"Error generating description: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
