import csv
import json
import sys
from collections import defaultdict
import itertools
import argparse


class DataLoader:
    """Handles reading and validating CSV files."""
    def __init__(self, sentence_file, people_file, common_words_file):
        self.sentences = self.read_csv(sentence_file, "sentence")
        self.people = self.read_people_csv(people_file)
        self.common_words = self.read_csv(common_words_file, "word", single_column=True)

    def read_csv(self, file_path, expected_header, single_column=False):
        """Reads a CSV file and validates its format."""
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                reader = csv.reader(file)
                header = next(reader, None)
                if not header or (not single_column and header[0] != expected_header):
                    raise ValueError("invalid input")
                return [row[0] for row in reader] if single_column else [row for row in reader]
        except Exception:
            print(json.dumps("invalid input"))
            sys.exit(1)

    def read_people_csv(self, file_path):
        """Reads people file and maps names to their variations."""
        people = {}
        header, rows = self.read_csv(file_path, "Name"), []
        for row in rows:
            if len(row) < 2:
                continue
            name, other_names = row[0], row[1].split(",") if row[1] else []
            people[name] = {name.lower()} | {n.strip().lower() for n in other_names}
        return people


class TextProcessor:
    """Handles text preprocessing such as common word removal."""
    def __init__(self, common_words):
        self.common_words = set(word.lower() for word in common_words)

    def preprocess(self, sentence):
        """Removes common words from a sentence."""
        return " ".join([word for word in sentence.split() if word.lower() not in self.common_words])


class WordCounter:
    """Counts sequences of words."""
    def __init__(self, sentences):
        self.sentences = sentences

    def count_word_sequences(self, n=2):
        """Counts occurrences of word sequences of length n."""
        sequence_counts = defaultdict(int)
        for sentence in self.sentences:
            words = sentence.split()
            for i in range(len(words) - n + 1):
                sequence = " ".join(words[i:i + n])
                sequence_counts[sequence] += 1
        return dict(sorted(sequence_counts.items()))


class PersonAnalyzer:
    """Analyzes person mentions and relationships."""
    def __init__(self, people):
        self.people = people

    def count_mentions(self, sentences):
        """Counts how often each person is mentioned."""
        mention_counts = defaultdict(int)
        for sentence in sentences:
            for name, aliases in self.people.items():
                if any(alias in sentence.lower() for alias in aliases):
                    mention_counts[name] += 1
        return dict(sorted(mention_counts.items()))

    def find_direct_connections(self, sentences):
        """Finds direct connections between people in the same sentence."""
        connections = defaultdict(set)
        for sentence in sentences:
            mentioned_people = {name for name, aliases in self.people.items() if any(alias in sentence.lower() for alias in aliases)}
            for p1, p2 in itertools.combinations(mentioned_people, 2):
                connections[p1].add(p2)
                connections[p2].add(p1)
        return {k: sorted(v) for k, v in connections.items()}


class GraphAnalyzer:
    """Handles indirect connections using graph traversal."""
    def __init__(self, connections):
        self.graph = connections

    def find_indirect_connections(self, person, target, max_depth=3):
        """Finds indirect paths between people up to a fixed depth."""
        if person not in self.graph or target not in self.graph:
            return []

        paths = []
        queue = [(person, [person])]

        while queue:
            current, path = queue.pop(0)
            if len(path) > max_depth:
                break
            for neighbor in self.graph.get(current, []):
                if neighbor == target:
                    paths.append(path + [neighbor])
                elif neighbor not in path:
                    queue.append((neighbor, path + [neighbor]))

        return paths


class TaskManager:
    """Handles task execution based on user input."""
    def __init__(self, data_loader):
        self.text_processor = TextProcessor(data_loader.common_words)
        self.word_counter = WordCounter([self.text_processor.preprocess(s[0]) for s in data_loader.sentences])
        self.person_analyzer = PersonAnalyzer(data_loader.people)
        self.graph_analyzer = None

    def execute(self, task_number):
        if task_number == 1:
            result = sorted([self.text_processor.preprocess(s[0]) for s in data_loader.sentences])
        elif task_number == 2:
            result = self.word_counter.count_word_sequences()
        elif task_number == 3:
            result = self.person_analyzer.count_mentions([s[0] for s in data_loader.sentences])
        elif task_number == 6:
            result = self.person_analyzer.find_direct_connections([s[0] for s in data_loader.sentences])
            self.graph_analyzer = GraphAnalyzer(result)
        elif task_number == 7:
            if not self.graph_analyzer:
                print(json.dumps("invalid input"))
                sys.exit(1)
            result = self.graph_analyzer.find_indirect_connections("Harry Potter", "Hermione Granger")
        else:
            result = "invalid input"
        
        print(json.dumps(result, indent=2))


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Process text and analyze people.")
    parser.add_argument("sentence_file", type=str)
    parser.add_argument("people_file", type=str)
    parser.add_argument("common_words_file", type=str)
    parser.add_argument("task_number", type=int)

    args = parser.parse_args()

    data_loader = DataLoader(args.sentence_file, args.people_file, args.common_words_file)
    task_manager = TaskManager(data_loader)
    task_manager.execute(args.task_number)
