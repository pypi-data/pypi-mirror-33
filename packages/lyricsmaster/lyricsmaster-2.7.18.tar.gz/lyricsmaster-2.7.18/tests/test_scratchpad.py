import pytest
from click.testing import CliRunner

from bs4 import BeautifulSoup, Tag

from lyricsmaster import models
from lyricsmaster import cli
from lyricsmaster.providers import LyricWiki, AzLyrics, Genius, Lyrics007
from lyricsmaster.utils import TorController, normalize

# provider = Genius()
#
# test = provider.search('The Notorious B.I.G.')
pass
