SpotToBee is a command-line tool for converting Spotify and other CSV playlists to an .xautopf format compatible with MusicBee. Fetching data from Spotify requires Spotify API client credentials from https://developer.spotify.com/dashboard. The tool can be used without credentials alongside https://exportify.net/. The tool can also be used to export a basic .csv of a Spotify playlist.

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

MIT License

Copyright (c) 2024 Brendan Stupik

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
