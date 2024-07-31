<!-- ./frontend/App.svelte -->

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

  // Initialize MusicKit and set up event listeners
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
      musicKitInstance.player.volume = 0.5; // Set initial volume
    });
  });

  // Function to authenticate the user and retrieve the User Token
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

  // Function to search for playlists using the API
  async function searchPlaylists() {
    const response = await fetch(`/api/search?query=${searchTerm}`);
    const data = await response.json();
    searchResults.set(data.results.playlists.data);
  }

  // Function to add selected playlist to the list of selected playlists
  function selectPlaylist(playlist) {
    selectedPlaylists.update(playlists => [...playlists, playlist]);
  }

  // Function to create a combined playlist from selected playlists
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

  <!-- Button to authenticate the user if not authorized -->
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
