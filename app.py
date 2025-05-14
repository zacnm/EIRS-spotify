!pip install spotipy matplotlib wordcloud

import streamlit as st
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests
from wordcloud import WordCloud
import matplotlib.pyplot as plt

st.title("Spotify Artist Explorer")

client_id = st.text_input("Enter your Spotify Client ID:")
client_secret = st.text_input("Enter your Spotify Client Secret:", type="password")

if client_id and client_secret:
    try:
        client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        st.success("Connected to Spotify API")
    except Exception as e:
        st.error(f"Error connecting to Spotify API: {e}")

    artist_name = st.text_input("Enter artist name:")

    if artist_name:
        try:
            def get_artist_albums(artist_name):
                results = sp.search(q=f'artist:{artist_name}', type='artist')
                artists = results['artists']['items']

                if not artists:
                    raise Exception(f"No artist found with name {artist_name}")

                artist = artists[0]
                artist_id = artist['id']
                albums = []
                results = sp.artist_albums(artist_id, album_type='album')
                albums.extend(results['items'])

                while results['next']:
                    results = sp.next(results)
                    albums.extend(results['items'])

                return {album['name']: album['id'] for album in albums}

            albums = get_artist_albums(artist_name)
            album_name = st.selectbox("Select an album:", [""] + list(albums.keys()), index=0)

            if album_name and album_name != "":
                album_id = albums[album_name]

                def get_album_tracks(album_id):
                    results = sp.album_tracks(album_id)
                    tracks = results['items']
                    return [track['name'] for track in tracks]

                tracks = get_album_tracks(album_id)
                track_name = st.selectbox("Select a track:", [""] + tracks, index=0)

                if track_name and track_name != "":
                    def get_track_lyrics(artist_name, track_name):
                        response = requests.get(f"https://api.lyrics.ovh/v1/{artist_name}/{track_name}")
                        response.raise_for_status()
                        data = response.json()
                        return data.get("lyrics", "Lyrics not found.")

                    try:
                        lyrics = get_track_lyrics(artist_name, track_name)

                        wordcloud = WordCloud(width=800, height=400, background_color='white').generate(lyrics.lower())

                        st.subheader("Lyrics Word Cloud")
                        fig = plt.figure(figsize=(10, 5))
                        plt.imshow(wordcloud, interpolation='bilinear')
                        plt.axis('off')
                        st.pyplot(fig)
                    except Exception as e:
                        st.error(f"Error retrieving lyrics: {e}")
        except Exception as e:
            st.error(f"Error retrieving albums: {e}")
