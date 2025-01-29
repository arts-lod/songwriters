import json
from difflib import SequenceMatcher

def load_jsonld(file_path):
    """
    It loads a JSON-LD file
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def similarity(a, b):
    """
    It calculates textual similarity in two strings
    """
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

def filter_duplicates(input_jsonld, europeana_json, output_file_new, output_file_duplicates, threshold=0.9):
    """
    It filters JSON-LD records comparing them with data from Europeana.
    Records not found in Europeana are saved in output_file_new,
    while records that duplicate Europeana data are saved in output_file_duplicates.
    """
    # It loads data
    input_data = input_jsonld["@graph"]
    europeana_data = europeana_json["items"]

    non_duplicates = []
    duplicates = []

    for input_record in input_data:
        input_title = input_record.get("dc:title", "")
        input_creators = input_record.get("dc:creator", [])
        
        is_duplicate = False

        for europeana_record in europeana_data:
            europeana_title = europeana_record.get("dcTitle", "")
            europeana_creators = europeana_record.get("dcCreator", [])

            # It compares titles
            title_similarity = similarity(input_title, europeana_title)

            # It compares authors
            creator_similarity = max(
                (similarity(input_creator, europeana_creator)
                 for input_creator in input_creators
                 for europeana_creator in europeana_creators),
                default=0
            )

            # It verifies similarity threshold
            if title_similarity > threshold and creator_similarity > threshold:
                is_duplicate = True
                break

        # It sorts records according to similarity
        if is_duplicate:
            duplicates.append(input_record)
        else:
            non_duplicates.append(input_record)

    # It saves results in two different files
    context = {"@context": input_jsonld["@context"]}

    with open(output_file_new, 'w', encoding='utf-8') as file_new:
        json.dump({"@context": context["@context"], "@graph": non_duplicates}, file_new, ensure_ascii=False, indent=4)

    with open(output_file_duplicates, 'w', encoding='utf-8') as file_duplicates:
        json.dump({"@context": context["@context"], "@graph": duplicates}, file_duplicates, ensure_ascii=False, indent=4)

    print(f"Completed filtering. New records: {output_file_new}, Duplicate records: {output_file_duplicates}")

# Input ed output files
input_jsonld_path = "OUTPUT_IN_EUROPEANA_JSONLD.jsonld"  # JSON-LD generated
europeana_json_path = "EXTRACTED_FROM_EUROPEANA.json"  # JSON from Europeana
output_new_path = "OUTPUT_NON_DUPLICATES.jsonld"
output_duplicates_path = "OUTPUT_DUPLICATES.jsonld"

# It loads input files
input_jsonld = load_jsonld(input_jsonld_path)
europeana_json = load_jsonld(europeana_json_path)

# It filters
filter_duplicates(input_jsonld, europeana_json, output_new_path, output_duplicates_path, threshold=0.9)
