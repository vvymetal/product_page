from flask import render_template, request, redirect, url_for
import json
import os
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__, static_folder='static', static_url_path='/static')

PRODUCTS_DIR = os.path.join('data', 'products')

CORS(app)



def load_product(product_id):
    if os.path.exists(PRODUCTS_DIR):
        for filename in os.listdir(PRODUCTS_DIR):
            if filename.endswith('.json') and product_id in filename:
                file_path = os.path.join(PRODUCTS_DIR, filename)
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        return json.load(file)
                except json.JSONDecodeError as e:
                    print(f"Chyba při čtení JSON souboru {file_path}: {str(e)}")
    return None





@app.route('/')
def index():
    products = []
    if os.path.exists(PRODUCTS_DIR):
        for filename in os.listdir(PRODUCTS_DIR):
            if filename.endswith('.json'):
                try:
                    product_id = filename.split('_')[1].split('.')[0]
                    product_data = load_product(product_id)
                    if product_data:
                        products.append({
                            "id": product_id,
                            "name": product_data['společné_části']['základní_informace']['název_produktu'],
                            "image_url": product_data['společné_části']['galerie_obrázků'][0] if product_data['společné_části']['galerie_obrázků'] else None
                        })
                except (IndexError, KeyError) as e:
                    print(f"Chyba při načítání produktu {filename}: {str(e)}")
    else:
        print(f"Adresář {PRODUCTS_DIR} neexistuje.")
    return render_template('index.html', products=products)

@app.route('/product/<product_id>')
def product(product_id):
    user_agent = request.user_agent.string
    if "Mobile" in user_agent:
        return redirect(url_for('product_mobile', product_id=product_id))
    
    product_data = load_product(product_id)
    if product_data:
        return render_template('product.html', product=product_data)
    return "Produkt nenalezen", 404


@app.route('/product/<product_id>/mobile')
def product_mobile(product_id):
    product_data = load_product(product_id)
    if product_data:
        user_agent = request.user_agent.string
        if "Mobile" in user_agent:
            return render_template('product_mobile.html', product=product_data)
        else:
            return redirect(url_for('product', product_id=product_id))
    return "Produkt nenalezen", 404

@app.route('/api/product/<product_id>')
def product_api(product_id):
    age_category = request.args.get('age_category', '18-29')
    product_data = load_product(product_id)
    if product_data:
        personalized_content = next((item for item in product_data['personalizované_části'] if item['věková_kategorie'] == age_category), None)
        if personalized_content:
            return jsonify({
                'společné_části': product_data['společné_části'],
                'personalizované_části': personalized_content,
                'dodatečné_informace': product_data['dodatečné_informace']
            })
    return jsonify({"error": "Product or age category not found"}), 404

if __name__ == '__main__':
    app.run(debug=True)