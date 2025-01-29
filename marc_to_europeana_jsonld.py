import json
import re

def parse_unimarc_text(file_path):
    """
    It reads a UNIMARC file in text format and produces a list of JSONLD records
    """
    records = []
    current_record = {}
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if not line:
                if current_record:
                    records.append(current_record)
                    current_record = {}
            else:
                match = re.match(r"^(\d{3})\s+(.+)$", line)
                if match:
                    tag, content = match.groups()
                    current_record.setdefault(tag, []).append(content)
        if current_record:
            records.append(current_record)
    return records

def parse_subfields(content):
    """
    It analyzes the subfields of a UNIMARC field and it gives them back as a dictionary
    """
    subfields = {}
    for subfield in content.split('$')[1:]:
        code = subfield[0]
        value = subfield[1:].strip()
        subfields[code] = value
    return subfields

def convert_to_europeana_jsonld(records, output_file):
    """
    It converts a single UNIMARC record to an Europeana compatible JSON-LD one
    """
    context = {
        "@context": {
            "edm": "http://www.europeana.eu/schemas/edm/",
            "dc": "http://purl.org/dc/elements/1.1/",
            "dcterms": "http://purl.org/dc/terms/",
            "ore": "http://www.openarchives.org/ore/terms/"
        }
    }

    items = []
    for record in records:
        identifier = record.get('001', ['unknown'])[0].strip()
        cho_uri = f"http://example.org/edm/cho/{identifier}"
        aggregation_uri = f"http://example.org/edm/aggregation/{identifier}"
        resource_uri = f"http://example.org/edm/resource/{identifier}"

        item = {
            "@id": cho_uri,
            "@type": "edm:ProvidedCHO",
            "dc:title": "",
            "dc:creator": [],
            "dc:date": "",
            "dc:subject": [],
            "dc:description": [],
            "edm:isShownAt": resource_uri,
            "edm:preview": f"http://example.org/preview/{identifier}",
            "ore:Aggregation": {
                "@id": aggregation_uri,
                "edm:aggregatedCHO": cho_uri,
                "edm:isShownAt": resource_uri,
                "edm:preview": f"http://example.org/preview/{identifier}"
            }
        }

        for tag, contents in record.items():
            for content in contents:
                subfields = parse_subfields(content)

                if tag == '200':  # Title and subtitle
                    item["dc:title"] = subfields.get('a', 'Unknown Title')
                    subtitle = subfields.get('e', None)
                    if subtitle:
                        item["dc:description"].append(f"Sottotitolo: {subtitle}")
                
                elif tag == '700':  # Author (single)
                    author = subfields.get('a', 'Unknown Author')
                    item["dc:creator"].append(author)
                
                elif tag == '710':  # Collective entity (author)
                    corporate_author = subfields.get('a', 'Unknown Corporate Author')
                    item["dc:creator"].append(corporate_author)
                
                elif tag == '210':  # Date and place of pubblication
                    item["dc:date"] = subfields.get('d', 'Unknown Date')
                
                elif tag == '215':  # Physical description
                    extent = subfields.get('a', None)
                    if extent:
                        item["dc:description"].append(f"Descrizione fisica: {extent}")
                
                elif tag == '606':  # Subject
                    subject = subfields.get('a', None)
                    if subject:
                        item["dc:subject"].append(subject)

        items.append(item)

    # Save data in JSON-LD format
    output = {"@graph": items}
    output.update(context)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

# Input and output files
input_file = "INPUT_UNIMARC.txt"
output_file = "OUTPUT_IN_EUROPEANA_JSONLD.jsonld"

# It analyzes and converts
records = parse_unimarc_text(input_file)
convert_to_europeana_jsonld(records, output_file)

print(f"An Europeana compatible JSON-LD file has been saved in: {output_file}")
