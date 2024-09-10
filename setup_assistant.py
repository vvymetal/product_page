from openai import OpenAI
from dotenv import load_dotenv
import os
import json

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def setup_assistant():
    # Načtení promptu
    with open('prompt.txt', 'r', encoding='utf-8') as f:
        prompt = f.read()

    # Načtení definice funkce
    with open('function_definition.json', 'r', encoding='utf-8') as f:
        function_definition = json.load(f)

    # 1. Nahrání HTML souboru s produkty do OpenAI
    with open("Worksheet.html", "rb") as file_content:
        file = client.files.create(
            file=file_content,
            purpose='assistants'
        )
    print(f"HTML File uploaded with ID: {file.id}")

    # 2. Vytvoření asistenta s povoleným code_interpreterem a funkcí
    assistant = client.beta.assistants.create(
        name="Product Description Generator",
        instructions=prompt + f"""
        Please use the file with ID {file.id} for product data and the provided function to generate personalized descriptions. 
        Utilize your extensive knowledge of TianDe products to enhance the descriptions.
        Ensure consistency of key product information across all age groups while personalizing the presentation for each group.
        Generate content in parts: base information, personalized content for each age group, and additional information.
        Use the following structure for the output:
        {{
          "společné_části": {{
            "základní_informace": {{...}},
            "galerie_obrázků": [...],
            "video_url": "...",
            "eco_friendly_badge": true/false
          }},
          "personalizované_části": [
            {{
              "věková_kategorie": "12-17",
              "meta_popisek": "...",
              "krátký_popis": "...",
              "detailní_popis": "...",
              "marketingový_obsah": {{...}},
              "tiande_lifestyle_text": "...",
              "recenze_zákazníků": [...],
              "doporučené_produkty": [...],
              "často_kupováno_společně": [...],
              "často_kladené_otázky": [...],
              "rady_expertů": "...",
              "personalizované_obrázky": [...]
            }},
            // Další věkové kategorie...
          ],
          "dodatečné_informace": {{
            "tiande_komunita": {{...}},
            "vzdělávací_sekce": {{...}},
            "newsletter_signup": {{...}}
          }}
        }}
        """,
        model="gpt-4-1106-preview",
        tools=[
            {"type": "code_interpreter"},
            {"type": "function", "function": function_definition}
        ]
    )
    print(f"Assistant created with ID: {assistant.id}")

    # 3. Vytvoření vlákna se zprávou pro zpracování dat
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": f"""
                Analyze the product data in the file with ID {file.id} and be ready to generate personalized descriptions using the provided function.
                Use your knowledge of TianDe products to provide accurate and detailed information.
                Remember to maintain consistency in key product information across all age groups while tailoring the content for each group.
                Generate the content in three main parts: base information, personalized content for each age group, and additional information.
                """
            }
        ]
    )
    print(f"Thread created with ID: {thread.id}")

    return assistant.id

if __name__ == "__main__":
    try:
        assistant_id = setup_assistant()
        with open('assistant_id.txt', 'w') as f:
            f.write(assistant_id)
        print("Setup completed successfully.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")