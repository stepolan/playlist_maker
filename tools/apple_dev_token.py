import jwt
import time
import os
import json

# File to store the necessary credentials
CONFIG_FILE = 'apple_music_config.json'

# Template for the configuration file
CONFIG_TEMPLATE = {
    "TEAM_ID": "YOUR_TEAM_ID",
    "KEY_ID": "YOUR_KEY_ID",
    "PRIVATE_KEY": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----"
}

def create_config_template():
    """Creates a template config file for the user to fill in."""
    with open(CONFIG_FILE, 'w') as f:
        json.dump(CONFIG_TEMPLATE, f, indent=4)
    print(f"Configuration template created: {CONFIG_FILE}")
    print("Please fill in your TEAM_ID, KEY_ID, and PRIVATE_KEY.")

def load_config():
    """Loads configuration from the file."""
    if not os.path.exists(CONFIG_FILE):
        print("Configuration file not found.")
        create_config_template()
        return None
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    return config

def generate_developer_token(team_id, key_id, private_key):
    """Generates a Developer Token for Apple Music API."""
    current_time = int(time.time())
    expiry_time = current_time + 86400 * 180  # Token valid for 180 days
    headers = {
        "alg": "ES256",
        "kid": key_id
    }
    payload = {
        "iss": team_id,
        "iat": current_time,
        "exp": expiry_time
    }

    token = jwt.encode(payload, private_key, algorithm='ES256', headers=headers)
    return token

def main():
    config = load_config()
    if not config:
        return

    team_id = config['TEAM_ID']
    key_id = config['KEY_ID']
    private_key = config['PRIVATE_KEY']

    developer_token = generate_developer_token(team_id, key_id, private_key)
    print(f"Developer Token: {developer_token}")

    # Ask the user if they want to delete the template file
    delete_choice = input(f"Do you want to delete the {CONFIG_FILE} file? (yes/no): ").strip().lower()
    if delete_choice == 'yes':
        os.remove(CONFIG_FILE)
        print(f"{CONFIG_FILE} has been deleted.")
    else:
        print(f"{CONFIG_FILE} has been kept.")

if __name__ == '__main__':
    main()
