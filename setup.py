from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='SpotToBee',
    version='1.0.5',
    author='Brendan Stupik',
    author_email='spottobee@brendanstupik.anonaddy.com',
    description='Convert a CSV or Spotify playlist URL to a MusicBee smart playlist',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    url='https://github.com/BrendanStupik/SpotToBee',
    packages=find_packages(),
    install_requires=[
        'spotipy>=2.0.0',
        'pandas>=1.0.0',
        'configparser>=5.0.0'
    ],
    entry_points={
        'console_scripts': [
            'SpotToBee = SpotToBee.SpotToBee:main'
        ]
    }
)
