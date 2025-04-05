import logging
from typing import List

import discord
from discord.ext import commands
from discord.ui import Button, View, Modal, TextInput

import utils
from config import config
from repository import *
from utils import response_send_message

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')

# Replace 'YOUR_BOT_TOKEN' with your actual bot token
TOKEN = config['DISCORD_TOKEN']
NEW_LINE = "\n"

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
async def on_guild_join(guild):
    await setup_channel(guild)


async def setup_channel(guild):
    print(f'Setup for guild {guild.id} - {guild.name}')
    guild_id = guild.id
    guild_channel_repository = GuildChannelRepository()
    guild_channel = guild_channel_repository.get_guild_channel_by_guild_channel_id(guild_id=guild_id)

    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=False),
        guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_messages=True)
    }

    overwrites_tl_shifter = {
        guild.default_role: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }

    channels = {
        'Category': {
            'name': config['CATEGORY_CHANNEL_NAME'],
            'type': 'category',
            'overwrites': overwrites
        },
        'Report': {
            'name': config['REPORT_CHANNEL_NAME'],
            'type': 'text',
            'overwrites': overwrites
        },
        'Boss1': {
            'name': config['BOSS1_CHANNEL_NAME'],
            'type': 'text',
            'overwrites': overwrites
        },
        'Boss2': {
            'name': config['BOSS2_CHANNEL_NAME'],
            'type': 'text',
            'overwrites': overwrites
        },
        'Boss3': {
            'name': config['BOSS3_CHANNEL_NAME'],
            'type': 'text',
            'overwrites': overwrites
        },
        'Boss4': {
            'name': config['BOSS4_CHANNEL_NAME'],
            'type': 'text',
            'overwrites': overwrites
        },
        'Boss5': {
            'name': config['BOSS5_CHANNEL_NAME'],
            'type': 'text',
            'overwrites': overwrites
        },
        'TlShifter': {
            'name': config['TL_SHIFTER_CHANNEL_NAME'],
            'type': 'text',
            'overwrites': overwrites_tl_shifter
        }
    }

    if guild_channel is None:
        # Create Category and all channels
        category_channel = await guild.create_category(
            channels['Category']['name'],
            overwrites=channels['Category']['overwrites']
        )

        created_channels = {}

        for channel_type, channel_config in channels.items():
            if channel_type == 'Category':
                continue  # Skip category since it's already created

            channel = await guild.create_text_channel(
                channel_config['name'],
                category=category_channel,
                overwrites=channel_config['overwrites']
            )

            created_channels[channel_type] = channel  # Store the created channel object

        guild_channel = GuildChannel(
            GuildId=guild_id,
            CategoryId=category_channel.id,
            ReportChannelId=created_channels['Report'].id,
            Boss1ChannelId=created_channels['Boss1'].id,
            Boss2ChannelId=created_channels['Boss2'].id,
            Boss3ChannelId=created_channels['Boss3'].id,
            Boss4ChannelId=created_channels['Boss4'].id,
            Boss5ChannelId=created_channels['Boss5'].id,
            TlShifterChannelId=created_channels['TlShifter'].id
        )

        guild_channel_repository.insert_guild_channel(guild_channel)

    else:
        # Update existing channels
        category_channel = guild.get_channel(guild_channel.CategoryId)
        if category_channel is None:
            category_channel = await guild.create_category(
                channels['Category']['name'],
                overwrites=channels['Category']['overwrites']
            )

        for channel_type, channel_config in channels.items():
            if channel_type == 'Category':
                continue  # Skip category since it's already handled

            channel = guild.get_channel(getattr(guild_channel, f"{channel_type}ChannelId"))
            if channel is None:
                channel = await guild.create_text_channel(
                    channel_config['name'],
                    category=category_channel,
                    overwrites=channel_config['overwrites']
                )

                setattr(guild_channel, f"{channel_type}ChannelId", channel.id)

        guild_channel = GuildChannel(
            GuildId=guild_id,
            CategoryId=category_channel.id,
            ReportChannelId=guild_channel.ReportChannelId,
            Boss1ChannelId=guild_channel.Boss1ChannelId,
            Boss2ChannelId=guild_channel.Boss2ChannelId,
            Boss3ChannelId=guild_channel.Boss3ChannelId,
            Boss4ChannelId=guild_channel.Boss4ChannelId,
            Boss5ChannelId=guild_channel.Boss5ChannelId,
            TlShifterChannelId=guild_channel.TlShifterChannelId
        )

        guild_channel_repository.update_guild_channel(guild_channel)

    await setup_message(guild, guild_channel=guild_channel)


async def setup_message(guild, guild_channel: GuildChannel):
    # Master CB Data
    clan_battle_period_repository = ClanBattlePeriodRepository()
    clan_battle_period = clan_battle_period_repository.get_current_running_clan_battle_period()

    if clan_battle_period is None:
        print("Need setup on Database !")
        return

    boss1_message = await check_or_generate_channel_message(guild, guild_channel.Boss1ChannelId)
    boss2_message = await check_or_generate_channel_message(guild, guild_channel.Boss2ChannelId)
    boss3_message = await check_or_generate_channel_message(guild, guild_channel.Boss3ChannelId)
    boss4_message = await check_or_generate_channel_message(guild, guild_channel.Boss4ChannelId)
    boss5_message = await check_or_generate_channel_message(guild, guild_channel.Boss5ChannelId)

    await generate_clan_battle_boss_entry(message_id=boss1_message.id, boss_id=clan_battle_period.Boss1Id)
    await generate_clan_battle_boss_entry(message_id=boss2_message.id, boss_id=clan_battle_period.Boss2Id)
    await generate_clan_battle_boss_entry(message_id=boss3_message.id, boss_id=clan_battle_period.Boss3Id)
    await generate_clan_battle_boss_entry(message_id=boss4_message.id, boss_id=clan_battle_period.Boss4Id)
    await generate_clan_battle_boss_entry(message_id=boss5_message.id, boss_id=clan_battle_period.Boss5Id)

    await boss1_message.edit(content="", embeds=create_embed_list(message_id=boss1_message.id), view=create_view())
    await boss2_message.edit(content="", embeds=create_embed_list(message_id=boss2_message.id), view=create_view())
    await boss3_message.edit(content="", embeds=create_embed_list(message_id=boss3_message.id), view=create_view())
    await boss4_message.edit(content="", embeds=create_embed_list(message_id=boss4_message.id), view=create_view())
    await boss5_message.edit(content="", embeds=create_embed_list(message_id=boss5_message.id), view=create_view())


# Book Button
class BookButton(Button):
    def __init__(self):
        super().__init__(label=Emoji.BOOK.name.capitalize(),
                         style=discord.ButtonStyle.primary,
                         emoji=Emoji.BOOK.value,
                         row=0)

    async def callback(self, interaction: discord.Interaction):
        x_user = interaction.user
        message_id = interaction.message.id
        if book_check(message_id=message_id, player_id=x_user.id):
            await response_send_message(interaction=interaction, message="## Already booked !")
        else:
            ephemeral_view = View()
            ephemeral_view.add_item(BookPatkButton(interaction.message.id))
            ephemeral_view.add_item(BookMatkButton(interaction.message.id))
            ephemeral_view.add_item(BookCancelButton())
            await interaction.response.send_message("## Choose your Entry Type", view=ephemeral_view, ephemeral=True)


# Cancel Button
class CancelButton(Button):
    def __init__(self):
        super().__init__(label=Emoji.CANCEL.name.capitalize(),
                         style=discord.ButtonStyle.danger,
                         emoji=Emoji.CANCEL.value,
                         row=0)

    async def callback(self, interaction: discord.Interaction):
        cb_boss_player_entry_repository = ClanBattleBossPlayerEntryRepository()
        x_user = cb_boss_player_entry_repository.get_single_book_by_message_id_and_player_id(
            message_id=interaction.message.id,
            player_id=interaction.user.id)

        if x_user:
            cb_boss_player_entry_repository.delete_book_by_message_id_and_player_id(
                clan_battle_boss_player_entry_id=x_user.ClanBattleBossPlayerEntryId)
            await interaction.message.edit(embeds=create_embed_list(message_id=interaction.message.id),
                                           view=create_view())

        await interaction.response.defer(ephemeral=True)


# Entry Button
class EntryButton(Button):
    def __init__(self):
        super().__init__(label=Emoji.ENTRY.name.capitalize(),
                         style=discord.ButtonStyle.primary,
                         emoji=Emoji.ENTRY.value,
                         row=1)

    async def callback(self, interaction: discord.Interaction):
        x_user = interaction.user
        message_id = interaction.message.id
        if not book_check(message_id=message_id, player_id=x_user.id):
            await utils.response_send_message(interaction=interaction, message="## Not Booked")

        modal = EntryInputModal()
        await interaction.response.send_modal(modal)


# Entry Input
class EntryInputModal(Modal, title="Entry Input"):
    # Define a text input
    user_input = TextInput(
        label="Entry Damage (in Million)",
        placeholder="0000",
        style=discord.TextStyle.short,
        required=True,
        min_length=1,
        max_length=100
    )

    async def on_submit(self, interaction: discord.Interaction):
        # Handle the submitted input
        if not self.user_input.value.isnumeric():
            await utils.response_send_message(interaction=interaction, message=f"## Number Only !")
            return
        if int(self.user_input.value) == 0:
            await utils.response_send_message(interaction=interaction, message=f"## Higher than 0 !")
            return
        await utils.response_send_message(interaction=interaction,
                                          message=f"Entry Damage Input : {self.user_input.value}")


# Done Button
class DoneButton(Button):
    def __init__(self):
        super().__init__(label=Emoji.DONE.name.capitalize(),
                         style=discord.ButtonStyle.green,
                         emoji=Emoji.DONE.value,
                         row=1)

    async def callback(self, interaction: discord.Interaction):
        x_user = interaction.user
        message_id = interaction.message.id
        if not book_check(message_id=message_id, player_id=x_user.id):
            await utils.response_send_message(interaction=interaction, message="## Not Booked")


# Dead Button
class DeadButton(Button):
    def __init__(self):
        super().__init__(label="Dead",
                         style=discord.ButtonStyle.gray,
                         emoji=Emoji.FINISH.value,
                         row=1)

    async def callback(self, interaction: discord.Interaction):
        x_user = interaction.user
        message_id = interaction.message.id
        if not book_check(message_id=message_id, player_id=x_user.id):
            await utils.response_send_message(interaction=interaction, message="## Not Booked")

        modal = LeftoverInputModal()
        await interaction.response.send_modal(modal)


# Leftover Modal
class LeftoverInputModal(Modal, title="Leftover Input"):
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
        # Handle the submitted input
        await utils.response_send_message(interaction=interaction,
                                          message=f"Boss Leftover Input Time : {self.user_input.value}")


def generate_done_attack_list(datas: List[ClanBattleBossPlayerEntry]) -> str:
    lines = [f"===== {Emoji.DONE.value} Done List ====={NEW_LINE}"]
    for data in datas:
        lines.append(
            f"{Emoji[data.AttackType].value} {utils.format_large_number(data.Damage)}: {data.PlayerName}{NEW_LINE}"
        )

    return f"```powershell{NEW_LINE}" + "".join(lines) + "```"


def generate_book_list(datas: List[ClanBattleBossPlayerEntry]) -> str:
    lines = [f"===== {Emoji.ENTRY.value} Book List ====={NEW_LINE}"]
    for data in datas:
        line = f"{Emoji[data.AttackType].value} {utils.format_large_number(data.Damage) if data.Damage != 0 else ''}: {data.PlayerName}"
        lines.append(line + NEW_LINE)

    return f"```powershell{NEW_LINE}" + "".join(lines) + "```"


# PATK Button
class BookPatkButton(Button):
    def __init__(self, message_id: int):
        super().__init__(label=Emoji.PATK.name,
                         style=discord.ButtonStyle.green,
                         emoji=Emoji.PATK.value,
                         row=0)
        self.message_id = message_id

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        cb_boss_player_entry_repository = ClanBattleBossPlayerEntryRepository()
        x_user = cb_boss_player_entry_repository.get_single_book_by_message_id_and_player_id(message_id=self.message_id,
                                                                                             player_id=user.id)
        if x_user:
            await interaction.response.defer(ephemeral=True)
            await interaction.delete_original_response()
            return

        message = await utils.try_fetch_message(channel=interaction.channel, message_id=self.message_id)

        # Insert to Db first !
        cb_boss_entry_repository = ClanBattleBossEntryRepository()
        cb_boss_entry = cb_boss_entry_repository.get_last_by_message_id(message_id=message.id)

        cb_boss_player_entry = ClanBattleBossPlayerEntry(ClanBattleBossEntryId=cb_boss_entry.ClanBattleBossEntryId,
                                                         PlayerId=user.id,
                                                         PlayerName=user.name,
                                                         AttackType=Emoji.PATK.name,
                                                         Damage=0,
                                                         IsDoneEntry=False
                                                         )

        cb_boss_player_entry_repository.insert_clan_battle_boss_player_book_entry(
            clan_battle_boss_player_entry=cb_boss_player_entry)

        await message.edit(embeds=create_embed_list(message_id=message.id), view=create_view())
        await interaction.response.defer(ephemeral=True)
        await interaction.delete_original_response()
        await interaction.channel.send(content=f"{interaction.user.name} {Emoji.PATK.value} added to book list.",
                                       delete_after=config['MESSAGE_DEFAULT_DELETE_AFTER'])


# MATK Button
class BookMatkButton(Button):
    def __init__(self, message_id: int):
        super().__init__(label=Emoji.MATK.name,
                         style=discord.ButtonStyle.blurple,
                         emoji=Emoji.MATK.value,
                         row=0)
        self.message_id = message_id

    async def callback(self, interaction: discord.Interaction):
        user = interaction.user
        cb_boss_player_entry_repository = ClanBattleBossPlayerEntryRepository()
        x_user = cb_boss_player_entry_repository.get_single_book_by_message_id_and_player_id(message_id=self.message_id,
                                                                                             player_id=user.id)
        if x_user:
            await interaction.delete_original_response()
            return

        message = await utils.try_fetch_message(channel=interaction.channel, message_id=self.message_id)

        # Insert to Db first !
        cb_boss_entry_repository = ClanBattleBossEntryRepository()
        cb_boss_entry = cb_boss_entry_repository.get_last_by_message_id(message_id=message.id)

        cb_boss_player_entry = ClanBattleBossPlayerEntry(ClanBattleBossEntryId=cb_boss_entry.ClanBattleBossEntryId,
                                                         PlayerId=user.id,
                                                         PlayerName=user.name,
                                                         AttackType=Emoji.MATK.name,
                                                         Damage=0,
                                                         IsDoneEntry=False
                                                         )

        cb_boss_player_entry_repository.insert_clan_battle_boss_player_book_entry(
            clan_battle_boss_player_entry=cb_boss_player_entry)

        await message.edit(embeds=create_embed_list(message.id), view=create_view())
        await interaction.response.defer(ephemeral=True)
        await interaction.delete_original_response()
        await interaction.channel.send(content=f"{interaction.user.name} {Emoji.MATK.value} added to book list.",
                                       delete_after=config['MESSAGE_DEFAULT_DELETE_AFTER'])


# Cancel Button (in Book context)
class BookCancelButton(Button):
    def __init__(self):
        super().__init__(label="Cancel",
                         style=discord.ButtonStyle.red,
                         emoji=Emoji.CANCEL.value,
                         row=0)

    async def callback(self, interaction: discord.Interaction):
        await interaction.delete_original_response()


def create_header_embed(cb_boss_entry: ClanBattleBossEntry):
    embed = discord.Embed(
        title=f"{cb_boss_entry.Name} (Round {cb_boss_entry.Round})",
        description=f"# HP : {utils.format_large_number(cb_boss_entry.CurrentHealth)} / {utils.format_large_number(cb_boss_entry.MaxHealth)}",
        color=discord.Color.red()
    )
    embed.set_image(url=cb_boss_entry.Image)
    return embed


def create_done_embed(list_boss_cb_player_entries: List[ClanBattleBossPlayerEntry]):
    embed = discord.Embed(
        title="",
        description=generate_done_attack_list(list_boss_cb_player_entries),
        color=discord.Color.green(),
    )
    return embed


def create_book_embed(list_boss_cb_player_entries: List[ClanBattleBossPlayerEntry]):
    embed = discord.Embed(
        title="",
        description=generate_book_list(list_boss_cb_player_entries),
        color=discord.Color.blue(),
    )
    return embed


def create_embed_list(message_id: int) -> List[discord.Embed]:
    clan_battle_boss_entry_repository = ClanBattleBossEntryRepository()
    clan_battle_boss_entry = clan_battle_boss_entry_repository.get_last_by_message_id(message_id=message_id)

    cb_boss_player_entry_repository = ClanBattleBossPlayerEntryRepository()
    list_boss_cb_player_entries = cb_boss_player_entry_repository.get_all_by_message_id(message_id=message_id)

    book_entries = []
    done_entries = []
    if len(list_boss_cb_player_entries) > 0:
        book_entries = [entry for entry in list_boss_cb_player_entries if not entry.IsDoneEntry]
        done_entries = [entry for entry in list_boss_cb_player_entries if entry.IsDoneEntry]

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


def book_check(message_id: int, player_id: int):
    cb_boss_entry_player_repository = ClanBattleBossPlayerEntryRepository()
    return cb_boss_entry_player_repository.get_single_book_by_message_id_and_player_id(message_id, player_id)


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

    message = await utils.try_fetch_message(channel, channel_message.MessageId)
    if message is None:
        message = await channel.send(content="Preparing data . . .")
        channel_message = ChannelMessage(
            ChannelId=channel_id,
            MessageId=message.id,
        )
        channel_message_repository.update_channel_message(channel_message)

    return message


async def generate_clan_battle_boss_entry(message_id: int, boss_id: int, gen_next_round: bool = False):
    clan_battle_boss_entry_repository = ClanBattleBossEntryRepository()
    clan_battle_boss_entry = clan_battle_boss_entry_repository.get_last_by_message_id(message_id=message_id)

    # For Next ?
    if gen_next_round:
        next_round = clan_battle_boss_entry.round + 1
        clan_battle_boss_repository = ClanBattleBossRepository()
        clan_battle_boss = clan_battle_boss_repository.get_one_by_clan_battle_boss_id(clan_battle_boss_id=boss_id)

        clan_battle_boss_health_repository = ClanBattleBossHealthRepository()
        clan_battle_boss_health = clan_battle_boss_health_repository.get_one_by_position_and_round(
            position=clan_battle_boss.position, round=next_round)

        if clan_battle_boss and clan_battle_boss_health:
            clan_battle_boss_entry = ClanBattleBossEntry(
                MessageId=message_id,
                BossId=clan_battle_boss.boss_id,
                Name=f"{clan_battle_boss.Name} 「{clan_battle_boss.Description}」",
                Image=clan_battle_boss.ImagePath,
                Round=next_round,
                CurrentHealth=clan_battle_boss_health.health,
                MaxHealth=clan_battle_boss_health.health,
            )

            clan_battle_boss_entry_repository.insert_clan_battle_boss_entry(clan_battle_boss_entry)

            return clan_battle_boss_entry

    # treat as new
    if clan_battle_boss_entry is None:

        clan_battle_boss_repository = ClanBattleBossRepository()
        clan_battle_boss = clan_battle_boss_repository.get_one_by_clan_battle_boss_id(clan_battle_boss_id=boss_id)

        clan_battle_boss_health_repository = ClanBattleBossHealthRepository()
        clan_battle_boss_health = clan_battle_boss_health_repository.get_one_by_position_and_round(
            position=clan_battle_boss.Position, round=1)

        if clan_battle_boss and clan_battle_boss_health:
            clan_battle_boss_entry = ClanBattleBossEntry(
                MessageId=message_id,
                BossId=clan_battle_boss.ClanBattleBossId,
                Name=f"{clan_battle_boss.Name} 「{clan_battle_boss.Description}」",
                Image=clan_battle_boss.ImagePath,
                Round=1,
                CurrentHealth=clan_battle_boss_health.Health,
                MaxHealth=clan_battle_boss_health.Health,
            )

            clan_battle_boss_entry_repository.insert_clan_battle_boss_entry(clan_battle_boss_entry)
            return clan_battle_boss_entry

    return clan_battle_boss_entry


bot.run(TOKEN, log_handler=handler)
