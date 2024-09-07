from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def setup_assistant():
    # Načtení promptu
    with open('prompt.txt', 'r', encoding='utf-8') as f:
        prompt = f.read()

    # 1. Nahrání XLSX souboru do OpenAI
    with open("products.csv", "rb") as file_content:
        file = client.files.create(
            file=file_content,
            purpose='assistants'
        )
    print(f"File uploaded with ID: {file.id}")

    # 2. Vytvoření asistenta
    assistant = client.beta.assistants.create(
        name="Product Description Generator",
        instructions=prompt + f"\nPlease use the file with ID {file.id} for analysis.",
        model="gpt-4-1106-preview",
        tools=[{"type": "file_search"}]
    )
    print(f"Assistant created with ID: {assistant.id}")

    # 3. Vytvoření vlákna se zprávou o souboru
    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": f"Please analyze the data in the file with ID {file.id}."
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
