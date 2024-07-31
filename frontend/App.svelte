<script>
  import { onMount } from 'svelte';
  import { writable } from 'svelte/store';

  const searchResults = writable([]);
  const selectedPlaylists = writable([]);
  const combinedTracks = writable([]);

  let searchTerm = '';

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
