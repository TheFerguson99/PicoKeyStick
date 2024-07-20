import os


class CSVHandler:
    def __init__(self, file_path = "/data/data.csv"):
        self.file_path = file_path
        # Check if the file exists
        try:
            os.stat(self.file_path)
        except OSError:
            try:
                # File does not exist, create it with a header
                with open(self.file_path, mode='w') as file:
                    file.write('name,value\n')
                print(f"File created with header: {self.file_path}")
            except:
                print("Error Readonly FileSystem.")
    
    def write_to_csv(self, data):
        """Append data to CSV file."""
        try:
            with open(self.file_path, mode='a') as file:  # Open in append mode
                for name, value in data.items():
                    file.write(f'{name},{value}\n')
            print("Data appended to CSV successfully.")
        except OSError as e:
            print(f"Error writing to {self.file_path}: {e}")

    def read_from_csv(self):
        """Read data from CSV file and return as a dictionary."""
        data = {}
        try:
            with open(self.file_path, mode='r') as file:
                lines = file.readlines()
                for line in lines[1:]:  # Skip the header
                    name, value = line.strip().split(',')
                    data[name] = value
        except OSError as e:
            print(f"Error reading from {self.file_path}: {e}")
        return data

    def get_value_by_name(self, name):
        """Retrieve the value for a given name from the CSV file."""
        data = self.read_from_csv()
        try:
            result = data.get(name)
        except:
            result = None
        return result
    def update_value(self, name, new_value):
        """Update the value for a given name in the CSV file."""
        data = self.read_from_csv()
        if name in data:
            data[name] = new_value
            try:
                with open(self.file_path, mode='w') as file:
                    file.write('name,value\n')
                    for key, value in data.items():
                        file.write(f'{key},{value}\n')
                print("Data updated in CSV successfully.")
            except OSError as e:
                print(f"Error writing to {self.file_path}: {e}")
        else:
            print(f"Name '{name}' not found in CSV.")

    def remove_entry(self, name):
        """Remove entry with the given name from CSV file."""
        try:
            # Read the current contents of the file
            with open(self.file_path, mode='r') as file:
                lines = file.readlines()

            # Filter out the lines that do not match the given name
            with open(self.file_path, mode='w') as file:
                for line in lines:
                    if not line.startswith(f'{name},'):
                        file.write(line)

            print(f"Entry with name '{name}' removed from CSV successfully.")
        except OSError as e:
            print(f"Error reading or writing to {self.file_path}: {e}")


