import re
import csv

def extract_name_email(text):
    name_pattern = r"Vaše jméno:\s*(.*?)\s*Vaše e-mailová adresa:"
    email_pattern = r"Vaše e-mailová adresa:\s*([\w\.-]+@[\w\.-]+)"
    
    names = re.findall(name_pattern, text)
    emails = re.findall(email_pattern, text)
    
    return list(zip(emails, names))

def write_to_csv(data, filename='output.csv'):
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['email', 'jméno'])
        writer.writerows(data)

# Načtení textu ze souboru (předpokládáme, že text je uložen v souboru 'input.txt')
with open('input.txt', 'r', encoding='utf-8') as file:
    text = file.read()

# Extrakce dat
extracted_data = extract_name_email(text)

# Zápis do CSV
write_to_csv(extracted_data)

print(f"Data byla úspěšně extrahována a zapsána do souboru 'output.csv'.")