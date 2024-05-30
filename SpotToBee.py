import csv
import re
import os
import xml.etree.ElementTree as ET
import configparser
import argparse
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import requests

CONFIG_FILE_DEFAULT = 'config.ini'

def load_config(config_file):
    config = configparser.ConfigParser()
    config.read(config_file)
    return config

def create_default_config(config_file):
    config = configparser.ConfigParser()
    config['ExclusionOptions'] = {
        'IncludeCompilation': 'False',
        'IncludeLive': 'False',
        'IncludeBroadcast': 'False',
        'IncludeSingle': 'False',
        'IncludeSoundtrack': 'False',
        'IncludeDemo': 'False',
        'IncludeEP': 'False'
    }
    config['OutputOptions'] = {'OutputDirectory': '', 'DeleteSpotifyCSVs': 'False'}
    config['ReleaseType'] = {'Field': ''}
    config['MusicLibrary'] = {'Path': ''}
    config['SpotifyAPI'] = {'ClientID': '', 'ClientSecret': ''}
    with open(config_file, 'w') as f:
        config.write(f)

def prompt_config():
    config = configparser.ConfigParser()
    output_dir = input("Enter playlist output directory: ")
    if not output_dir:
        output_dir = ''
    music_library_path = input("Enter your MusicBee library path: ")
    if not music_library_path:
        music_library_path = ''
    config['OutputOptions'] = {'OutputDirectory': output_dir}

    delete_spotify_csvs = input("Save Spotify playlists as CSVs? (yes/no): ")
    config['OutputOptions']['DeleteSpotifyCSVs'] = 'True' if delete_spotify_csvs.lower() in ['yes', 'y'] else 'False'

    config['MusicLibrary'] = {'Path': music_library_path}

    filter_by_release = input("Do you want to filter by release type? (yes/no): ")
    if filter_by_release.lower() in ['yes', 'y']:
        config['ExclusionOptions'] = {
            'IncludeCompilation': 'True',
            'IncludeLive': 'True',
            'IncludeBroadcast': 'True',
            'IncludeSingle': 'True',
            'IncludeSoundtrack': 'True',
            'IncludeDemo': 'True',
            'IncludeEP': 'True'
        }

        release_type_tag = input("Enter the tag in which the Release Type is located (e.g., Custom1): ")
        config['ReleaseType'] = {'Field': release_type_tag}

        exclude_compilation = input("Exclude compilations? (yes/no): ")
        config['ExclusionOptions']['IncludeCompilation'] = 'False' if exclude_compilation.lower() in ['yes', 'y'] else 'True'

        exclude_live = input("Exclude live recordings? (yes/no): ")
        config['ExclusionOptions']['IncludeLive'] = 'False' if exclude_live.lower() in ['yes', 'y'] else 'True'

        exclude_broadcast = input("Exclude broadcasts? (yes/no): ")
        config['ExclusionOptions']['IncludeBroadcast'] = 'False' if exclude_broadcast.lower() in ['yes', 'y'] else 'True'

        exclude_single = input("Exclude singles? (yes/no): ")
        config['ExclusionOptions']['IncludeSingle'] = 'False' if exclude_single.lower() in ['yes', 'y'] else 'True'

        exclude_soundtrack = input("Exclude soundtracks? (yes/no): ")
        config['ExclusionOptions']['IncludeSoundtrack'] = 'False' if exclude_soundtrack.lower() in ['yes', 'y'] else 'True'

        exclude_demo = input("Exclude demo versions? (yes/no): ")
        config['ExclusionOptions']['IncludeDemo'] = 'False' if exclude_demo.lower() in ['yes', 'y'] else 'True'

        exclude_ep = input("Exclude EPs? (yes/no): ")
        config['ExclusionOptions']['IncludeEP'] = 'False' if exclude_ep.lower() in ['yes', 'y'] else 'True'

    use_spotify = input("Do you want to fetch data from Spotify URLs? (yes/no): ")
    if use_spotify.lower() in ['yes', 'y']:
        client_id = input("Enter Spotify Client ID: ")
        client_secret = input("Enter Spotify Client Secret: ")
        config['SpotifyAPI'] = {'ClientID': client_id, 'ClientSecret': client_secret}

    return config

def clean_track_name(track_name):
    track_name = re.sub(r'\([^)]*\)', '', track_name)
    track_name = re.sub(r'\[[^\]]*\]', '', track_name)
    track_name = re.sub(r' - \d{4} remaster.*$', '', track_name)
    track_name = re.sub(r' - [^\-]*$', '', track_name)
    return track_name.strip()

def convert_to_xml(csv_file, config):
    output_dir = config.get('OutputOptions', 'OutputDirectory', fallback="")
    music_library_path = config.get('MusicLibrary', 'Path', fallback="")
    release_type_field = config.get('ReleaseType', 'Field', fallback="Custom1")

    output_file = os.path.splitext(os.path.basename(csv_file))[0].replace('_', ' ').title() + ".xautopf"
    output_path = os.path.join(output_dir, output_file)
    root = ET.Element("SmartPlaylist", SaveStaticCopy="False", LiveUpdating="True", Layout="4", LayoutGroupBy="0",
                      ShuffleMode="None", ShuffleSameArtistWeight="0.5", GroupBy="track", ConsolidateAlbums="False",
                      MusicLibraryPath=music_library_path)

    source = ET.SubElement(root, "Source", Type="1")
    conditions = ET.SubElement(source, "Conditions", CombineMethod="Any")

    with open(csv_file, 'r', encoding='utf-8-sig') as file:
        reader = csv.DictReader(file)
        for row in reader:
            track_name = clean_track_name(row['Track Name'])
            artist_name = row['Artist Name(s)']
            condition = ET.SubElement(conditions, "Condition", Field="Title", Comparison="Contains", Value=track_name)
            and_condition = ET.SubElement(condition, "And", CombineMethod="All")
            artist_condition = ET.SubElement(and_condition, "Condition", Field="ArtistPeople", Comparison="Is", Value=artist_name)

            if not config.getboolean('ExclusionOptions', 'IncludeCompilation', fallback=True):
                exclusion_condition = ET.SubElement(and_condition, "Condition", Field=release_type_field, Comparison="IsNot", Value="compilation")
            if not config.getboolean('ExclusionOptions', 'IncludeLive', fallback=True):
                exclusion_condition = ET.SubElement(and_condition, "Condition", Field=release_type_field, Comparison="IsNot", Value="live")
                exclusion_condition_title = ET.SubElement(and_condition, "Condition", Field="Title", Comparison="DoesNotContain", Value="(live")
                exclusion_condition_title = ET.SubElement(and_condition, "Condition", Field="Title", Comparison="DoesNotContain", Value="live)")
            if not config.getboolean('ExclusionOptions', 'IncludeBroadcast', fallback=True):
                exclusion_condition = ET.SubElement(and_condition, "Condition", Field=release_type_field, Comparison="IsNot", Value="broadcast")
            if not config.getboolean('ExclusionOptions', 'IncludeSingle', fallback=True):
                exclusion_condition = ET.SubElement(and_condition, "Condition", Field=release_type_field, Comparison="IsNot", Value="single")
            if not config.getboolean('ExclusionOptions', 'IncludeSoundtrack', fallback=True):
                exclusion_condition = ET.SubElement(and_condition, "Condition", Field=release_type_field, Comparison="IsNot", Value="soundtrack")
            if not config.getboolean('ExclusionOptions', 'IncludeDemo', fallback=True):
                exclusion_condition = ET.SubElement(and_condition, "Condition", Field=release_type_field, Comparison="IsNot", Value="demo")
                exclusion_condition_title = ET.SubElement(and_condition, "Condition", Field="Title", Comparison="DoesNotContain", Value="(demo")
                exclusion_condition_title = ET.SubElement(and_condition, "Condition", Field="Title", Comparison="DoesNotContain", Value="demo)")
            if not config.getboolean('ExclusionOptions', 'IncludeEP', fallback=True):
                exclusion_condition = ET.SubElement(and_condition, "Condition", Field=release_type_field, Comparison="IsNot", Value="ep")

    limit = ET.SubElement(source, "Limit", FilterDuplicates="True", Enabled="False", Count="25", Type="Items", SelectedBy="Random")
    sort_by = ET.SubElement(source, "SortBy", Field="30", Order="Ascending")

    tree = ET.ElementTree(root)
    tree.write(output_path, encoding="utf-8", xml_declaration=True)
    print(f"Playlist '{output_file}' created successfully.")

def download_playlist_cover(playlist_name, playlist_id, output_dir, config):
    try:
        client_credentials_manager = SpotifyClientCredentials(client_id=config.get('SpotifyAPI', 'ClientID'),
                                                              client_secret=config.get('SpotifyAPI', 'ClientSecret'))
        sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)
        playlist_cover_url = sp.playlist_cover_image(playlist_id)[0]['url']
        response = requests.get(playlist_cover_url)
        if response.status_code == 200:
            playlist_name = playlist_name.replace('_', ' ')
            with open(os.path.join(output_dir, f"{playlist_name}.jpg"), 'wb') as f:
                f.write(response.content)
            print(f"Playlist cover for '{playlist_name}' downloaded successfully.")
        else:
            print(f"Failed to download playlist cover. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error downloading playlist cover: {e}")

def get_playlist_tracks(playlist_id, config):
    client_credentials_manager = SpotifyClientCredentials(client_id=config.get('SpotifyAPI', 'ClientID'),
                                                          client_secret=config.get('SpotifyAPI', 'ClientSecret'))
    sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

    try:
        playlist = sp.playlist(playlist_id)
        playlist_name = playlist['name']
    except Exception as e:
        print(f"Error fetching playlist details: {e}")
        return []

    try:
        all_tracks = []
        offset = 0
        while True:
            tracks = sp.playlist_tracks(playlist_id, offset=offset)
            all_tracks.extend(tracks['items'])
            offset += len(tracks['items'])
            if not tracks['next']:
                break
    except Exception as e:
        print(f"Error fetching playlist tracks: {e}")
        return []

    playlist_details = []
    for item in all_tracks:
        try:
            track = item['track']
            if track:
                track_details = {
                    'Playlist Name': playlist_name,
                    'Track Name': track['name'],
                    'Artist Name(s)': ', '.join([artist['name'] for artist in track['artists']]),
                    'Album': track['album']['name']
                }
                playlist_details.append(track_details)
        except Exception as e:
            print(f"Error processing track details: {e}")

    return playlist_details

def main():
    parser = argparse.ArgumentParser(description='Convert CSV to XML playlist')
    parser.add_argument('input_files', nargs='*', help='Path(s) to the input CSV file(s) or Spotify playlist URL(s)')
    parser.add_argument('--config', help='Path to the configuration file (default: config.ini)', default=CONFIG_FILE_DEFAULT)
    parser.add_argument('--reconfigure', action='store_true', help='Reconfigure the settings')
    args = parser.parse_args()

    if args.reconfigure:
        config = prompt_config()
        with open(args.config, 'w') as configfile:
            config.write(configfile)
            print(f"Configuration file '{args.config}' reconfigured.")
        return

    if not os.path.exists(args.config):
        print(f"Configuration file '{args.config}' not found.")
        create_config = input("Do you want to create a default configuration file? (yes/no): ")
        if create_config.lower() in ['yes', 'y']:
            create_default_config(args.config)
            print(f"Default configuration file '{args.config}' created.")

    if not os.path.exists(args.config):
        config = prompt_config()
        with open(args.config, 'w') as configfile:
            config.write(configfile)
            print(f"Configuration file '{args.config}' created.")
    else:
        config = load_config(args.config)

    if args.input_files:
        for input_file in args.input_files:
            if input_file.startswith("https://open.spotify.com"):
                if not (config.get('SpotifyAPI', 'ClientID') and config.get('SpotifyAPI', 'ClientSecret')):
                    print("Error: Spotify Client ID and Client Secret are required.")
                    return
                playlist_id = input_file.split('/')[-1]
                playlist_details = get_playlist_tracks(playlist_id, config)
                if playlist_details:
                    playlist_name = playlist_details[0]['Playlist Name'].replace(' ', '_')
                    download_playlist_cover(playlist_name, playlist_id, config.get('OutputOptions', 'OutputDirectory'), config)
                    csv_output_file = f"{playlist_name}.csv"
                    with open(csv_output_file, 'w', newline='', encoding='utf-8') as csvfile:
                        fieldnames = ['Playlist Name', 'Track Name', 'Artist Name(s)', 'Album']
                        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                        writer.writeheader()
                        writer.writerows(playlist_details)

                    convert_to_xml(csv_output_file, config)
                    if config.getboolean('OutputOptions', 'DeleteSpotifyCSVs', fallback=False):
                        os.remove(csv_output_file)
                        print(f"CSV file '{csv_output_file}' deleted.")
            else:
                convert_to_xml(input_file, config)
    else:
        print("Error: Please provide input files or use the --reconfigure flag.")

if __name__ == "__main__":
    main()
