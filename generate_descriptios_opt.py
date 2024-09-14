import json
import os
import csv
from dotenv import load_dotenv
import anthropic
import openai
from openai import OpenAI
import re
import codecs
import argparse

load_dotenv()

# Kontrola API klíčů
if "ANTHROPIC_API_KEY" not in os.environ:
    print("API klíč pro Anthropic není nastaven. Přidejte ANTHROPIC_API_KEY do souboru .env")
    exit(1)

if "OPENAI_API_KEY" not in os.environ:
    print("API klíč pro OpenAI není nastaven. Přidejte OPENAI_API_KEY do souboru .env")
    exit(1)

anthropic_client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

class AIModel:
    def __init__(self, model_type):
        self.model_type = model_type
        if model_type == "chatgpt":
            self.openai_client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    def generate_completion(self, prompt, max_tokens):
        if self.model_type == "claude":
            response = anthropic_client.completions.create(
                model="claude-2.1",
                prompt=prompt,
                max_tokens_to_sample=max_tokens,
                temperature=0.5
            )
            return response.completion
        elif self.model_type == "chatgpt":
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=0.5
            )
            return response.choices[0].message.content
        else:
            raise ValueError("Nepodporovaný typ modelu")

def parse_csv_with_html(file_path):
    with codecs.open(file_path, 'r', encoding='utf-8-sig') as file:
        content = file.read()
    
    html_pattern = re.compile(r'<.*?>', re.DOTALL)
    html_contents = html_pattern.findall(content)
    for i, html in enumerate(html_contents):
        content = content.replace(html, f'___HTML_PLACEHOLDER_{i}___', 1)
    
    rows = content.split('\n')
    reader = csv.DictReader(rows)
    
    product_data = {}
    for row in reader:
        product_id = next((row[col] for col in row if 'kód' in col.lower() or 'code' in col.lower() or 'id' in col.lower()), None)
        if not product_id:
            continue
        
        for key, value in row.items():
            for i, html in enumerate(html_contents):
                if f'___HTML_PLACEHOLDER_{i}___' in value:
                    row[key] = value.replace(f'___HTML_PLACEHOLDER_{i}___', html)
        
        product_data[product_id] = row
    
    return product_data

def load_additional_data(product_id):
    filename = f"additional_data_{product_id}.txt"
    if os.path.exists(filename):
        print("načtena doplňková data")
        with open(filename, 'r', encoding='utf-8') as file:
            return file.read()
    return None

def clean_value(value):
    if isinstance(value, str):
        return value.strip()
    elif isinstance(value, list):
        return [item.strip() if isinstance(item, str) else item for item in value]
    return value

def load_product_data(csv_file):
    product_data = {}
    with codecs.open(csv_file, 'r', encoding='utf-8-sig') as file:
        dialect = csv.Sniffer().sniff(file.read(1024))
        file.seek(0)
        
        reader = csv.DictReader(file, dialect=dialect)
        
        id_column = next((col for col in reader.fieldnames if 'kód' in col.lower() or 'code' in col.lower() or 'id' in col.lower()), None)
        
        if not id_column:
            print("Nepodařilo se najít sloupec s kódem produktu. Použijeme první sloupec jako ID.")
            id_column = reader.fieldnames[0]
        
        print(f"Používáme sloupec '{id_column}' jako ID produktu.")
        
        for row in reader:
            product_id = row[id_column]
            cleaned_row = {k: clean_value(v) for k, v in row.items() if v}
            product_data[product_id] = cleaned_row
    
    print("Načtená data z CSV:")
    print(json.dumps(product_data, ensure_ascii=False, indent=2))
    
    return product_data

def load_prompt():
    with open('prompt.txt', 'r', encoding='utf-8') as f:
        return f.read()

def parse_json_response(response_text):
    try:
        return json.loads(response_text)
    except json.JSONDecodeError:
        try:
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                json_str = json_match.group()
                print("Vyhledaný JSON:")
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

def validate_json(data):
    try:
        json.dumps(data)
        return True
    except (TypeError, ValueError):
        return False

def generate_common_parts(product_info, base_prompt, ai_model):
    print("Vstupní data pro generate_common_parts:")
    print(json.dumps(product_info, ensure_ascii=False, indent=2))
    
    prompt = f"""
    \n\nHuman: Na základě následujících informací o produktu vygenerujte společné části popisu. Ujistěte se, že výstup je validní JSON a neobsahuje žádný další text:
    
    {json.dumps(product_info, ensure_ascii=False, indent=2)}
    
    
    
    Generujte pouze část "společné_části" v následujícím JSON formátu:
    {{
      "základní_informace": {{
        "název_produktu": "",
        "kód_produktu": "",
        "meta_popisek": "",
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
      "galerie_obrázků": [
        {{
          "url": "",
          "alt": ""
        }}
      ],
      "video_url": "",
      "eco_friendly_badge": false
    }}
    
    Použijte pouze informace poskytnuté ve vstupních datech. Pokud některé informace chybí, nechte příslušné pole prázdné nebo nastavte na výchozí hodnotu.

    Použijte tento základní prompt:
    {base_prompt}

    \n\nAssistant:"""
    
    response = ai_model.generate_completion(prompt, 3000)
    
    print("Odpověď pro společné části:")
    print(response)
    return parse_json_response(response)

def generate_personalized_part(product_info, base_prompt, age_category, ai_model):
    prompt = f"""
    \n\nHuman: Na základě následujících informací o produktu vygenerujte personalizovanou část popisu pro věkovou kategorii {age_category}:
    
    {json.dumps(product_info, ensure_ascii=False, indent=2)}
    
      Použijte tento základní prompt:
    {base_prompt}
    
    Generujte pouze část pro danou věkovou kategorii v následujícím JSON formátu. Ujistěte se, že výstup je validní JSON a neobsahuje žádný další text. Dbejte na to, aby informace byly konzistentní s ostatními věkovými kategoriemi, ale zároveň specifické pro tuto věkovou skupinu:
    {{
      "věková_kategorie": "{age_category}",
       "meta_popisek": ""
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
    
    response = ai_model.generate_completion(prompt, 3000)
    print(f"Odpověď pro věkovou kategorii {age_category}:")
    print(response)
    return parse_json_response(response)

def combine_parts(common_parts, personalized_parts, additional_info, další_informace):
    return {
        "společné_části": common_parts,
        "personalizované_části": personalized_parts,
        "dodatečné_informace": additional_info,
        "další_informace": json.dumps(další_informace) if další_informace else None
    }

def generate_description(product_id, product_info, base_prompt, ai_model):
    try:
        common_parts = generate_common_parts(product_info, base_prompt, ai_model)
        if not common_parts or not validate_json(common_parts):
            raise Exception("Nepodařilo se vygenerovat platné společné části")
        
        print("Společné části úspěšně vygenerovány")
        
        personalized_parts = []
        for age_category in ["12-17", "18-29", "30-45", "46-60", "61+"]:
            part = generate_personalized_part(product_info, base_prompt, age_category, ai_model)
            if not part or not validate_json(part):
                raise Exception(f"Nepodařilo se vygenerovat platnou personalizovanou část pro kategorii {age_category}")
            personalized_parts.append(part)
            print(f"Personalizovaná část pro kategorii {age_category} úspěšně vygenerována")
        
        additional_info = """{{
      "tiande_komunita": {{
        "social_media_links": [],
        "user_generated_content": []
      }},
      "vzdělávací_sekce": {{
        "název_kurzu": "Univerzita Království tianDe",
        "popis_kurzu": "vše, co potřebujete vědět o životním stylu a produktech tianDe najdete v naší univerzitě",
        "url": "https://univerzita.kralovstvi-tiande.cz/"
      }},
      "newsletter_signup": {{
        "nadpis": "",
        "popis": ""
      }}
    }}"""
        if not additional_info or not validate_json(additional_info):
            raise Exception("Nepodařilo se vygenerovat platné dodatečné informace")
        
        print("Všechny části úspěšně vygenerovány, začínám spojování")
        
        další_informace = product_info.get('additional_data', '')
        
        final_description = combine_parts(common_parts, personalized_parts, additional_info, další_informace)
        
        print("Části úspěšně spojeny")
        
        return final_description
    except Exception as e:
        print(f"Chyba při generování popisu pro produkt {product_id}: {str(e)}")
        return None

def safe_filename(product_id):
    return product_id.replace('/', '_').replace('\\', '_')

def main():
    parser = argparse.ArgumentParser(description="Generátor popisů produktů")
    parser.add_argument("--model", choices=["claude", "chatgpt"], default="claude", help="Vyberte AI model (claude nebo chatgpt)")
    args = parser.parse_args()

    ai_model = AIModel(args.model)

    csv_file = 'products.csv'
    
    if not os.path.exists(csv_file):
        print(f"Soubor {csv_file} nebyl nalezen. Ujistěte se, že je ve stejné složce jako tento skript.")
        exit(1)
    
    product_data = parse_csv_with_html(csv_file)

    if not product_data:
        print("Nepodařilo se načíst žádná data z CSV souboru.")
        exit(1)
    
    print("Načtená data z CSV:")
    print(json.dumps(product_data, ensure_ascii=False, indent=2))
    
    base_prompt = load_prompt()

    #product_ids = ["41105", "44402-1","63601/01","63601/05","63601/10","60145/05","60145/10","60145/01","30101","61902","61911","61914","61915","61921","30117","30118"]
    product_ids = ["41105", "44402-1","63601/01"]

    os.makedirs('data/products', exist_ok=True)

    for product_id in product_ids:
        if product_id in product_data:
            product_info = product_data[product_id]
            print(f"Produkt info z csv: {json.dumps(product_info, ensure_ascii=False, indent=2)}")

            additional_data = load_additional_data(product_id)
            if additional_data:
                product_info['additional_data'] = additional_data

            description = generate_description(product_id, product_info, base_prompt, ai_model)
            if description:
                safe_id = safe_filename(product_id)
                file_path = os.path.join('data', 'products', f'product_{safe_id}.json')
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(description, f, ensure_ascii=False, indent=2)
                print(f"Popis pro produkt {product_id} byl vygenerován a uložen do {file_path}.")
            else:
                print(f"Nepodařilo se vygenerovat popis pro produkt {product_id}.")
        else:
            print(f"Produkt s ID {product_id} nebyl nalezen v CSV souboru.")

if __name__ == "__main__":
    main()