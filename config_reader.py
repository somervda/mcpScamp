import json
from pathlib import Path

class ConfigReader:
    def __init__(self, config_file="config.json"):
        self.config_file = Path(config_file)
        self._config_data = None
    
    @property
    def gps_file(self):
        """Get the GPS file path from config."""
        if self._config_data is None:
            self._load_config()
        return self._config_data.get("gps_file")
    
    def _load_config(self):
        """Load configuration from JSON file."""
        try:
            with open(self.config_file, 'r') as f:
                self._config_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Config file {self.config_file} not found")
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in config file {self.config_file}")

def main():
    # Create a sample config file for testing
    sample_config = {
        "gps_file": "c:/temp/gps.json"
    }
    
    # Write sample config
    with open("config.json", "w") as f:
        json.dump(sample_config, f, indent=2)
    
    # Test the ConfigReader class
    try:
        config = ConfigReader("config.json")
        print(f"GPS file path: {config.gps_file}")
        
        # Test that it's a property
        print(f"Type of gps_file: {type(config.gps_file)}")
        
        # Test accessing non-existent config file
        config2 = ConfigReader("nonexistent.json")
        print(config2.gps_file)
        
    except FileNotFoundError as e:
        print(f"Error: {e}")
    except ValueError as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
