import requests
import json

def upload_to_europeana(jsonld_file, api_key):
    """
    It loads JSON-LD records to Europeana via API.
    """
    # API Endpoint
    endpoint = "https://api.europeana.eu/v3/record/upload.json"

    # It loads JSON-LD file
    with open(jsonld_file, 'r', encoding='utf-8') as file:
        data = json.load(file)

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    # It sends each record separately to the endpoint
    for record in data["@graph"]:
        payload = {
            "apikey": api_key,
            "record": record
        }

        response = requests.post(endpoint, headers=headers, json=payload)

        # It verifies responses
        if response.status_code == 200:
            print(f"Record {record['@id']} loaded.")
        else:
            print(f"Error in loading record {record['@id']}: {response.text}")

# Input file and API key
jsonld_file = "OUTPUT_NON_DUPLICATES.jsonld"
api_key = "YOUR_EUROPEANA_API_KEY"

# It loads records
upload_to_europeana(jsonld_file, api_key)
