# Enum
from enum import Enum

import discord

from config import config


class ChannelEnum(Enum):
    CATEGORY = {"type": "CATEGORY", "name": config.CATEGORY_CHANNEL_NAME}
    REPORT = {"type": "REPORT", "name": config.REPORT_CHANNEL_NAME}
    BOSS1 = {"type": "BOSS1", "name": config.BOSS1_CHANNEL_NAME}
    BOSS2 = {"type": "BOSS2", "name": config.BOSS2_CHANNEL_NAME}
    BOSS3 = {"type": "BOSS3", "name": config.BOSS3_CHANNEL_NAME}
    BOSS4 = {"type": "BOSS4", "name": config.BOSS4_CHANNEL_NAME}
    BOSS5 = {"type": "BOSS5", "name": config.BOSS5_CHANNEL_NAME}
    TL_SHIFTER = {"type": "TL_SHIFTER", "name": config.TL_SHIFTER_CHANNEL_NAME}


class AttackTypeEnum(Enum):
    PATK = "🥊"
    MATK = "📘"
    CARRY = "💼"


# Enums for better readability
class EmojiEnum(Enum):
    PATK = "🥊"
    MATK = "📘"
    CARRY = "💼"
    CANCEL = "⛔"
    DONE = "✅"
    BOOK = "⚔️"
    ENTRY = "📝"
    FINISH = "🏁"
    STAR = "🌟"
    YES = "✔"
    NO = "❌"
    GREEN_BLOCK = "🟩"
    RED_BLOCK = "🟥"


class ButtonStyle:
    PRIMARY = discord.ButtonStyle.primary
    GREEN = discord.ButtonStyle.green
    RED = discord.ButtonStyle.red
    BLURPLE = discord.ButtonStyle.blurple