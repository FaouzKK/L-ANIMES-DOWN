
from pathlib import Path

BASE_DATA_DIR = Path.home() / '.lad_dont_delete'

ANIMESAMA_LINK = 'https://anime-sama.fr'
ANIMESAMA_CATALOGUE = 'https://anime-sama.fr/catalogue'

DOWNLOAD_PATH = Path.home() / 'Downloads' / 'L-ANIME-DOWNLOADER'

MEDIA_PATH = Path(__file__).resolve().parent.parent.parent / 'media'

STYLE_PATH = Path(__file__).resolve().parent.parent.parent / 'css'


if not BASE_DATA_DIR.exists() :
    BASE_DATA_DIR.mkdir()
    
if not DOWNLOAD_PATH.exists() :
    DOWNLOAD_PATH.mkdir()
    

if __name__ == '__main__':
    print(BASE_DATA_DIR)
    print(DOWNLOAD_PATH)
    print(MEDIA_PATH)
    print(STYLE_PATH)