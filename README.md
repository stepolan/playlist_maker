# Project Documentation: Apple Music Playlist Combiner

## Project Goals

1. Search Apple Music Playlists.
2. Tag and Select Playlists.
3. Combine Playlists.
4. Use Python for Backend (Flask).
5. Use Svelte for Frontend.
6. Manage Environment with Conda.

## Project Structure

```txt
apple_pl_combiner/
├── backend/
│   ├── app.py
│   ├── .env
│   └── environment.yml
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
├── tools/
│   └── apple_dev_token.py
└── run.py
```

## Setup Instructions

### 1. Environment Setup

1. **Create project structure**:

    ```bash
    mkdir apple_pl_combiner
    cd apple_pl_combiner
    mkdir /apple
    mkdir -p /backend /frontend/public /frontend/src /tools
    touch /LICENSE /backend/app.py /backend/.env /backend/environment.yml /frontend/package.json /frontend/vite.config.js /tools/apple_dev_token.py
    ```

2. **Install Conda**: If Conda is not already installed, download and install it from [Conda's official site](https://docs.conda.io/projects/conda/en/latest/user-guide/install/index.html).

3. **Create `environment.yml`**:

    ```yaml
    name: myenv
    channels:
        - defaults
        - conda-forge
    dependencies:
        - python=3.8
        - flask
        - flask-cors
        - requests
        - python-dotenv
    ```

4. **Create and activate Conda environment**:

    ```bash
    conda env create -f environment.yml
    conda activate myenv
    ```

5. **Install Node.js and npm**: Install from [Node.js official site](https://nodejs.org/).

### 2. Backend: Flask

1. **Create `.env` file**: Add your Apple Music API tokens.

    ```sh
    DEVELOPER_TOKEN=your_developer_token_here
    USER_TOKEN=your_user_token_here
    ```

2. **Implement Flask application**: Add endpoints in `app.py`.

    ```python
    # app.py

    from flask import Flask, request, jsonify
    from flask_cors import CORS
    import requests
    import os
    from dotenv import load_dotenv

    load_dotenv()

    app = Flask(__name__)
    CORS(app)

    DEVELOPER_TOKEN = os.getenv('DEVELOPER_TOKEN')
    USER_TOKEN = os.getenv('USER_TOKEN')

    def search_playlists(query):
        url = f'https://api.music.apple.com/v1/catalog/us/search?term={query}&types=playlists'
        headers = {
            'Authorization': f'Bearer {DEVELOPER_TOKEN}',
            'Music-User-Token': USER_TOKEN
        }
        response = requests.get(url, headers=headers)
        return response.json()

    def get_playlist_tracks(playlist_id):
        url = f'https://api.music.apple.com/v1/catalog/us/playlists/{playlist_id}'
        headers = {
            'Authorization': f'Bearer {DEVELOPER_TOKEN}',
            'Music-User-Token': USER_TOKEN
        }
        response = requests.get(url, headers=headers)
        data = response.json()
        tracks = data['data'][0]['relationships']['tracks']['data']
        return [track['id'] for track in tracks]

    def create_playlist(name, description, track_ids):
        url = 'https://api.music.apple.com/v1/me/library/playlists'
        headers = {
            'Authorization': f'Bearer {DEVELOPER_TOKEN}',
            'Music-User-Token': USER_TOKEN,
            'Content-Type': 'application/json'
        }
        playlist_data = {
            'attributes': {
                'name': name,
                'description': description
            },
            'relationships': {
                'tracks': {
                    'data': [{'id': track_id, 'type': 'songs'} for track_id in track_ids]
                }
            }
        }
        response = requests.post(url, json=playlist_data, headers=headers)
        return response.json()

    @app.route('/search', methods=['GET'])
    def search():
        query = request.args.get('query')
        playlists = search_playlists(query)
        return jsonify(playlists)

    @app.route('/tracks/<playlist_id>', methods=['GET'])
    def tracks(playlist_id):
        tracks = get_playlist_tracks(playlist_id)
        return jsonify(tracks)

    @app.route('/create_playlist', methods=['POST'])
    def create():
        data = request.json
        name = data.get('name')
        description = data.get('description')
        track_ids = data.get('track_ids')
        new_playlist = create_playlist(name, description, track_ids)
        return jsonify(new_playlist)

    if __name__ == '__main__':
        app.run(debug=True)
    ```

### 3. Frontend: Svelte

1. **Initialize Svelte project**:

    ```bash
    npm init svelte@next
    npm install
    ```

2. **Set up `package.json`**: Add necessary dependencies and scripts.

3. **Configure Vite (`vite.config.js`)**: Set up proxy for API requests to Flask backend.

    ```js
    // vite.config.js

    import { defineConfig } from 'vite';
    import { svelte } from '@sveltejs/vite-plugin-svelte';

    export default defineConfig({
      plugins: [svelte()],
      server: {
        proxy: {
          '/api': {
            target: 'http://localhost:5000',
            changeOrigin: true,
            rewrite: (path) => path.replace(/^\/api/, '')
          }
        }
      }
    });
    ```

4. **Create `App.svelte`**:

    ```svelte
    <!-- src/App.svelte -->

    <script>
      import { onMount } from 'svelte';
      import { writable } from 'svelte/store';

      const searchResults = writable([]);
      const selectedPlaylists = writable([]);
      const combinedTracks = writable([]);
      const userToken = writable('');
      let musicKitInstance = null;
      let isAuthorized = false;
      let searchTerm = '';

      onMount(() => {
        document.addEventListener("musickitloaded", () => {
          musicKitInstance = MusicKit.getInstance();
          musicKitInstance.configure({
            developerToken: 'YOUR_DEVELOPER_TOKEN',
            app: {
              name: 'Apple Music Playlist Combiner',
              build: '1.0'
            }
          });
          musicKitInstance.player.volume = 0.5;
        });
      });

      async function authenticateUser() {
        try {
          const token = await musicKitInstance.authorize();
          userToken.set(token);
          isAuthorized = true;
          console.log("User Token: ", token);
        } catch (error) {
          console.error("Authentication failed:", error);
        }
      }

      async function searchPlaylists() {
        const response = await fetch(`/api/search?query=${searchTerm}`);
        const data = await response.json();
        searchResults.set(data.results.playlists.data);
      }

      function selectPlaylist(playlist) {
        selectedPlaylists.update(playlists => [...playlists, playlist]);
      }

      async function createCombinedPlaylist() {
        const tracks = [];
        const playlists = $selectedPlaylists;
        for (const playlist of playlists) {
          const response = await fetch(`/api/tracks/${playlist.id}`);
          const data = await response.json();
          tracks.push(...data);
        }

        const response = await fetch('/api/create_playlist', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            name: 'Combined Playlist',
            description: 'Combined from multiple playlists',
            track_ids: tracks
          })
        });

        const data = await response.json();
        alert('Playlist created successfully!');
      }
    </script>

    <main>
      <h1>Apple Music Playlist Combiner</h1>

      {#if !isAuthorized}
        <button on:click={authenticateUser}>Login with Apple Music</button>
      {/if}

      <input type="text" bind:value={searchTerm} placeholder="Search for playlists" />
      <button on:click={searchPlaylists}>Search</button>

      <h2>Search Results</h2>
      <ul>
        {#each $searchResults as playlist}
          <li>
            <p>{playlist.attributes.name}</p>
            <button on:click={() => selectPlaylist(playlist)}>Select</button>
          </li>
        {/each}
      </ul>

      <h2>Selected Playlists</h2>
      <ul>
        {#each $selectedPlaylists as playlist}
          <li>{playlist.attributes.name}</li>
        {/each}
      </ul>

      <button on:click={createCombinedPlaylist}>Create Combined Playlist</button>
    </main>

    <style>
      main {
        max-width: 600px;
        margin: 0 auto;
        padding: 1rem;
        text-align: center;
      }

      input {
        width: calc(100% - 2rem);
        padding: 0.5rem;
        margin: 1rem 0;
      }

      button {
        padding: 0.5rem 1rem;
        margin: 0.5rem;
      }

      ul {
        list-style-type: none;
        padding: 0;
      }

      li {
        margin: 1rem 0;
      }
    </style>
    ```

### 4. Integration

1. **Create a `run.py` script** to run both Flask and Svelte applications.

    ```python
    # run.py

    import subprocess

    # Run Flask app
    subprocess.Popen(["python", "backend/app.py"])

    # Run Svelte app
    subprocess.Popen(["npm", "run", "dev"], cwd="frontend")
    ```

### 5. Version Control and Collaboration

1. **Initialize Git repository**:

    ```bash
    git init
    ```

2. **Set up GitHub repository**: Create a new repository on GitHub and push the initial commit.

    ```bash
    git remote add origin https://github.com/your-username/apple-music-playlist-combiner.git
    git add .
    git commit -m "Initial project structure"
    git push -u origin main
    ```

3. **Install VS Code extensions** for Python, Svelte, and other tools.

## Generating Developer and User Tokens

To interact with the Apple Music API, you need a Developer Token and a User Token.

### Developer Token

1. **Create an Apple ID**: If you don’t have one, create an Apple ID [here](https://appleid.apple.com/account).

2. **Enroll in the Apple Developer Program**: Visit [developer.apple.com/programs/enroll](https://developer.apple.com/programs/enroll) and enroll using your Apple ID.

3. **Generate a Key**: 
   - Go to the [Apple Developer Account](https://developer.apple.com/account/) and navigate to "Certificates, Identifiers & Profiles".
   - Create a new key under the "Keys" section and enable the "MusicKit" capability.
   - Download the private key file (.p8) immediately after creating it.

4. **Use the Script to Generate Developer Token**:
   - Place the `apple_dev_token.py` script in the `/tools` directory.

    ```python
    # tools/apple_dev_token.py

    import jwt
    import time
    import os
    import json

    CONFIG_FILE = 'apple_music_config.json'

    CONFIG_TEMPLATE = {
        "TEAM_ID": "YOUR_TEAM_ID",
        "KEY_ID": "YOUR_KEY_ID",
        "PRIVATE_KEY": "-----BEGIN PRIVATE KEY-----\nYOUR_PRIVATE_KEY_HERE\n-----END PRIVATE KEY-----"
    }

    def create_config_template():
        with open(CONFIG_FILE, 'w') as f:
            json.dump(CONFIG_TEMPLATE, f, indent=4)
        print(f"Configuration template created: {CONFIG_FILE}")
        print("Please fill in your TEAM_ID, KEY_ID, and PRIVATE_KEY.")

    def load_config():
        if not os.path.exists(CONFIG_FILE):
            print("Configuration file not found.")
            create_config_template()
            return None
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        return config

    def generate_developer_token(team_id, key_id, private_key):
        current_time = int(time.time())
        expiry_time = current_time + 86400 * 180
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

        delete_choice = input(f"Do you want to delete the {CONFIG_FILE} file? (yes/no): ").strip().lower()
        if delete_choice == 'yes':
            os.remove(CONFIG_FILE)
            print(f"{CONFIG_FILE} has been deleted.")
        else:
            print(f"{CONFIG_FILE} has been kept.")

    if __name__ == '__main__':
        main()
    ```

5. **Run the Script**: 
   - Navigate to the `/tools` directory and run the script to generate the Developer Token.

   ```bash
   python apple_dev_token.py
   ```

### User Token

1. **Include MusicKit JS in Frontend**:
   - Add the MusicKit JS script in your `index.html` file.

   ```html
   <!DOCTYPE html>
   <html lang="en">
   <head>
     <meta charset="UTF-8">
     <meta name="viewport" content="width=device-width, initial-scale=1.0">
     <title>Apple Music Playlist Combiner</title>
     <script src="https://js-cdn.music.apple.com/musickit/v1/musickit.js"></script>
   </head>
   <body>
     <script type="text/javascript">
       document.addEventListener("musickitloaded", function() {
         MusicKit.configure({
           developerToken: 'YOUR_DEVELOPER_TOKEN',
           app: {
             name: 'Apple Music Playlist Combiner',
             build: '1.0'
           }
         });
       });
     </script>
     <div id="svelte-app"></div>
     <script src="/build/bundle.js"></script>
   </body>
   </html>
   ```

2. **User Authentication**:
   - Implement user authentication in `App.svelte` using MusicKit JS, as shown in the frontend section above.

3. **Handling the User Token**:
   - Use the User Token for making authenticated API calls to access user-specific Apple Music content.

By following these steps, you can set up your environment, implement both backend and frontend components, and manage the necessary authentication tokens for accessing the Apple Music API.
