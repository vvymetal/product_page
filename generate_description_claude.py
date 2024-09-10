import json
import os
import csv
from dotenv import load_dotenv
import anthropic
import re

load_dotenv()

if "ANTHROPIC_API_KEY" not in os.environ:
    print("API klíč pro Anthropic není nastaven. Přidejte ANTHROPIC_API_KEY do souboru .env")
    exit(1)

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

# Funkce load_product_data a load_prompt zůstávají beze změny


def load_product_data(csv_file):
    product_data = {}
    with open(csv_file, 'r', encoding='utf-8') as file:
        # Nejprve zjistíme, jaký oddělovač je použit
        dialect = csv.Sniffer().sniff(file.read(1024))
        file.seek(0)
        
        reader = csv.DictReader(file, dialect=dialect)
        
        # Vypíšeme názvy sloupců pro debugging
        #print("Názvy sloupců v CSV souboru:")
        #print(reader.fieldnames)
        
        # Pokusíme se najít sloupec, který by mohl obsahovat kód produktu
        id_column = next((col for col in reader.fieldnames if 'kód' in col.lower() or 'code' in col.lower() or 'id' in col.lower()), None)
        
        if not id_column:
            print("Nepodařilo se najít sloupec s kódem produktu. Použijeme první sloupec jako ID.")
            id_column = reader.fieldnames[0]
        
        print(f"Používáme sloupec '{id_column}' jako ID produktu.")
        
        for row in reader:
            product_id = row[id_column]
            product_data[product_id] = row
    
    return product_data

def load_prompt():
    with open('prompt.txt', 'r', encoding='utf-8') as f:
        return f.read()


def parse_json_response(response_text):
    """Pokusí se najít a parsovat JSON odpověď v textu."""
    try:
        # Hledáme text mezi prvními složenými závorkami
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        if json_match:
            json_str = json_match.group()

            print("vyhledaný json:")
            print(json_str)

            return json.loads(json_str)
        else:
            print("Nepodařilo se najít JSON v odpovědi.")
            print(f"Celá odpověď: {response_text}")
            return None
    except json.JSONDecodeError as e:
        print(f"Chyba při parsování JSON: {str(e)}")
        print(f"Problematická část: {json_str if 'json_str' in locals() else 'N/A'}")
        return None



def generate_common_parts(product_info, base_prompt):
    prompt = f"""
    \n\nHuman:Na základě následujících informací o produktu vygenerujte společné části popisu.Ujistěte se, že výstup je validní JSON a neobsahuje žádný další text:
    
    {json.dumps(product_info, ensure_ascii=False, indent=2)}
    
    Použijte tento základní prompt:
    {base_prompt}
    
    Generujte pouze část "společné_části" v následujícím JSON formátu:
    {{
      "základní_informace": {{
        "název_produktu": "",
        "kód_produktu": "",
        "cena": {{
          "s_dph": 0,
          "bez_dph": 0
        }},
        "dostupnost": "",
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
          "hmotnost": "",
          "produktová_řada": ""
        }}
      }},
      "galerie_obrázků": [],
      "video_url": "",
      "eco_friendly_badge": false
    }}
    \n\nAssistant:"""
    
    response = client.completions.create(
        model="claude-2.1",
        prompt=prompt,
        max_tokens_to_sample=4000,
        temperature=0.5
    )
    
    print("Odpověď pro společné části:")
    print(response.completion)
    return parse_json_response(response.completion)

def generate_personalized_part(product_info, base_prompt, age_category):
    prompt = f"""
    \n\nHuman:Na základě následujících informací o produktu vygenerujte personalizovanou část popisu pro věkovou kategorii {age_category}:
    
    {json.dumps(product_info, ensure_ascii=False, indent=2)}
    
    Použijte tento základní prompt:
    {base_prompt}
    
    Generujte pouze část pro danou věkovou kategorii v následujícím JSON formátu.Ujistěte se, že výstup je validní JSON a neobsahuje žádný další text:
    {{
      "věková_kategorie": "{age_category}",
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
        {{ "jméno": "", "věk": 0, "hodnocení": 0, "text": "" }}
      ],
      "doporučené_produkty": [],
      "často_kupováno_společně": [],
      "často_kladené_otázky": [
        {{ "otázka": "", "odpověď": "" }}
      ],
      "rady_expertů": "",
      "personalizované_obrázky": []
    }}
    \n\nAssistant:"""
    
    response = client.completions.create(
        model="claude-2.1",
        prompt=prompt,
        max_tokens_to_sample=4000,
        temperature=0.5
    )
    print("Odpověď pro společné části:")
    print(response.completion)

    return parse_json_response(response.completion)

def generate_additional_info(product_info, base_prompt):
    prompt = f"""
    \n\nHuman:Na základě následujících informací o produktu vygenerujte dodatečné informace:
    
    {json.dumps(product_info, ensure_ascii=False, indent=2)}
    
    Použijte tento základní prompt:
    {base_prompt}
    
    Generujte pouze část "dodatečné_informace" v následujícím JSON formátu. Ujistěte se, že výstup je validní JSON a neobsahuje žádný další text:
    {{
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
    \n\nAssistant:"""
    
    response = client.completions.create(
        model="claude-2.1",
        prompt=prompt,
        max_tokens_to_sample=500,
        temperature=0.5
    )
    print("Odpověď pro společné části:")
    print(response.completion)
    return parse_json_response(response.completion)

def combine_parts(common_parts, personalized_parts, additional_info):
    return {
        "společné_části": common_parts["společné_části"],
        "personalizované_části": personalized_parts,
        "dodatečné_informace": additional_info["dodatečné_informace"]
    }

def generate_description(product_id, product_info, base_prompt):
    try:
        common_parts = generate_common_parts(product_info, base_prompt)
        if not common_parts:
            raise Exception("Nepodařilo se vygenerovat společné části")
        
        personalized_parts = []
        for age_category in ["12-17", "18-29", "30-45", "46-60", "61+"]:
            part = generate_personalized_part(product_info, base_prompt, age_category)
            if not part:
                raise Exception(f"Nepodařilo se vygenerovat personalizovanou část pro kategorii {age_category}")
            personalized_parts.append(part)
        
        additional_info = ""
        #generate_additional_info(product_info, base_prompt)
        #if not additional_info:
        #    raise Exception("Nepodařilo se vygenerovat dodatečné informace")
        
        # Spojení všech částí do finálního JSON objektu
        print("před spojením částí")
        print(common_parts)
        print(personalized_parts)
        
        final_description = combine_parts(common_parts, personalized_parts, additional_info)
        
        return final_description
    except Exception as e:
        print(f"Chyba při generování popisu pro produkt {product_id}: {str(e)}")
        return None

def main():
    csv_file = 'products.csv'
    
    if not os.path.exists(csv_file):
        print(f"Soubor {csv_file} nebyl nalezen. Ujistěte se, že je ve stejné složce jako tento skript.")
        exit(1)
    
    product_data = load_product_data(csv_file)
    
    if not product_data:
        print("Nepodařilo se načíst žádná data z CSV souboru.")
        exit(1)
    
    base_prompt = load_prompt()

    # Vypíšeme několik prvních klíčů ze slovníku product_data pro kontrolu
    #print("První produkty v datovém souboru:")
    #for i, (key, value) in enumerate(list(product_data.items())[:5]):
    #    print(f"{key}: {value.get('Název', 'N/A')}")
    #    if i >= 4:
    #        break

    product_ids = ["30221"]  # Nahraďte skutečnými ID produktů

    for product_id in product_ids:
        if product_id in product_data:
            product_info = product_data[product_id]
            description = generate_description(product_id, product_info, base_prompt)
            if description:
                with open(f'product_description_{product_id}.json', 'w', encoding='utf-8') as f:
                    json.dump(description, f, ensure_ascii=False, indent=2)
                print(f"Popis pro produkt {product_id} byl vygenerován a uložen.")
            else:
                print(f"Nepodařilo se vygenerovat popis pro produkt {product_id}.")
        else:
            print(f"Produkt s ID {product_id} nebyl nalezen v CSV souboru.")

if __name__ == "__main__":
    main()