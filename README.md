# Sync YouTube Playlists to Plex
This Python module will create Plex [Collections](https://support.plex.tv/articles/201273953-collections/)
which match those on a given YouTube channel.

**NOTE** There is an assumption that you have used something like [yt-dlp](https://github.com/yt-dlp/yt-dlp)
or [tubearchivist](https://github.com/tubearchivist/tubearchivist) to download the videos from your
favorite YouTube channels and have imported them into your Plex Media Server.

This module only groups your videos into Plex Collections, **it does not download videos or add them to Plex**

## Installation
Clone this repo and run:
```bash
pip install -r requirements.txt
```

## Usage
See the following output for the available options:
```
usage: sync_youtube_playlists_to_plex.py [-h] --plex-url PLEX_URL --plex-token PLEX_TOKEN --plex-library PLEX_LIBRARY --youtube-channel-id YOUTUBE_CHANNEL_ID [-u]

optional arguments:
  -h, --help            show this help message and exit
  --plex-url PLEX_URL   URL of the Plex instance (e.g. http://localhost:32400)
  --plex-token PLEX_TOKEN
                        Token to use to talk to the Plex API (see https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/)
  --plex-library PLEX_LIBRARY
                        Library/Section to scan for videos and create playlists
  --youtube-channel-id YOUTUBE_CHANNEL_ID
                        ID of the YouTube channel to create playlists for
  -u, --unattended      Assume no human is present and do not confirm that the settings are correct
```

## Example usage
To get a Plex Token see [these instructions](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/).

```bash
python3 sync_youtube_playlists_to_plex.py --plex-token <redacted> --plex-url "http://plex.local:32400" --plex-library YouTube --youtube-channel-id UCXuqSBlHAE6Xw-yeJA0Tunw
```
