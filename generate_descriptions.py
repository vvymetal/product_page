import openai
import json
from dotenv import load_dotenv
import os
import time
import asyncio

load_dotenv()
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

async def generate_base_info(assistant_id, thread, product_id):
    message_content = f"""
    Generate base information for product ID {product_id}.
    Include the following:
    - Basic product information
    - Common parts that will be consistent across all age groups
    Use the following structure for the output:
    {{
      "společné_části": {{
        "základní_informace": {{
          "název_produktu": "",
          "kód_produktu": "",
          "cena": {{
            "s_dph": 0,
            "bez_dph": 0
          }},
          "dostupnost": "",
          "bodové_ohodnocení": 0,
          "hodnocení": {{
            "průměr": 0,
            "počet_hodnocení": 0
          }},
          "složení_a_účinky": [
            {{ "složka": "", "účinek": "" }}
          ],
          "návod_k_použití": "",
          "technické_informace": {{
            "objem": "",
            "kód_produktu": "",
            "země_původu": "",
            "trvanlivost": ""
          }}
        }},
        "galerie_obrázků": [],
        "video_url": "",
        "eco_friendly_badge": false
      }}
    }}
    """
    
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message_content
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )
    
    while run.status not in ['completed', 'failed']:
        time.sleep(5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    
    if run.status == 'failed':
        return f"Error: {run.last_error}"
    
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return json.loads(messages.data[0].content[0].text.value)

async def generate_personalized_content(assistant_id, thread, product_id, age_group, base_info):
    message_content = f"""
    Generate personalized content for product ID {product_id} and age group {age_group}.
    Use the following base information: {json.dumps(base_info)}
    Use the following structure for the output:
    {{
      "věková_kategorie": "{age_group}",
      "meta_popisek": "",
      "krátký_popis": "",
      "detailní_popis": "",
      "marketingový_obsah": {{
        "rychlý_přehled": [],
        "řeší_tyto_potíže": [],
        "klíčové_benefity": [],
        "proč_zvolit_tento_produkt": []
      }},
      "tiande_lifestyle_text": "",
      "recenze_zákazníků": [
        {{
          "jméno": "",
          "věk": 0,
          "hodnocení": 0,
          "text": ""
        }}
      ],
      "doporučené_produkty": [],
      "často_kupováno_společně": [],
      "často_kladené_otázky": [
        {{
          "otázka": "",
          "odpověď": ""
        }}
      ],
      "rady_expertů": "",
      "personalizované_obrázky": []
    }}
    """
    
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message_content
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )
    
    while run.status not in ['completed', 'failed']:
        time.sleep(5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    
    if run.status == 'failed':
        return f"Error: {run.last_error}"
    
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return json.loads(messages.data[0].content[0].text.value)

async def generate_additional_info(assistant_id, thread, product_id):
    message_content = f"""
    Generate additional information for product ID {product_id}.
    Use the following structure for the output:
    {{
      "dodatečné_informace": {{
        "tiande_komunita": {{
          "social_media_links": [],
          "user_generated_content": []
        }},
        "vzdělávací_sekce": {{
          "název_kurzu": "",
          "popis_kurzu": "",
          "url": ""
        }},
        "newsletter_signup": {{
          "nadpis": "",
          "popis": ""
        }}
      }}
    }}
    """
    
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message_content
    )
    
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id
    )
    
    while run.status not in ['completed', 'failed']:
        time.sleep(5)
        run = client.beta.threads.runs.retrieve(thread_id=thread.id, run_id=run.id)
    
    if run.status == 'failed':
        return f"Error: {run.last_error}"
    
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    return json.loads(messages.data[0].content[0].text.value)

async def generate_descriptions(assistant_id, product_ids):
    for product_id in product_ids:
        thread = client.beta.threads.create()
        
        base_info = await generate_base_info(assistant_id, thread, product_id)
        
        personalized_content = []
        for age_group in ["12-17", "18-29", "30-45", "46-60", "61+"]:
            content = await generate_personalized_content(assistant_id, thread, product_id, age_group, base_info)
            personalized_content.append(content)
        
        additional_info = await generate_additional_info(assistant_id, thread, product_id)
        
        complete_description = {
            "společné_části": base_info["společné_části"],
            "personalizované_části": personalized_content,
            "dodatečné_informace": additional_info["dodatečné_informace"]
        }
        
        # Uložení vygenerovaného popisu do JSON souboru
        with open(f'product_description_{product_id}.json', 'w', encoding='utf-8') as f:
            json.dump(complete_description, f, ensure_ascii=False, indent=2)
        
        print(f"Description for product {product_id} generated and saved.")

async def main():
    # Načtení assistant_id
    with open('assistant_id.txt', 'r') as f:
        assistant_id = f.read().strip()

    # Seznam produktů, ke kterým chceme popis
    product_ids = ["44402-1"]  # Nahraďte skutečnými ID produktů

    print("Generating descriptions...")
    await generate_descriptions(assistant_id, product_ids)

    print("All descriptions generated and saved.")

if __name__ == "__main__":
    asyncio.run(main())