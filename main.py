import argparse
import csv
import json
import sys
from collections import defaultdict

def read_csv(file_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            header = next(reader, None)
            return header, [row for row in reader if row]
    except Exception:
        print(json.dumps("invalid input"))
        sys.exit(1)

def preprocess_text(sentence, common_words):
    words = sentence.split()
    return " ".join([word for word in words if word.lower() not in common_words])

def main():
    parser = argparse.ArgumentParser(description="Process sentences and analyze people.")
    parser.add_argument("sentence_file", type=str, help="Path to the sentence CSV file")
    parser.add_argument("people_file", type=str, help="Path to the people CSV file")
    parser.add_argument("common_words_file", type=str, help="Path to common words CSV file")
    parser.add_argument("task_number", type=int, help="The task number to execute")
    args = parser.parse_args()

    # Read input files
    sentence_header, sentence_data = read_csv(args.sentence_file)
    people_header, people_data = read_csv(args.people_file)
    common_words_header, common_words_data = read_csv(args.common_words_file)

    if not (sentence_header and people_header and common_words_header):
        print(json.dumps("invalid input"))
        sys.exit(1)

    if sentence_header[0] != "sentence" or people_header[:2] != ["Name", "Other Names"]:
        print(json.dumps("invalid input"))
        sys.exit(1)

    common_words = set(row[0].lower() for row in common_words_data)
    people = {}
    for row in people_data:
        if len(row) < 2:
            continue
        name, other_names = row[0], row[1].split(",") if row[1] else []
        people[name] = {name.lower()} | {n.strip().lower() for n in other_names}

    # Task-based logic
    if args.task_number == 1:
        result = sorted([preprocess_text(row[0], common_words) for row in sentence_data])
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps("invalid input"))
        sys.exit(1)

if __name__ == "__main__":
    main()
