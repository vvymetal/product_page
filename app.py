
from flask import Flask, render_template, jsonify, request
import json
import os

app = Flask(__name__, static_folder='static', static_url_path='/static')

# ... zbytek kódu zůstává stejný

def load_product(product_id):
    file_path = os.path.join('data', 'products', f'{product_id}.json')
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    return None

@app.route('/')
def index():
    # Zde bychom normálně načetli seznam produktů z databáze
    products = [
        {"id": "product1", "name": "Fytogel na nohy Slaviton"},
        {"id": "product2", "name": "Hydratační krém"},
    ]
    return render_template('index.html', products=products)

@app.route('/product/<product_id>')
def product(product_id):
    product_data = load_product(product_id)
    return render_template('product.html', product=product_data)

@app.route('/api/product/<product_id>')
def product_api(product_id):
    age_category = request.args.get('age_category', '18-29')
    product_data = load_product(product_id)
    if product_data:
        product_data['selected_age_category'] = age_category
        return jsonify(product_data)
    return jsonify({"error": "Product not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)