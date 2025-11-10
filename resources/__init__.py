from pathlib import Path
from PIL import ImageFont

# Base directory for all resources
DIR_PATH = Path(__file__).resolve().parent

# Resource file paths
CHAT_BG = DIR_PATH / "background.png"
RANK_ICONS_JSON_PATH = DIR_PATH / "rank_icons.json"

def OSRS_FONT(size: int, **kwargs) -> ImageFont.FreeTypeFont:
    """Load the RuneScape font at the given size."""
    font_path = DIR_PATH / "runescape_uf.ttf"
    return ImageFont.truetype(str(font_path), size, **kwargs)