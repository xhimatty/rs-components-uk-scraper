import json
from rs import fetch_data

cookies = {} # already handled and saved in .env. Cannot be exposed

with open('.env', 'a', encoding='utf-8') as f:
    f.write(f"\nRS_COOKIES='{json.dumps(cookies)}'\n")

data = fetch_data() # handled before applying async
rs_json = json.dumps(data, indent=4)

with open('rs.json', 'w', encoding='utf-8') as f:
    f.write(rs_json)