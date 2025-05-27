import asyncio
import random as rand
import numpy as np
from io import BytesIO
from PIL import Image, ImageDraw
from discord import Embed, File
from discord_bot.discord_bot_util import err_embed
from util import RESPONSE_ERR, RESPONSE_OK, debug_print
from resources import CHAT_BG, OSRS_FONT

RANDOM_WEIGHTS_OPTIONS = ['True']
MAX_OPT_CHAR_LEN = 20
MAX_OPTIONS_LEN = 20
MAX_WEIGHT = 1_000_000
OSRS_FONT_SIZE = 20

async def spin_cb(_, ctx, options, weights=None, randomize_weights=None, shuffle_options=None, options_detail=None):
    val = validate_params(options, weights, randomize_weights, shuffle_options, options_detail)
    if not val:
        await ctx.send(embed=err_embed(val.err), ephemeral=True)
        return

    opt_fields = list(map(str.strip, options.strip().split(",")))
    opt_len = len(opt_fields)
    weights = convert_param_weights(opt_len, weights, randomize_weights)

    if shuffle_options:
        rand.shuffle(opt_fields)

    await process_spin_images(ctx, opt_fields, weights, opt_len, options_detail)

def validate_params(options, weights, randomize_weights, shuffle_options, options_details):
    if options is None:
        return RESPONSE_ERR("No options are provided")
    
    if randomize_weights and randomize_weights not in RANDOM_WEIGHTS_OPTIONS:
        return RESPONSE_ERR(f"Value for Randomized Weights Enabled [{randomize_weights}] is not True")
    
    if shuffle_options and not shuffle_options == "True":
        return RESPONSE_ERR(f"Value for Shuffle Options Enabled [{shuffle_options}] is not True")
    
    if options_details and not options_details == "True":
        return RESPONSE_ERR(f"Value for Option Details Enabled [{options_details}] is not True")
        
    opts_fields = options.strip().split(",")
    opts_len = len(opts_fields)

    if opts_len < 2:
        return RESPONSE_ERR(f"Number of options must be greater than 2")

    if opts_len > MAX_OPTIONS_LEN:
        return RESPONSE_ERR(f"Number of options '{opts_len}' exceeds {MAX_OPTIONS_LEN} options limit")

    if weights:
        weights_fields = weights.strip().split(",")
        weights_len = len(weights_fields)
        if weights_len != opts_len:
            return RESPONSE_ERR(f"Number of weights '{weights_len}' do not match number of options '{opts_len}'") 
    
    for idx in range(opts_len):
        option = opts_fields[idx].strip()

        if len(option) > MAX_OPT_CHAR_LEN:
            return RESPONSE_ERR(f"Option [{option}] exceeds {MAX_OPT_CHAR_LEN} characters limit")
        
        if weights:
            weight = weights_fields[idx].strip()
            try:
                weight = int(weight)
                if not isinstance(weight, int) or weight < 1 or weight > MAX_WEIGHT:
                    raise ValueError
            except ValueError:
                return RESPONSE_ERR(f"The entered weight [{weight}] is invalid. The weight must be an integer in the range 1..1000000.")
    
    return RESPONSE_OK

def convert_param_weights(opt_len, weights, randomize_weights):
    """
    weights  | randomize_weights | Result
    ----------------------------------------
    None     |     True          | generate random weights
    None     |     False         | generate normalized weights of 1 per option
    not None |     True          | use weights and normalize, shuffle
    not None |     False         | use weights and normalize, no shuffle  
    """
    if weights is None:
        if randomize_weights:
            weights = np.random.rand(opt_len)
        else:
            weights = np.array([1] * opt_len)
    else:
        weights = weights.replace(" ", "").split(",")
        weights = np.divide(1, np.array(weights, dtype=int))

        if randomize_weights:
            np.random.shuffle(weights)

    weights = np.divide(weights, np.sum(weights))
    return weights

def get_rng_option(options, weights, opts_len):
    rng = rand.random()
    total = 0

    debug_print(f"RNG: {rng}")

    for idx in range(opts_len):
        option = options[idx]
        weight = weights[idx]
        total += weight
        if rng <= total:
            return option

async def process_spin_images(ctx, options, weights, opts_len, show_options_detail):
    rng_option = get_rng_option(options, weights, opts_len)
    option_to_frame = dict()

    with Image.open(CHAT_BG) as bg:
        width = bg.width
        height = bg.height

        for option in options:
            cp = bg.copy()
            draw = ImageDraw.Draw(cp)
            _,_,w,h = draw.textbbox((0,0), option, font=OSRS_FONT(OSRS_FONT_SIZE))
            draw.text(((width-w)//2, (height-h)//2), option, fill=(0,0,0), font=OSRS_FONT(OSRS_FONT_SIZE))
            option_to_frame[option] = cp
    
    frames = list(option_to_frame.values())
    frame_one = frames[0]
    chosen_option_frame = option_to_frame[rng_option]

    with BytesIO() as gif_bytes:
        frame_one.save(gif_bytes, format="GIF", append_images=frames[1:], save_all=True, duration=100, loop=0)
        gif_bytes.seek(0)
        gif_file = f"gif_{hash(str(frames))}.gif"
        gif_embed = Embed().set_image(url=f"attachment://{gif_file}")
        message = await ctx.send(embed=gif_embed, file=File(gif_bytes, filename=gif_file))
        
    await asyncio.sleep(3)
    debug_print(rng_option)

    with BytesIO() as winner_bytes:
        chosen_option_frame.save(winner_bytes, format="PNG")
        winner_bytes.seek(0)
        winner_frame_file = f"winner_{hash(str(chosen_option_frame))}.png"
        winner_embed = Embed().set_image(url=f"attachment://{winner_frame_file}")
        embeds = [winner_embed]
        if show_options_detail == "True":
            rng_options_embed = Embed().add_field(name="**Options**", 
                                                  value="\n".join([f"> {options[i]} ({float(weights[i]) * 100.0:.2f}%)" for i in range(opts_len)]))
            embeds.append(rng_options_embed)
        last_message = await ctx.fetch_message(message.id)
        await last_message.edit(embeds=embeds, attachments=[File(winner_bytes, filename=winner_frame_file)])
