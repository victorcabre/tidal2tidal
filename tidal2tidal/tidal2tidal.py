import logging
from pathlib import Path
import sys

import tidalapi
from tqdm import tqdm


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(sys.stdout))

oauth_file_1 = Path("tidal-session-A.json")
oauth_file_2 = Path("tidal-session-B.json")

def do_transfer():
    session_src = tidalapi.Session()
    session_dst = tidalapi.Session()
    logger.info("Login to user A (source)...")
    if not session_src.login_session_file(oauth_file_1):
        logger.error("ERROR: Unable to login to Tidal")
        exit(1)
    logger.info("Login to user B (destination)...")
    if not session_dst.login_session_file(oauth_file_2):
        logger.error("ERROR: Unable to login to Tidal")
        exit(1)

    # Transfer liked tracks
    tracks = session_src.user.favorites.tracks()
    tracks_sorted = sorted(tracks, key=lambda x: x.user_date_added)
    for track in tqdm(tracks_sorted, desc="Transferring liked tracks"):
        try:
            session_dst.user.favorites.add_track(track.id)
        except:
            logger.error(f"error while adding track {track.id} {track.name}")

    # Transfer liked albums
    albums = session_src.user.favorites.albums()
    for album in tqdm(albums, desc="Transferring liked albums"):
        try:
            session_dst.user.favorites.add_album(album.id)
        except:
            logger.error(f"error while adding album {album.id} {album.name}")

    # Transfer liked artists
    artists = session_src.user.favorites.artists()
    for artist in tqdm(artists, desc="Transferring artists"):
        try:
            session_dst.user.favorites.add_artist(artist.id)
        except:
            logger.error(f"An error occurred while adding artist {artist.id} - {artist.name}")

    # Transfer playlists (liked and user created)
    user_playlists = session_src.user.playlists()
    all_playlists = session_src.user.playlist_and_favorite_playlists()
    
    user_playlist_ids = {playlist.id for playlist in user_playlists}
    liked_playlists = [playlist for playlist in all_playlists if playlist.id not in user_playlist_ids]

    for playlist in tqdm(user_playlists, desc="Transferring user playlists"):
        try:
            new_playlist: tidalapi.UserPlaylist = session_dst.user.create_playlist(playlist.name, playlist.description)
            tracks = sorted(playlist.tracks(), key=lambda x: x.user_date_added)

            new_playlist.add([track.id for track in tracks])
        except:
            logger.error(f"An error occurred while creating playlist {playlist.id} - {playlist.name}")

    for playlist in tqdm(liked_playlists, desc="Transferring liked playlists"):
        try:
            session_dst.user.favorites.add_playlist(playlist.id)
        except:
            logger.error(f"An error occurred while adding playlist {playlist.id} - {playlist.name}")
            
    logger.info("Transfer complete.")


if __name__ == "__main__":
    do_transfer()