import discord
from discord import TextChannel

from config import config


async def try_fetch_message(channel: TextChannel, message_id: int):
    try:
        return await channel.fetch_message(message_id)
    except discord.NotFound:
        return None


def format_large_number(num):
    if abs(num) >= 1_000_000:
        return f"{num / 1_000_000:,.2f}M"
    elif abs(num) >= 1_000:
        return f"{num / 1_000:,.2f}k"
    else:
        return str(num)


async def response_send_message(interaction: discord.interactions.Interaction, message: str, ephemeral: bool = True,
                                delete_after=None):
    if delete_after is None:
        delete_after = config['MESSAGE_DEFAULT_DELETE_AFTER']

    await interaction.response.send_message(content=message, ephemeral=ephemeral,
                                            delete_after=delete_after)  # type: ignore
