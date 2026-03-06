import json

class DataStorage:
    def __init__(self, filename):
        self.filename = filename

    def save_data(self, data):
        with open(self.filename, 'w') as f:
            json.dump(data, f, indent=4)

    def load_data(self):
        try:
            with open(self.filename, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}  # Return empty dict if file does not exist
        except json.JSONDecodeError:
            return {}  # Return empty dict if file is not valid JSON

# Example usage:
# storage = DataStorage('data.json')
# storage.save_data({'key': 'value'})
# data = storage.load_data()