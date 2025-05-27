import pathlib
from PIL import ImageFont

__DIR_PATH = str(pathlib.Path(__file__).parent.absolute())

CHAT_BG = __DIR_PATH + "/background.png"
OSRS_FONT = lambda size: ImageFont.truetype(__DIR_PATH + "/runescape_uf.ttf", size)
