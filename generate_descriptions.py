import openai
import json
from dotenv import load_dotenv
import os
import time

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def generate_descriptions(assistant_id, product_ids):
    # Vytvoření vlákna
    thread = client.beta.threads.create()
    
    for product_id in product_ids:
        # Vytvoření zprávy s instrukcemi pro asistenta
        message_content = f"""
        Please generate a personalized product description for product ID {product_id}.
        Include descriptions for all age groups: 12-17, 18-29, 30-45, 46-60, and 61+.
        Use the following structure for the output:
        {{
          "společné_části": {{
            "základní_informace": {{
              "název_produktu": "",
              "meta_popis": "",
              "složení_a_účinky": [
                {{ "složka": "", "účinek": "" }}
              ],
              "návod_k_použití": "",
              "technické_informace": {{
                "velikost_balení": "",
                "kód_produktu": "",
                "země_původu": "",
                "trvanlivost": ""
              }}
            }},
            "detailní_popis": ""
          }},
          "personalizované_části": {{
            "12-17": {{
              "meta_popisek": "",
              "krátký_popis": "",
              "detailní_popis": "",
              "marketingový_obsah": {{
                "rychlý_přehled": [],
                "řeší_tyto_potíže": [],
                "klíčové_benefity": [],
                "proč_zvolit_tento_produkt": []
              }},
              "doplňující_informace": {{
                "často_kladené_otázky": [
                  {{ "otázka": "", "odpověď": "" }}
                ],
                "rady_expertů": "",
                "personalizační_prvek": ""
              }},
              "recenze_zákazníků": [
                {{ "jméno": "", "hodnocení": 0, "text": "" }}
              ],
              "doporučené_produkty": []
            }},
            "18-29": {{...}},
            "30-45": {{...}},
            "46-60": {{...}},
            "61+": {{...}}
          }}
        }}
        """

        # Odeslání zprávy do vlákna
        client.beta.threads.messages.create(
            thread_id=thread.id,
            role="user",
            content=message_content
        )
    
    # Spuštění asistenta
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )
    
    # Čekání na dokončení běhu asistenta
    while run.status not in ['completed', 'failed']:
        time.sleep(5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    
    if run.status == 'failed':
        return f"Error: {run.last_error}"
    
    # Získání odpovědí asistenta
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return [msg.content[0].text.value for msg in messages.data if msg.role == "assistant"]

def main():
    # Načtení assistant_id
    with open('assistant_id.txt', 'r') as f:
        assistant_id = f.read().strip()

    # Seznam produktů, ke kterým chceme popis
    product_ids = ["10127"]  # Nahraďte skutečnými ID produktů

    print("Generating descriptions...")
    descriptions = generate_descriptions(assistant_id, product_ids)

    # Uložení vygenerovaných popisů do JSON souboru
    with open('new_product_descriptions.json', 'w', encoding='utf-8') as f:
        json.dump(descriptions, f, ensure_ascii=False, indent=2)

    print("All descriptions generated and saved.")

if __name__ == "__main__":
    main()
