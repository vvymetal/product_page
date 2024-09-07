import openai
import json
import time
from dotenv import load_dotenv
import os

# Načtení proměnných prostředí
load_dotenv()

# Nastavení API klíče
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_description(assistant_id, product):
    thread = openai.beta.threads.create()
    
    openai.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=f"Generate a description for this product: {json.dumps(product, ensure_ascii=False)}"
    )
    
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )
    
    while run.status not in ['completed', 'failed']:
        time.sleep(1)
        run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    
    if run.status == 'failed':
        return f"Error: {run.last_error}"
    
    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value

def main():
    # Načtení ID asistenta
    with open('assistant_id.txt', 'r') as f:
        assistant_id = f.read().strip()

    # Načtení produktů
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)

    # Generování popisů
    new_descriptions = []
    for product in products:
        print(f"Generating description for product {product['id']}...")
        new_description = generate_description(assistant_id, product)
        new_descriptions.append({
            "id": product["id"],
            "original_description": product.get("description", ""),
            "new_description": new_description
        })

    # Uložení výsledků
    with open('new_product_descriptions.json', 'w', encoding='utf-8') as f:
        json.dump(new_descriptions, f, ensure_ascii=False, indent=2)

    print("All descriptions generated and saved.")

if __name__ == "__main__":
    main()