# SpotToBee
SpotToBee is a command-line tool for converting Spotify and other CSV playlists to an .xautopf format compatible with MusicBee. Fetching data from Spotify requires Spotify Client Credentials from https://developer.spotify.com/dashboard. The tool can be used without credentials alongside https://exportify.net/. The tool can also be used to export a basic .csv of a Spotify playlist.

## Installation

    pip install SpotToBee

Running SpotToBee will automatically create a config file in its run directory. This can be manually reset by passing the --reconfigure argument.

## Usage/Examples

    SpotToBee path/to/playlist.csv

    SpotToBee https://open.spotify.com/playlist/37i9dQZF1DX9wa6XirBPv8

    SpotToBee path/to/playlist.csv --config path/to/config.ini

    SpotToBee --reconfigure

## Configuration Options

    outputdirectory -  location of output directory (= /path/to/config.ini)

    field - set your release type field, (= any)

    includecompilation - include compilations (= True/False)

    includelive - include live albums (= True/False)

    includebroadcast - include live albums (= True/False)

    includesingle - include singles (= True/False)

    includesoundtrack - include soundtracks (= True/False)

    includedemo - include demos (= True/False)

    includeep - include EPs (= True/False)

## License

[MIT](https://choosealicense.com/licenses/mit/)
