import pandas as pd
import json

# Načtení dat z XLSX souboru
df = pd.read_excel('products.xlsx')

# Konverze na JSON
json_data = df.to_json(orient='records', indent=4)

# Uložení do JSON souboru
with open('products.json', 'w') as json_file:
    json_file.write(json_data)

print("XLSX soubor byl úspěšně převeden na JSON.")