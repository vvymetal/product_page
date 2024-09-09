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
    with open("Worksheet.html", "rb") as file_content:  # Změna zpět na Worksheet.html
        file = client.files.create(
            file=file_content,
            purpose='assistants'
        )
    print(f"HTML File uploaded with ID: {file.id}")

    # 2. Vytvoření asistenta s povoleným code_interpreterem a funkcí
    assistant = client.beta.assistants.create(
        name="Product Description Generator",
        instructions=prompt + f"\nPlease use the file with ID {file.id} for product data and the provided function to generate personalized descriptions. Utilize your extensive knowledge of TianDe products to enhance the descriptions.",
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
                "content": f"Analyze the product data in the file with ID {file.id} and be ready to generate personalized descriptions using the provided function. Use your knowledge of TianDe products to provide accurate and detailed information."
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