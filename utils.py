import math

import discord
from discord import TextChannel

from config import config
from enums import EmojiEnum


async def discord_try_fetch_message(channel: TextChannel, message_id: int):
    try:
        return await channel.fetch_message(message_id)
    except discord.NotFound:
        return None


async def discord_close_response(interaction: discord.Interaction):
    await interaction.response.defer(ephemeral=True)
    await interaction.delete_original_response()


async def discord_resp_send_msg(interaction: discord.Interaction, message: str, ephemeral: bool = True,
                                delete_after=None):
    if delete_after is None:
        delete_after = config.MESSAGE_DEFAULT_DELETE_AFTER_SHORT

    await interaction.response.send_message(content=message, ephemeral=ephemeral,
                                            delete_after=delete_after)  # type: ignore


def generate_health_bar(current_health:int, max_health:int):
    max_bar = 10
    green_block = math.floor(current_health / max_health * 10)
    result = f"`"
    for i in range(green_block):
        result += f"{EmojiEnum.GREEN_BLOCK.value}"
    for i in range(max_bar - green_block):
        result += f"{EmojiEnum.RED_BLOCK.value}"
    result += f"`"
    return result



def format_large_number(num):
    if abs(num) >= 1_000_000:
        return f"{num / 1_000_000:,.1f}M"
    elif abs(num) >= 1_000:
        return f"{num / 1_000:,.1f}k"
    else:
        return str(num)


def reduce_int_ab_non_zero(a: int, b: int):
    return max(a - b, 0)

# TL Shifter
def time_to_seconds(time_str: str) -> int:
    """Convert time string (MM:SS or SS) to total seconds."""
    if ':' in time_str:
        m, s = map(int, time_str.split(':', 1))
        return m * 60 + s
    return int(time_str)

def format_time(seconds: int) -> str:
    """Convert total seconds to MM:SS format."""
    m, s = divmod(seconds, 60)
    return f"{m}:{s:02d}"
