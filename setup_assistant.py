import openai
import json
from dotenv import load_dotenv
import os

# Načtení proměnných prostředí
load_dotenv()

# Nastavení API klíče
openai.api_key = os.getenv("OPENAI_API_KEY")

def setup_assistant():
    # Načtení produktů
    with open('products.json', 'r', encoding='utf-8') as f:
        products = json.load(f)

    # Nahrání dat do znalostní báze asistenta
    file = openai.files.create(
        file=json.dumps(products, ensure_ascii=False).encode('utf-8'),
        purpose='assistants'
    )

    # Vytvoření asistenta
    assistant = openai.beta.assistants.create(
        name="Product Description Generator",
        instructions="""
        You are a product description generator for an e-commerce site. Your task is to create compelling, 
        accurate, and SEO-friendly descriptions for products based on the provided data. Each description should:
        1. Highlight key features and benefits
        2. Use engaging language to appeal to potential customers
        3. Be concise yet informative (aim for 50-100 words)
        4. Include relevant keywords for SEO
        5. Be tailored to the product category and target audience
        Avoid exaggeration and stick to factual information provided in the product data.
        """,
        model="gpt-4-1106-preview",
        tools=[{"type": "retrieval"}],
        file_ids=[file.id]
    )

    print(f"Assistant created with ID: {assistant.id}")
    return assistant.id

if __name__ == "__main__":
    assistant_id = setup_assistant()
    # Uložte ID asistenta do souboru pro pozdější použití
    with open('assistant_id.txt', 'w') as f:
        f.write(assistant_id)