import pathlib
import os
from PIL import ImageFont

__DIR_PATH = str(pathlib.Path(__file__).parent.absolute())

CHAT_BG = os.path.join(__DIR_PATH, "background.png")
def OSRS_FONT(size, **kwargs): return ImageFont.truetype(__DIR_PATH + "/runescape_uf.ttf", size, **kwargs)
