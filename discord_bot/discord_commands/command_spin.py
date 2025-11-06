import asyncio
import numpy as np
import discord
from io import BytesIO
from PIL import Image, ImageDraw
from typing import List

from discord_bot import EmbedUtil
from resources import CHAT_BG, OSRS_FONT

invalid_param_msg = ""
DELIMITER = ";"
MAX_OPT_LEN = 20
MAX_WEIGHT = 1000000
OSRS_FONT_SIZE = 20

def _validate_params(weight_fields: List[str], opt_len: int):
    """
    :Note: weight_fields are changed in this function to convert from
            str to int
    """
    global invalid_param_msg
    weights_len = len(weight_fields)

    if opt_len < 2:
        invalid_param_msg = "Add a few more options — at least 2 are required."
        return False

    if opt_len > MAX_OPT_LEN:
        invalid_param_msg = f"Woah there! That's too many options for me (I can support up to 20 options, counted {opt_len})."
        return False

    if weights_len > 0 and not weights_len == opt_len:
        invalid_param_msg = f"Number of weights ({weights_len}) do not match the number of options ({opt_len})."
        return False
    
    for idx, weight in enumerate(weight_fields):
        if not weight.isnumeric():
            invalid_param_msg = f"Invalid weight: {weight}. I only support weights between 1 and {MAX_WEIGHT} (no commas please!)"
            return False

        weight = int(weight)
        weight_fields[idx] = weight
        if weight == 0:
            invalid_param_msg = f"Ummm... I cannot divide by zero. (Got weight {weight})"
            return False
        elif weight > MAX_WEIGHT:
            invalid_param_msg = f"Oof, I can't carry this weight! My max lift is {MAX_WEIGHT}, got {weight}"
            return False
        
    return True

def _convert_weights(weights: List[int],
                     randomize_weights: bool,
                     opt_len: int) -> List[float]:
    """
    weights | randomize_weights | Result
    ------------------------------------
       []   |      True         | generate random weights
       []   |      False        | generate weights of 1
      [..]  |      True         | use weights and randomize
      [..]  |      False        | use weights as is   
    """
    weights_len = len(weights)

    if weights_len > 0:
        if randomize_weights:
            np.random.shuffle(weights)
    else:
        if randomize_weights:
            weights = np.random.rand(opt_len)
        else:
            weights = np.array([1] * opt_len)

    weights = np.divide(1, np.array(weights, dtype=float))
    weights = np.divide(weights, np.sum(weights))
    return weights


def _create_frame(bg: Image.Image, text: str) -> Image.Image:
    """Create single frame with centered text"""
    frame = bg.copy()
    draw = ImageDraw.Draw(frame)
    _, _, w, h = draw.textbbox((0, 0), text, font=OSRS_FONT(OSRS_FONT_SIZE))
    draw.text(
        ((bg.width - w) // 2, (bg.height - h) // 2), 
        text, 
        fill=(0, 0, 0), 
        font=OSRS_FONT(OSRS_FONT_SIZE)
    )
    return frame

def _save_gif(frames: List[Image.Image]) -> BytesIO:
    """Save frames as an GIF to BytesIO"""
    gif_bytes = BytesIO()
    frames[0].save(
        gif_bytes, 
        format="GIF", 
        append_images=frames[1:], 
        save_all=True, 
        duration=100, 
        loop=0
    )
    gif_bytes.seek(0)
    return gif_bytes

def _save_image(img: Image.Image) -> BytesIO:
    """Save single image to BytesIO"""
    img_bytes = BytesIO()
    img.save(img_bytes, format="PNG")
    img_bytes.seek(0)
    return img_bytes

async def _process_spin_images(interaction: discord.Interaction,
                         options: List[str],
                         weights: List[float],
                         opt_len: int):
    rng_option = np.random.choice(options, p=weights)
    options_text = "\n".join([f"> {options[i]} ({float(weights[i]) * 100.0:.2f}%)" for i in range(opt_len)])

    # Create frames for all options
    with Image.open(CHAT_BG) as bg:
        option_frames = {opt: _create_frame(bg, opt) for opt in options}
    
    frames = list(option_frames.values())
    chosen_frame = option_frames[rng_option]

    # Send spinning GIF
    gif_bytes = _save_gif(frames)
    gif_file = f"gif_{hash(str(frames))}.gif"
    gif_embed = discord.Embed(title="🎰 Spinning...").set_image(url=f"attachment://{gif_file}")
    
    await interaction.edit_original_response(
        embed=gif_embed, 
        attachments=[discord.File(gif_bytes, filename=gif_file)]
    )

    await asyncio.sleep(3)

    # Send final winner frame
    winner_bytes = _save_image(chosen_frame)
    winner_file = f"winner_{hash(str(chosen_frame))}.png"
    winner_embed = (
        discord.Embed(title="🎉 Winner!", color=discord.Color.yellow())
        .set_image(url=f"attachment:///{winner_file}")
        .add_field(name="**Options**", value=options_text, inline=False)
    )

    await interaction.edit_original_response(
        embed=winner_embed, 
        attachments=[discord.File(winner_bytes, filename=winner_file)]
    )
    
async def discord_bot_command_spin(interaction: discord.Interaction,
                                   options: str,
                                   weights: str,
                                   randomize_weights: bool):
    opt_fields = [opt.strip() for opt in options.split(DELIMITER) if opt.strip()]
    opt_len = len(opt_fields)
    weight_fields = [weight.strip() for weight in weights.split(DELIMITER) if weight.strip()]

    if not _validate_params(weight_fields, opt_len):
        await interaction.response.send_message(
            embed=EmbedUtil.error_embed(invalid_param_msg)
        )
        return

    await interaction.response.defer(thinking=True)

    weight_fields = _convert_weights(weight_fields, randomize_weights, opt_len)
    await _process_spin_images(interaction, opt_fields, weight_fields, opt_len)
