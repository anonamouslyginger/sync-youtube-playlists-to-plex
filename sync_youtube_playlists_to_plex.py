"""
Sync YouTube playlists for a channel to a Plex media server.

This will not download the videos and assumes that the videos are already on the server.
"""
import argparse
import logging
import sys
import yt_dlp
from plexapi.server import PlexServer

# Set up logging first
logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")


class YtDlpLogger:
    """yt-dlp logger bypass"""

    def debug(self, msg):
        """DEBUG log"""
        if msg.startswith("[debug] "):
            logging.debug(msg)
        else:
            self.info(msg)

    def info(self, msg):
        """INFO log"""

    def warning(self, msg):
        """WARNING log"""

    def error(self, msg):
        """ERROR log"""
        logging.error(msg)


def confirm_config(plex_url, plex_library, youtube_url):
    """Confirms with the user that the configuration is correct"""
    print("This application will sync playlists from YouTube to Plex!")
    print("Please confirm the below information is correct:")
    print()
    print(f"    Plex URL: {plex_url}")
    print(f"    Plex Library: {plex_library}")
    print(f"    YouTube Channel: {youtube_url}")
    print()
    try:
        if input("Is this correct? [y/N]: ").upper() != "Y":
            sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)


def get_playlists_from_channel(client, youtube_url):
    """Get playlist URLs and Titles for the given channel"""
    playlists_url = f"{youtube_url}/playlists?view=1&sort=dd&shelf_id=0"
    playlists = client.extract_info(playlists_url)
    return [(i["url"], i["title"]) for i in playlists["entries"]]


def get_videos_from_playlist(client, youtube_url):
    """Get video Titles for the given playlist"""
    channel_playlist = client.extract_info(youtube_url)
    return [(i["title"]) for i in channel_playlist["entries"]]


# Be civil and get all out arguments from the command line
parser = argparse.ArgumentParser()
parser.add_argument(
    "--plex-url",
    help="URL of the Plex instance (e.g. http://localhost:32400)",
    required=True,
    action="store",
)
parser.add_argument(
    "--plex-token",
    help=(
        "Token to use to talk to the Plex API (see"
        " https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)"
    ),
    required=True,
    action="store",
)
parser.add_argument(
    "--plex-library",
    help="Library/Section to scan for videos and create playlists",
    required=True,
    action="store",
)
parser.add_argument(
    "--youtube-channel-id",
    help="ID of the YouTube channel to create playlists for",
    required=True,
    action="store",
)
parser.add_argument(
    "-u",
    "--unattended",
    help="Assume no human is present and do not confirm that the settings are correct",
    action="store_true",
)
args = parser.parse_args()

youtube_channel_url = f"https://www.youtube.com/channel/{args.youtube_channel_id}"

# If we are not unattended then ask the user to confirm config
if not args.unattended:
    confirm_config(args.plex_url, args.plex_library, youtube_channel_url)

plex = PlexServer(args.plex_url, args.plex_token)
plex_section = plex.library.section(args.plex_library)
youtube = yt_dlp.YoutubeDL(
    {
        "quiet": True,
        "skip_download": True,
        "extract_flat": True,
        "logger": YtDlpLogger(),
    }
)

channel_playlists = get_playlists_from_channel(youtube, youtube_channel_url)
for playlist_url, playlist_title in channel_playlists:
    logging.debug("Processing playlist '%s' at '%s'", playlist_title, playlist_url)

    plex_playlist_entries = []
    for video_title in get_videos_from_playlist(youtube, playlist_url):

        # Ignore private videos
        if video_title == "[Private video]":
            continue

        video_search = plex_section.search(title=video_title)
        if len(video_search) == 1:
            logging.debug("Video with name '%s' found in plex", video_title)
            plex_playlist_entries.append(video_search[0])
        else:
            logging.warning("Video with name '%s' not found in Plex", video_title)

    # If we have no videos from the playlist don't do anything
    if len(plex_playlist_entries) == 0:
        logging.warning(
            "Skipping playlist '%s' as no videos exist in Plex", playlist_title
        )
        continue

    playlist_search = plex_section.search(title=playlist_title, libtype="collection")

    # If the playlist does not exist, create it
    if len(playlist_search) == 0:
        logging.debug("Creating playlist with name '%s' in Plex", playlist_title)
        plex.createCollection(playlist_title, plex_section, items=plex_playlist_entries)
    else:
        plex_playlist = playlist_search[0]

        # Remove all items and re-add
        plex_playlist.removeItems(plex_playlist.items())
        plex_playlist.addItems(plex_playlist_entries)

        logging.debug("Updated playlist with name '%s' in Plex", playlist_title)

logging.info("Processed %d playlists", len(channel_playlists))
sys.exit(0)
