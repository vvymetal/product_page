import openai
import json
import time
from dotenv import load_dotenv
import os

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def generate_descriptions(assistant_id, product_ids):
    thread = openai.beta.threads.create()
    
    for product_id in product_ids:
        message_content = f"Použijte funkci generate_product_description pro produkt s ID {product_id}"
        openai.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message_content
        )
    
    run = openai.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )
    
    while run.status not in ['completed', 'failed']:
        time.sleep(5)
        run = openai.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    
    if run.status == 'failed':
        return f"Error: {run.last_error}"
    
    messages = openai.beta.threads.messages.list(thread_id=thread.id)
    return messages.data[0].content[0].text.value

def main():
    with open('assistant_id.txt', 'r') as f:
        assistant_id = f.read().strip()

    product_ids = ["1", "2", "3"]  # Nahraďte skutečnými ID produktů

    print("Generating descriptions...")
    descriptions_json = generate_descriptions(assistant_id, product_ids)

    with open('new_product_descriptions.json', 'w', encoding='utf-8') as f:
        f.write(descriptions_json)

    print("All descriptions generated and saved.")

if __name__ == "__main__":
    main()