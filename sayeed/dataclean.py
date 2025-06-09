import json
import re

def clean_medical_data(file_path):
    # Read the JSON file
    with open(file_path, 'r') as file:
        data = json.load(file)
    
    # Initial count
    initial_count = len(data)
    print(f"Initial number of records: {initial_count}")

    # Function to validate a string (not just numbers, codes, or special characters)
    def is_valid_string(s):
        if s is None:
            return False
        if isinstance(s, str):
            # Check if string contains at least one letter and isn't just a code
            if not bool(re.search('[a-zA-Z]', s)):
                return False
            # Remove entries with format like C0036429 or just numbers
            if re.match('^[A-Z][0-9]+$', s) or s.isdigit():
                return False
            # Remove entries that are just URLs
            if s.startswith('http://'):
                return False
            return True
        return False

    # Clean data
    cleaned_data = [
        entry for entry in data
        if all([
            # Check for null values in important fields
            entry['disease_id'] is not None and entry['disease_id'].strip() != '',
            entry['disease_label'] is not None and entry['disease_label'].strip() != '',
            entry['predicate_id'] is not None and entry['predicate_id'].strip() != '',
            # Validate labels
            is_valid_string(entry['disease_label']),
            entry['predicate_label'] is not None,
            # Object label should be valid if present
            (entry['object_label'] is None or is_valid_string(entry['object_label']))
        ])
    ]

    # Final count
    final_count = len(cleaned_data)
    print(f"Number of records after cleaning: {final_count}")
    print(f"Removed {initial_count - final_count} records")

    # Save cleaned data
    output_file = 'cleaned_medical_diseases.json'
    with open(output_file, 'w') as file:
        json.dump(cleaned_data, file, indent=2)
    print(f"Cleaned data saved to {output_file}")

if __name__ == "__main__":
    clean_medical_data('medical_diseases.json')