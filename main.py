import logging
import re
from typing import List

import discord
from discord.abc import GuildChannel
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput

import enums
import utils
from repository import *
from enums import *

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

NEW_LINE = "\n"

TL_SHIFTER_CHANNEL = {}

# Precompile regex patterns for better performance
SPACE_PATTERN = re.compile(r'[ \t　]+')
NON_DIGIT = re.compile(r'\D')

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)


class ButtonStyle:
    PRIMARY = discord.ButtonStyle.primary
    GREEN = discord.ButtonStyle.green
    RED = discord.ButtonStyle.red
    BLURPLE = discord.ButtonStyle.blurple


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    for guild in bot.guilds:
        await setup_channel(guild)


@bot.event
async def on_message(message):
    # Early exit for bot messages
    if message.author == bot.user:
        return

    # Early exit for non-target channels
    if message.channel.id not in TL_SHIFTER_CHANNEL:
        await bot.process_commands(message)
        return

    content = message.content
    lines = content.split('\n', 1)  # Split only once if possible
    if not lines:
        await bot.process_commands(message)
        return

    # Process first line
    first_line, *rest = lines[0].split('\n')  # Handle potential multi-split
    first_segment = SPACE_PATTERN.split(first_line.strip(), 1)[0]
    second_str = NON_DIGIT.sub('', first_segment)

    if not second_str.isdigit():
        await bot.process_commands(message)
        return

    second = int(second_str)
    if second > 90:
        await bot.process_commands(message)
        return

    sec_reduction = 90 - second
    result_lines = [
        f"TL Shift for {second}s",
        "```powershell"
    ]

    # Process remaining lines
    for line in (lines[1].split('\n') if len(lines) > 1 else []):
        parts = SPACE_PATTERN.split(line.strip(), 1)
        if len(parts) < 2:
            continue

        time_str, desc = parts
        try:
            parsed_time = utils.time_to_seconds(time_str)
        except ValueError:
            continue

        result_time = parsed_time - sec_reduction
        if result_time <= 0:
            continue

        result_lines.append(f"{utils.format_time(result_time)}  {desc.strip()}")

    # Only send response if we have valid entries
    if len(result_lines) > 2:
        result_lines.append("```")
        await message.reply(NEW_LINE.join(result_lines))


@bot.event
async def on_guild_join(guild):
    await setup_channel(guild)


async def setup_channel(guild):
    print(f'Setup for guild {guild.id} - {guild.name}')
    guild_id = guild.id
    g_repo = GuildRepository()
    guild_db = g_repo.get_by_guild_id(guild_id=guild_id)

    if guild_db is None:
        guild_db = g_repo.insert_guild(Guild(GuildId=guild.id, GuildName=guild.name))

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
    }

    overwrites_tl_shifter = {
        guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }

    gc_repo = GuildChannelRepository()
    guild_channel = gc_repo.get_all_by_guild_id(guild_id=guild_db.GuildId)

    category_channel = None
    processed_channel = []

    # Channel Setup
    for enum in ChannelEnum:
        channel_data = next((channel for channel in guild_channel if channel.ChannelType == enum), None)
        # Assume no Channel Exist for specific enum
        if channel_data is None:
            local_overwrites = overwrites
            if enum == ChannelEnum.TL_SHIFTER:
                local_overwrites = overwrites_tl_shifter

            if enum == ChannelEnum.CATEGORY:
                channel = await guild.create_category(
                    name=ChannelEnum.CATEGORY.value['name'],
                    overwrites=overwrites
                )
                category_channel = channel
            else:
                channel = await guild.create_text_channel(
                    name=enum.value['name'],
                    category=category_channel,
                    overwrites=local_overwrites
                )

            gc_repo.insert_channel(Channel(ChannelId=channel.id, GuildId=guild_db.GuildId, ChannelType=enum))
            processed_channel.append((enum, channel))
        else:
            channel = guild.get_channel(channel_data.ChannelId)
            processed_channel.append((enum, channel))

        # For TL Shifting watcher
        if enum == ChannelEnum.TL_SHIFTER and channel:
            TL_SHIFTER_CHANNEL[channel.id] = None

    await setup_message(guild, channels=processed_channel)


async def setup_message(guild, channels: list[tuple[ChannelEnum, GuildChannel]]):
    # Master CB Data
    clan_battle_period_repository = ClanBattlePeriodRepository()
    clan_battle_period = clan_battle_period_repository.get_current_running_clan_battle_period()

    if clan_battle_period is None:
        print("Need setup on Database !")
        return

    for enum, channel in channels:
        if "boss" in enum.name.lower():
            message = await check_or_generate_channel_message(guild, channel_id=channel.id)
            boss_id = getattr(clan_battle_period, f"{enum.value['type'].capitalize()}Id")
            await generate_clan_battle_boss_entry(message_id=message.id, boss_id=boss_id)
            await refresh_boss_message(message)


# Book Button
class BookButton(Button):
    def __init__(self):
        super().__init__(label=EmojiEnum.BOOK.name.capitalize(),
                         style=discord.ButtonStyle.primary,
                         emoji=EmojiEnum.BOOK.value,
                         row=0)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild_id
        message_id = interaction.message.id
        if book_check_by_guild_id(guild_id=interaction.guild_id, player_id=user_id):
            await utils.discord_resp_send_msg(interaction=interaction, message="## Already booked !")
            return

        cb_overall_repo = ClanBattleOverallEntryRepository()
        entry_count = cb_overall_repo.get_entry_count_by_guild_id_and_player_id(guild_id=guild_id, player_id=user_id)

        disable = entry_count == 3

        view = View(timeout=None)
        view.add_item(BookPatkButton(message_id=message_id, disable=disable))
        view.add_item(BookMatkButton(message_id=message_id, disable=disable))
        view.add_item(ConfirmationNoCancelButton(emoji_param=EmojiEnum.CANCEL))

        # generate Leftover ?
        leftover = cb_overall_repo.get_leftover_by_guild_id_and_player_id(guild_id=guild_id, player_id=user_id)
        for left_data in leftover:
            view.add_item(BookLeftoverButton(leftover=left_data, message_id=message_id))

        await interaction.response.send_message(
            f"## Choose your Entry Type [{utils.reduce_int_ab_non_zero(a=3, b=entry_count)}/3]", view=view,
            ephemeral=True, delete_after=15)


# Cancel Button
class CancelButton(Button):
    def __init__(self):
        super().__init__(label=EmojiEnum.CANCEL.name.capitalize(),
                         style=discord.ButtonStyle.danger,
                         emoji=EmojiEnum.CANCEL.value,
                         row=0)

    async def callback(self, interaction: discord.Interaction):
        cb_book_repository = ClanBattleBossBookRepository()
        x_user = cb_book_repository.get_one_by_message_id_and_player_id(
            message_id=interaction.message.id,
            player_id=interaction.user.id)

        if x_user:
            cb_book_repository.delete_book_by_id(clan_battle_boss_book_id=x_user.ClanBattleBossBookId)
            await refresh_boss_message(interaction.message)

        await interaction.response.defer(ephemeral=True)


# Entry Button
class EntryButton(Button):
    def __init__(self):
        super().__init__(label=EmojiEnum.ENTRY.name.capitalize(),
                         style=discord.ButtonStyle.primary,
                         emoji=EmojiEnum.ENTRY.value,
                         row=1)

    async def callback(self, interaction: discord.Interaction):
        if not book_check_by_message_id(message_id=interaction.message.id, player_id=interaction.user.id):
            await utils.discord_resp_send_msg(interaction=interaction, message="## Not Booked")

        modal = EntryInputModal()
        await interaction.response.send_modal(modal)


# Entry Input
class EntryInputModal(Modal, title="Entry Input"):
    # Define a text input
    user_input = TextInput(
        label="Entry Damage",
        placeholder="123456789",
        style=discord.TextStyle.short,
        required=True,
        min_length=1,
        max_length=10
    )

    async def on_submit(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        message_id = interaction.message.id
        # Handle the submitted input
        if not self.user_input.value.isdigit():
            await utils.discord_resp_send_msg(interaction=interaction, message=f"## Number only !")
            return
        if int(self.user_input.value) < 1:
            await utils.discord_resp_send_msg(interaction=interaction, message=f"## Must be higher than 0 !")
            return

        # Update damage
        cb_book_repository = ClanBattleBossBookRepository()
        book = cb_book_repository.get_one_by_message_id_and_player_id(message_id=message_id, player_id=user_id)
        damage = int(self.user_input.value)
        cb_book_repository.update_damage_boss_book_by_id(clan_battle_boss_book_id=book.ClanBattleBossEntryId,
                                                         damage=damage)

        # Refresh Messages
        message = await utils.discord_try_fetch_message(channel=interaction.channel, message_id=message_id)
        if message:
            await refresh_boss_message(message)

        await interaction.response.defer(ephemeral=True)


# Done Button
class DoneButton(Button):
    def __init__(self):
        super().__init__(label=EmojiEnum.DONE.name.capitalize(),
                         style=discord.ButtonStyle.green,
                         emoji=EmojiEnum.DONE.value,
                         row=1)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        message_id = interaction.message.id
        if not book_check_by_message_id(message_id=message_id, player_id=user_id):
            await utils.discord_resp_send_msg(interaction=interaction, message="## Not booked")
            return

        cb_book_repository = ClanBattleBossBookRepository()
        boss_book = cb_book_repository.get_one_by_message_id_and_player_id(message_id=message_id,
                                                                           player_id=user_id)
        if boss_book.Damage is None:
            await utils.discord_resp_send_msg(interaction=interaction, message="## Input entry first !")
            return

        message_id = interaction.message.id
        view = View(timeout=None)
        view.add_item(DoneOkButton(message_id=message_id))
        view.add_item(ConfirmationNoCancelButton(emoji_param=EmojiEnum.NO))

        await interaction.response.send_message(content=f"## Are you sure want to Mark your entry as Done ?",
                                                view=view, ephemeral=True,
                                                delete_after=config.MESSAGE_DEFAULT_DELETE_AFTER_LONG)


# Done Ok Confirm Button
class DoneOkButton(Button):
    def __init__(self, message_id: int):
        super().__init__(label=EmojiEnum.DONE.name.capitalize(),
                         style=discord.ButtonStyle.green,
                         emoji=EmojiEnum.DONE.value,
                         row=0)
        self.message_id = message_id

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        display_name = interaction.user.display_name
        message_id = self.message_id
        guild_id = interaction.guild_id

        cb_book_repository = ClanBattleBossBookRepository()
        boss_book = cb_book_repository.get_one_by_message_id_and_player_id(message_id=message_id,
                                                                           player_id=user_id)

        # Get CB Entry
        cb_boss_repo = ClanBattleBossEntryRepository()
        boss_entry = cb_boss_repo.get_last_by_message_id(message_id=message_id)

        cb_period_repo = ClanBattlePeriodRepository()
        period = cb_period_repo.get_current_running_clan_battle_period()

        cb_book_repository.delete_book_by_id(clan_battle_boss_book_id=boss_book.ClanBattleBossBookId)

        # Prepare insert into overall Entry
        cb_overall_repository = ClanBattleOverallEntryRepository()
        overall = cb_overall_repository.insert(
            cb_overall_entry=ClanBattleOverallEntry(
                GuildId=guild_id,
                ClanBattlePeriodId=period.ClanBattlePeriodId,
                ClanBattleBossId=boss_entry.ClanBattleBossId,
                PlayerId=user_id,
                PlayerName=display_name,
                Round=boss_entry.Round,
                AttackType=boss_book.AttackType,
                Damage=boss_book.Damage
            )
        )

        if not boss_book.ClanBattleOverallEntryId is None:
            cb_overall_repository.update_overall_link(cb_overall_entry_id=boss_book.ClanBattleOverallEntryId,
                                                      overall_parent_entry_id=overall.ClanBattleOverallEntryId)

        # Update Boss Entry
        cb_boss_repo.update_on_attack(clan_battle_boss_entry_id=boss_entry.ClanBattleBossEntryId,
                                      current_health=utils.reduce_int_ab_non_zero(boss_entry.CurrentHealth,
                                                                                  boss_book.Damage))

        # Refresh Messages
        message = await utils.discord_try_fetch_message(channel=interaction.channel, message_id=message_id)
        if message:
            await refresh_boss_message(message=message)

        await utils.discord_close_response(interaction=interaction)


# Dead Button
class DeadButton(Button):
    def __init__(self):
        super().__init__(label="Dead",
                         style=discord.ButtonStyle.gray,
                         emoji=EmojiEnum.FINISH.value,
                         row=1)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        message_id = interaction.message.id
        if not book_check_by_message_id(message_id=message_id, player_id=user_id):
            await utils.discord_resp_send_msg(interaction=interaction, message="## Not Booked")

        cb_book_repository = ClanBattleBossBookRepository()
        boss_book = cb_book_repository.get_one_by_message_id_and_player_id(message_id=message_id,
                                                                           player_id=user_id)
        if boss_book.Damage is None:
            await utils.discord_resp_send_msg(interaction=interaction, message="## Input entry first !")
            return

        # Fresh Entry
        if boss_book.LeftoverTime is None:
            modal = LeftoverInputModal()
            await interaction.response.send_modal(modal)
        # Carry over
        else:
            view = View(timeout=None)
            view.add_item(DeadOkButton(message_id=message_id, leftover_time=boss_book.LeftoverTime))
            view.add_item(ConfirmationNoCancelButton(emoji_param=EmojiEnum.NO))

            await interaction.response.send_message(content=f"## Are you sure want to Mark your entry as Boss Kill ?",
                                                    view=view, ephemeral=True,
                                                    delete_after=config.MESSAGE_DEFAULT_DELETE_AFTER_LONG)


# Leftover Modal
class LeftoverInputModal(Modal, title="Leftover Input"):
    def __init__(self):
        super().__init__()

    # Define a text input
    user_input = TextInput(
        label="Leftover Time (in second)",
        placeholder="20",
        style=discord.TextStyle.short,
        required=True,
        min_length=1,
        max_length=2
    )

    async def on_submit(self, interaction: discord.Interaction):
        message_id = interaction.message.id
        # Handle the submitted input
        if not self.user_input.value.isdigit():
            await utils.discord_resp_send_msg(interaction=interaction, message=f"## Number only !")
            return

        leftover_time = int(self.user_input.value)

        if leftover_time < 20 or leftover_time > 90:
            await utils.discord_resp_send_msg(interaction=interaction, message=f"## Must between 20 and 90s")
            return

        view = View(timeout=None)
        view.add_item(DeadOkButton(message_id=message_id, leftover_time=leftover_time))
        view.add_item(ConfirmationNoCancelButton(emoji_param=EmojiEnum.NO))

        await interaction.response.send_message(content=f"## Are you sure want to Mark your entry as Boss Kill ?",
                                                view=view, ephemeral=True,
                                                delete_after=config.MESSAGE_DEFAULT_DELETE_AFTER_LONG)


# Done Ok Confirm Button
class DeadOkButton(Button):
    def __init__(self, message_id: int, leftover_time: int):
        super().__init__(label=EmojiEnum.DONE.name.capitalize(),
                         style=discord.ButtonStyle.green,
                         emoji=EmojiEnum.DONE.value,
                         row=0)
        self.message_id = message_id
        self.leftover_time = leftover_time

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        display_name = interaction.user.display_name
        message_id = self.message_id
        guild_id = interaction.guild_id

        leftover_time = self.leftover_time

        cb_book_repository = ClanBattleBossBookRepository()
        boss_book = cb_book_repository.get_one_by_message_id_and_player_id(message_id=message_id,
                                                                           player_id=user_id)

        # Get CB Entry
        cb_boss_repo = ClanBattleBossEntryRepository()
        boss_entry = cb_boss_repo.get_last_by_message_id(message_id=message_id)

        cb_period_repo = ClanBattlePeriodRepository()
        period = cb_period_repo.get_current_running_clan_battle_period()

        cb_book_repository.delete_book_by_id(clan_battle_boss_book_id=boss_book.ClanBattleBossBookId)

        # Prepare insert into overall Entry
        cb_overall_repository = ClanBattleOverallEntryRepository()
        overall = cb_overall_repository.insert(
            cb_overall_entry=ClanBattleOverallEntry(
                GuildId=guild_id,
                ClanBattlePeriodId=period.ClanBattlePeriodId,
                ClanBattleBossId=boss_entry.ClanBattleBossId,
                PlayerId=user_id,
                PlayerName=display_name,
                Round=boss_entry.Round,
                AttackType=boss_book.AttackType,
                Damage=boss_book.Damage,
                LeftoverTime=None if boss_book.AttackType == AttackTypeEnum.CARRY else leftover_time
            )
        )

        # Update Boss Entry
        cb_boss_repo.update_on_attack(clan_battle_boss_entry_id=boss_entry.ClanBattleBossEntryId,
                                      current_health=utils.reduce_int_ab_non_zero(boss_entry.CurrentHealth,
                                                                                  boss_book.Damage))

        if not boss_book.ClanBattleOverallEntryId is None:
            cb_overall_repository.update_overall_link(cb_overall_entry_id=boss_book.ClanBattleOverallEntryId,
                                                      overall_parent_entry_id=overall.ClanBattleOverallEntryId)

        await utils.discord_close_response(interaction=interaction)

        # Refresh Messages
        message = await utils.discord_try_fetch_message(channel=interaction.channel, message_id=message_id)
        if message:
            await generate_next_clan_battle_boss_entry(interaction=interaction, boss_id=boss_entry.ClanBattleBossId,
                                                       message_id=message_id,
                                                       attack_type=boss_book.AttackType, leftover_time=leftover_time)


def generate_done_attack_list(datas: List[ClanBattleOverallEntry]) -> str:
    lines = [f"========== {EmojiEnum.DONE.value} Done List =========="]
    for data in datas:
        line = f"{NEW_LINE}{data.AttackType.value} {f"[{utils.format_large_number(data.Damage)}] " if data.Damage else ''}: {data.PlayerName}"
        if data.LeftoverTime:
            line += f"{NEW_LINE} ┗━ {EmojiEnum.STAR.value} ({data.LeftoverTime}s)"

        lines.append(line)

    return f"```powershell{NEW_LINE}" + "".join(lines) + "```"


def generate_book_list(datas: List[ClanBattleBossBook]) -> str:
    lines = [f"========== {EmojiEnum.ENTRY.value} Book List =========="]
    for data in datas:
        line = f"{NEW_LINE}{data.AttackType.value}{f"({data.LeftoverTime}s)" if data.LeftoverTime else ''} {f"[{utils.format_large_number(data.Damage)}] " if data.Damage else ''}: {data.PlayerName}"
        lines.append(line)

    return f"```powershell{NEW_LINE}" + "".join(lines) + "```"


# PATK Button
class BookPatkButton(Button):
    def __init__(self, message_id: int, disable: bool):
        self.local_emoji = EmojiEnum.PATK
        self.attack_type = AttackTypeEnum.PATK
        self.message_id = message_id

        super().__init__(label=self.local_emoji.name,
                         style=discord.ButtonStyle.success,
                         emoji=self.local_emoji.value,
                         disabled=disable,
                         row=0)
        self.message_id = message_id

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        display_name = interaction.user.display_name

        cb_book_repository = ClanBattleBossBookRepository()
        x_user = cb_book_repository.check_book_count_by_player_id(guild_id=interaction.guild_id, player_id=user_id)
        if x_user > 0:
            await utils.discord_close_response(interaction=interaction)
            return

        message = await utils.discord_try_fetch_message(channel=interaction.channel, message_id=self.message_id)

        # Insert to Db first !
        cb_entry_repository = ClanBattleBossEntryRepository()
        cb_boss_entry = cb_entry_repository.get_last_by_message_id(message_id=message.id)

        cb_book = ClanBattleBossBook(
            ClanBattleBossEntryId=cb_boss_entry.ClanBattleBossEntryId,
            PlayerId=user_id,
            PlayerName=display_name,
            AttackType=self.attack_type
        )

        cb_book_repository.insert_boss_book_entry(clan_battle_boss_book=cb_book)

        await refresh_boss_message(message)
        await utils.discord_close_response(interaction=interaction)
        await interaction.channel.send(content=f"{display_name} {self.local_emoji.value} added to book list.",
                                       delete_after=config.MESSAGE_DEFAULT_DELETE_AFTER_SHORT)


# MATK Button
class BookMatkButton(Button):
    def __init__(self, message_id: int, disable: bool):
        self.local_emoji = EmojiEnum.MATK
        self.attack_type = AttackTypeEnum.MATK
        self.message_id = message_id

        super().__init__(label=self.local_emoji.name,
                         style=discord.ButtonStyle.blurple,
                         emoji=self.local_emoji.value,
                         disabled=disable,
                         row=0)
        self.message_id = message_id

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        display_name = interaction.user.display_name

        cb_book_repository = ClanBattleBossBookRepository()
        x_user = cb_book_repository.check_book_count_by_player_id(guild_id=interaction.guild_id, player_id=user_id)
        if x_user > 0:
            await utils.discord_close_response(interaction=interaction)
            return

        message = await utils.discord_try_fetch_message(channel=interaction.channel, message_id=self.message_id)

        # Insert to Db first !
        cb_entry_repository = ClanBattleBossEntryRepository()
        cb_boss_entry = cb_entry_repository.get_last_by_message_id(message_id=message.id)

        cb_book = ClanBattleBossBook(
            ClanBattleBossEntryId=cb_boss_entry.ClanBattleBossEntryId,
            PlayerId=user_id,
            PlayerName=display_name,
            AttackType=self.attack_type
        )

        cb_book_repository.insert_boss_book_entry(clan_battle_boss_book=cb_book)

        await refresh_boss_message(message)
        await utils.discord_close_response(interaction=interaction)
        await interaction.channel.send(content=f"{display_name} {self.local_emoji.value} added to book list.",
                                       delete_after=config.MESSAGE_DEFAULT_DELETE_AFTER_SHORT)


# Leftover Button
class BookLeftoverButton(Button):
    def __init__(self, leftover: ClanBattleLeftover, message_id: int):
        self.local_emoji = EmojiEnum.CARRY
        self.attack_type = AttackTypeEnum.CARRY
        self.message_id = message_id
        self.parent_overall_id = leftover.ClanBattleOverallEntryId
        self.label_string = f"{leftover.AttackType.value} {leftover.LeftoverTime}s ({leftover.ClanBattleBossName})"
        self.leftover_time = leftover.LeftoverTime

        super().__init__(label=self.label_string,
                         style=discord.ButtonStyle.blurple,
                         emoji=self.local_emoji.value,
                         row=1)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        username = interaction.user.display_name
        cb_book_repository = ClanBattleBossBookRepository()
        x_user = cb_book_repository.check_book_count_by_player_id(guild_id=interaction.guild_id, player_id=user_id)
        if x_user > 0:
            await utils.discord_close_response(interaction=interaction)
            return

        message = await utils.discord_try_fetch_message(channel=interaction.channel, message_id=self.message_id)

        # Insert to Db first !
        cb_entry_repository = ClanBattleBossEntryRepository()
        cb_boss_entry = cb_entry_repository.get_last_by_message_id(message_id=message.id)

        cb_book = ClanBattleBossBook(
            ClanBattleBossEntryId=cb_boss_entry.ClanBattleBossEntryId,
            PlayerId=user_id,
            PlayerName=username,
            AttackType=self.attack_type,
            LeftoverTime=self.leftover_time,
            ClanBattleOverallEntryId=self.parent_overall_id
        )

        cb_book_repository.insert_boss_book_entry(clan_battle_boss_book=cb_book)

        await refresh_boss_message(message)
        await utils.discord_close_response(interaction=interaction)
        await interaction.channel.send(content=f"{username} {self.local_emoji.value} added to book list.",
                                       delete_after=config.MESSAGE_DEFAULT_DELETE_AFTER_SHORT)


# Universal Cancel / No Button
class ConfirmationNoCancelButton(Button):
    def __init__(self, emoji_param: enums.EmojiEnum):
        super().__init__(label=emoji_param.name.capitalize(),
                         style=discord.ButtonStyle.red,
                         emoji=emoji_param.value,
                         row=0)

    async def callback(self, interaction: discord.Interaction):
        await utils.discord_close_response(interaction=interaction)


def create_header_embed(cb_boss_entry: ClanBattleBossEntry, include_image: bool = True):
    embed = discord.Embed(
        title=f"{cb_boss_entry.Name} (Round {cb_boss_entry.Round})",
        description=f"# HP : {utils.format_large_number(cb_boss_entry.CurrentHealth)} / {utils.format_large_number(cb_boss_entry.MaxHealth)}",
        color=discord.Color.red()
    )
    if include_image:
        embed.set_image(url=cb_boss_entry.Image)
    return embed


def create_done_embed(list_cb_overall_entry: List[ClanBattleOverallEntry]):
    embed = discord.Embed(
        title="",
        description=generate_done_attack_list(list_cb_overall_entry),
        color=discord.Color.green(),
    )
    return embed


def create_book_embed(list_boss_cb_player_entries: List[ClanBattleBossBook]):
    embed = discord.Embed(
        title="",
        description=generate_book_list(list_boss_cb_player_entries),
        color=discord.Color.blue(),
    )
    return embed


async def refresh_boss_message(message):
    embeds = []
    message_id = message.id
    guild_id = message.guild.id

    # Header
    cb_entry_repository = ClanBattleBossEntryRepository()
    clan_battle_boss_entry = cb_entry_repository.get_last_by_message_id(message_id=message_id)

    embeds.append(create_header_embed(clan_battle_boss_entry))

    # Entry
    cb_overall_repository = ClanBattleOverallEntryRepository()
    done_entries = cb_overall_repository.get_all_by_guild_id_boss_id_and_round(guild_id=guild_id,
                                                                               clan_battle_boss_id=clan_battle_boss_entry.ClanBattleBossId,
                                                                               boss_round=clan_battle_boss_entry.Round)

    if len(done_entries) > 0:
        embeds.append(create_done_embed(done_entries))

    # Book
    cb_book_repository = ClanBattleBossBookRepository()
    book_entries = cb_book_repository.get_all_by_message_id(message_id=message_id)

    if len(book_entries) > 0:
        embeds.append(create_book_embed(book_entries))

    await message.edit(content="", embeds=embeds, view=create_view())


def create_embed_list(guild_id: int, message_id: int) -> List[discord.Embed]:
    cb_entry_repository = ClanBattleBossEntryRepository()
    clan_battle_boss_entry = cb_entry_repository.get_last_by_message_id(message_id=message_id)

    cb_book_repository = ClanBattleBossBookRepository()
    book_entries = cb_book_repository.get_all_by_message_id(message_id=message_id)

    cb_overall_repository = ClanBattleOverallEntryRepository()
    done_entries = cb_overall_repository.get_all_by_guild_id_boss_id_and_round(guild_id=guild_id,
                                                                               clan_battle_boss_id=clan_battle_boss_entry.ClanBattleBossId,
                                                                               boss_round=clan_battle_boss_entry.Round)

    return [create_header_embed(clan_battle_boss_entry), create_done_embed(done_entries),
            create_book_embed(book_entries)]


def create_view() -> View:
    view = View(timeout=None)
    view.add_item(BookButton())
    view.add_item(CancelButton())
    view.add_item(EntryButton())
    view.add_item(DoneButton())
    view.add_item(DeadButton())
    return view


def book_check_by_guild_id(guild_id: int, player_id: int):
    cb_book_repository = ClanBattleBossBookRepository()
    return cb_book_repository.check_book_count_by_player_id(guild_id=guild_id, player_id=player_id)


def book_check_by_message_id(message_id: int, player_id: int):
    cb_book_repository = ClanBattleBossBookRepository()
    return cb_book_repository.get_one_by_message_id_and_player_id(message_id=message_id, player_id=player_id)


async def check_or_generate_channel_message(guild, channel_id: int):
    channel_message_repository = ChannelMessageRepository()
    channel = guild.get_channel(channel_id)
    # Get Message from Database
    channel_message = channel_message_repository.get_channel_message_by_channel_id(channel_id=channel.id)

    if channel_message is None:
        message = await channel.send(content="Preparing data . . .")
        channel_message = ChannelMessage(
            ChannelId=channel_id,
            MessageId=message.id,
        )
        channel_message_repository.insert_channel_message(channel_message)

    message = await utils.discord_try_fetch_message(channel, channel_message.MessageId)
    if message is None:
        message = await channel.send(content="Preparing data . . .")
        channel_message = ChannelMessage(
            ChannelId=channel_id,
            MessageId=message.id,
        )
        channel_message_repository.update_channel_message(channel_message)

    return message


async def generate_clan_battle_boss_entry(message_id: int, boss_id: int):
    cb_entry_repo = ClanBattleBossEntryRepository()
    cb_entry = cb_entry_repo.get_last_by_message_id(message_id=message_id)

    cb_period_repo = ClanBattlePeriodRepository()
    cb_period = cb_period_repo.get_current_running_clan_battle_period()

    # treat as new
    if cb_entry is None:

        clan_battle_boss_repository = ClanBattleBossRepository()
        clan_battle_boss = clan_battle_boss_repository.get_one_by_clan_battle_boss_id(clan_battle_boss_id=boss_id)

        clan_battle_boss_health_repository = ClanBattleBossHealthRepository()
        clan_battle_boss_health = clan_battle_boss_health_repository.get_one_by_position_and_round(
            position=clan_battle_boss.Position, boss_round=1)

        if clan_battle_boss and clan_battle_boss_health:
            cb_entry = ClanBattleBossEntry(
                MessageId=message_id,
                ClanBattlePeriodId=cb_period.ClanBattlePeriodId,
                ClanBattleBossId=clan_battle_boss.ClanBattleBossId,
                Name=f"{clan_battle_boss.Name} 「{clan_battle_boss.Description}」",
                Image=clan_battle_boss.ImagePath,
                Round=1,
                CurrentHealth=clan_battle_boss_health.Health,
                MaxHealth=clan_battle_boss_health.Health,
            )

            cb_entry_repo.insert_clan_battle_boss_entry(cb_entry)
            return cb_entry

    return cb_entry


async def generate_next_clan_battle_boss_entry(interaction: discord.interactions.Interaction, boss_id: int,
                                               message_id: int, attack_type: AttackTypeEnum, leftover_time: int):
    message_id = message_id
    guild_id = interaction.guild_id
    channel_id = interaction.channel.id
    cb_entry_repo = ClanBattleBossEntryRepository()
    boss_entry = cb_entry_repo.get_last_by_message_id(message_id=message_id)

    # Edit Old one
    prev_msg = await utils.discord_try_fetch_message(channel=interaction.channel, message_id=message_id)
    if prev_msg:
        cb_overall_repository = ClanBattleOverallEntryRepository()
        done_entries = cb_overall_repository.get_all_by_guild_id_boss_id_and_round(guild_id=guild_id,
                                                                                   clan_battle_boss_id=boss_entry.ClanBattleBossId,
                                                                                   boss_round=boss_entry.Round)

        await prev_msg.edit(embeds=[create_header_embed(cb_boss_entry=boss_entry, include_image=False),
                                    create_done_embed(done_entries)], view=None)

    # Generate New One
    cm_repo = ChannelMessageRepository()

    await interaction.channel.send(
        content=f"Boss killed by {interaction.user.display_name} with {attack_type.value} ({leftover_time}s)")

    next_round = boss_entry.Round + 1
    cb_boss_repo = ClanBattleBossRepository()
    cb_boss = cb_boss_repo.get_one_by_clan_battle_boss_id(clan_battle_boss_id=boss_id)

    cb_boss_health_repo = ClanBattleBossHealthRepository()
    cb_boss_health = cb_boss_health_repo.get_one_by_position_and_round(
        position=cb_boss.Position, boss_round=next_round)

    cb_period_repo = ClanBattlePeriodRepository()
    cb_period = cb_period_repo.get_current_running_clan_battle_period()

    new_message = await interaction.channel.send(content="Preparing data . . .")
    channel_message = ChannelMessage(
        ChannelId=channel_id,
        MessageId=new_message.id,
    )
    cm_repo.update_channel_message(channel_message)

    if cb_boss and cb_boss_health:
        boss_entry = ClanBattleBossEntry(
            MessageId=new_message.id,
            ClanBattlePeriodId=cb_period.ClanBattlePeriodId,
            ClanBattleBossId=cb_boss.ClanBattleBossId,
            Name=f"{cb_boss.Name} 「{cb_boss.Description}」",
            Image=cb_boss.ImagePath,
            Round=next_round,
            CurrentHealth=cb_boss_health.Health,
            MaxHealth=cb_boss_health.Health,
        )

        cb_entry_repo.insert_clan_battle_boss_entry(boss_entry)

    await refresh_boss_message(message=new_message)


bot.run(config.DISCORD_TOKEN, log_handler=handler)
