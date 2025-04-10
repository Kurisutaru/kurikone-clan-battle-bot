import discord
from discord.ui import View, Button, Modal, TextInput

import enums
import utils
from config import config
from enums import EmojiEnum, AttackTypeEnum
from logger import KuriLogger
from models import ClanBattleLeftover
from services import ClanBattleBossBookService, ClanBattleOverallEntryService, MainService, ClanBattleBossEntryService

NEW_LINE = "\n"


# Book Button
class BookButton(Button):
    def __init__(self):
        self.clan_battle_boss_book_service = ClanBattleBossBookService()
        self.clan_battle_overall_entry_service = ClanBattleOverallEntryService()
        self.logger = KuriLogger()
        super().__init__(label=EmojiEnum.BOOK.name.capitalize(),
                         style=discord.ButtonStyle.primary,
                         emoji=EmojiEnum.BOOK.value,
                         row=0)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        guild_id = interaction.guild_id
        message_id = interaction.message.id

        boss_book = await self.clan_battle_boss_book_service.get_player_book_count(guild_id, user_id)
        if not boss_book.is_success:
            interaction.response.defer(ephemeral=True)
            self.logger.error(boss_book.error_messages)
            return

        if boss_book.result > 0:
            await utils.discord_resp_send_msg(interaction=interaction, message="## Already booked !")
            return

        entry_count = await self.clan_battle_overall_entry_service.get_player_overall_entry_count(
            guild_id, user_id)
        if not entry_count.is_success:
            interaction.response.defer(ephemeral=True)
            self.logger.error(entry_count.error_messages)
            return

        count = entry_count.result

        disable = count == 3

        # generate Leftover ?
        leftover = await self.clan_battle_overall_entry_service.get_leftover_by_guild_id_and_player_id(
            guild_id=guild_id, player_id=user_id)
        if not leftover.is_success:
            interaction.response.defer(ephemeral=True)
            self.logger.error(leftover.error_messages)
            return

        # if disable and len(leftover.result) == 0:
        #     await utils.discord_resp_send_msg(interaction=interaction, message="## No more entry for today !")
        #     return

        view = View(timeout=None)
        view.add_item(BookPatkButton(message_id=message_id, disable=disable))
        view.add_item(BookMatkButton(message_id=message_id, disable=disable))
        view.add_item(ConfirmationNoCancelButton(emoji_param=EmojiEnum.CANCEL))
        for left_data in leftover.result:
            view.add_item(BookLeftoverButton(leftover=left_data, message_id=message_id))

        await interaction.response.send_message(
            f"## Choose your Entry Type [{utils.reduce_int_ab_non_zero(a=3, b=count)}/3]", view=view,
            ephemeral=True, delete_after=15)


# Cancel Button
class CancelButton(Button):
    def __init__(self):
        self.main_service = MainService()
        self.clan_battle_boss_book_service = ClanBattleBossBookService()
        self.logger = KuriLogger()
        super().__init__(label=EmojiEnum.CANCEL.name.capitalize(),
                         style=discord.ButtonStyle.danger,
                         emoji=EmojiEnum.CANCEL.value,
                         row=0)

    async def callback(self, interaction: discord.Interaction):
        book_result = await self.clan_battle_boss_book_service.get_player_book_entry(
            message_id=interaction.message.id,
            player_id=interaction.user.id)

        if not book_result.is_success or book_result.result is None:
            await interaction.response.defer(ephemeral=True)
            self.logger.error(book_result.error_messages)
            return

        await self.clan_battle_boss_book_service.delete_book_by_id(book_id=book_result.result.clan_battle_boss_book_id)
        embeds = await self.main_service.refresh_clan_battle_boss_embeds(guild_id=interaction.guild_id,
                                                                         message_id=interaction.message.id)
        if not embeds.is_success:
            await interaction.response.defer(ephemeral=True)
            self.logger.error(embeds.error_messages)
            return

        await interaction.message.edit(embeds=embeds.result, view=create_view())
        await interaction.response.defer(ephemeral=True)


# Entry Button
class EntryButton(Button):
    def __init__(self):
        self.clan_battle_book_service = ClanBattleBossBookService()
        super().__init__(label=EmojiEnum.ENTRY.name.capitalize(),
                         style=discord.ButtonStyle.primary,
                         emoji=EmojiEnum.ENTRY.value,
                         row=1)

    async def callback(self, interaction: discord.Interaction):
        book = await self.clan_battle_book_service.get_player_book_entry(message_id=interaction.message.id,
                                                                         player_id=interaction.user.id)
        if book.is_success and book.result is None:
            await utils.discord_resp_send_msg(interaction=interaction, message="## Not Booked")
            return

        modal = EntryInputModal()
        await interaction.response.send_modal(modal)


# Entry Input
class EntryInputModal(Modal, title="Entry Input"):
    def __init__(self):
        super().__init__()
        self.main_service = MainService()
        self.logger = KuriLogger()
        self.clan_battle_boss_book_service = ClanBattleBossBookService()

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
        book_result = await self.clan_battle_boss_book_service.get_player_book_entry(
            message_id=interaction.message.id,
            player_id=interaction.user.id)
        book = book_result.result

        if not book_result.is_success:
            interaction.response.defer(ephemeral=True)
            self.logger.error(book_result.error_messages)
            return

        damage = int(self.user_input.value)
        update_result = await self.clan_battle_boss_book_service.update_damage_boss_book_by_id(
            book.clan_battle_boss_entry_id,
            damage)

        if not update_result.is_success:
            interaction.response.defer(ephemeral=True)
            self.logger.error(book_result.error_messages)
            return

        # Refresh Messages
        message = await utils.discord_try_fetch_message(channel=interaction.channel, message_id=message_id)
        if message:
            embeds = await self.main_service.refresh_clan_battle_boss_embeds(guild_id=interaction.guild_id,
                                                                             message_id=interaction.message.id)
            if not embeds.is_success:
                interaction.response.defer(ephemeral=True)
                self.logger.error(embeds.error_messages)
                return

            await interaction.message.edit(embeds=embeds.result, view=create_view())

        await interaction.response.defer(ephemeral=True)


# Done Button
class DoneButton(Button):
    def __init__(self):
        self.clan_battle_book_service = ClanBattleBossBookService()
        super().__init__(label=EmojiEnum.DONE.name.capitalize(),
                         style=discord.ButtonStyle.green,
                         emoji=EmojiEnum.DONE.value,
                         row=1)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        message_id = interaction.message.id
        book_result = await self.clan_battle_book_service.get_player_book_entry(message_id=message_id,
                                                                                player_id=user_id)
        book = book_result.result

        if book_result.is_success and book_result.result is None:
            await utils.discord_resp_send_msg(interaction=interaction, message="## Not Booked")
            return

        if book.damage is None:
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
        self.main_service = MainService()
        self.logger = KuriLogger()
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

        done_service = await self.main_service.done_entry(guild_id, message_id, user_id, display_name)
        if not done_service.is_success:
            interaction.response.defer(ephemeral=True)
            self.logger.error(done_service.error_messages)
            return

        # Refresh Messages
        message = await utils.discord_try_fetch_message(channel=interaction.channel, message_id=message_id)
        if message:
            embeds = await self.main_service.refresh_clan_battle_boss_embeds(guild_id, message_id)
            if not embeds.is_success:
                interaction.response.defer(ephemeral=True)
                self.logger.error(embeds.error_messages)
                return

            await message.edit(embeds=embeds.result, view=create_view())

        await utils.discord_close_response(interaction=interaction)


# Dead Button
class DeadButton(Button):
    def __init__(self):
        self.clan_battle_boss_book_service = ClanBattleBossBookService()
        self.clan_battle_boss_entry_service = ClanBattleBossEntryService()
        self.logger = KuriLogger()
        super().__init__(label="Dead",
                         style=discord.ButtonStyle.gray,
                         emoji=EmojiEnum.FINISH.value,
                         row=1)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        message_id = interaction.message.id
        book_result = await self.clan_battle_boss_book_service.get_player_book_entry(message_id=message_id,
                                                                                     player_id=user_id)
        if not book_result.is_success:
            interaction.response.defer(ephemeral=True)
            self.logger.error(book_result.error_messages)
            return

        book = book_result.result
        if book_result.is_success and book is None:
            await utils.discord_resp_send_msg(interaction=interaction, message="## Not Booked")
            return

        if book.damage is None:
            await utils.discord_resp_send_msg(interaction=interaction, message="## Input entry first !")
            return

        boss_entry = await self.clan_battle_boss_entry_service.get_last_by_message_id(message_id)
        if not book_result.is_success:
            interaction.response.defer(ephemeral=True)
            self.logger.error(boss_entry.error_messages)
            return

        if book.damage < boss_entry.result.current_health:
            await utils.discord_resp_send_msg(interaction=interaction,
                                              message="## Your entry damage lower than boss health !")
            return

        # Fresh Entry
        if book.leftover_time is None:
            modal = LeftoverInputModal()
            await interaction.response.send_modal(modal)
        # Carry over
        else:
            view = View(timeout=None)
            view.add_item(DeadOkButton(message_id=message_id, leftover_time=book.leftover_time))
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

        await interaction.response.send_message(
            content=f"## Are you sure want to Mark your entry as Boss Kill ?{NEW_LINE}"
                    f"Leftover Time : **{leftover_time}s**",
            view=view, ephemeral=True,
            delete_after=config.MESSAGE_DEFAULT_DELETE_AFTER_LONG)


# Done Ok Confirm Button
class DeadOkButton(Button):
    def __init__(self, message_id: int, leftover_time: int):
        super().__init__(label=EmojiEnum.DONE.name.capitalize(),
                         style=discord.ButtonStyle.green,
                         emoji=EmojiEnum.DONE.value,
                         row=0)
        self.main_service = MainService()
        self.logger = KuriLogger()
        self.message_id = message_id
        self.leftover_time = leftover_time

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        display_name = interaction.user.display_name
        message_id = self.message_id
        guild_id = interaction.guild_id
        leftover_time = self.leftover_time

        await utils.discord_close_response(interaction=interaction)

        dead_result = await self.main_service.dead_ok(guild_id, message_id, user_id, display_name, leftover_time)
        if not dead_result.is_success:
            self.logger.error(dead_result.error_messages)
            await interaction.response.defer(ephemeral=True)

        boss_id = dead_result.result.clan_battle_boss_id
        generate = await self.main_service.generate_next_boss(interaction, boss_id, message_id,
                                                              dead_result.result.attack_type, leftover_time)
        if not generate.is_success:
            self.logger.error(generate.error_messages)
            await interaction.response.defer(ephemeral=True)

        message = await utils.discord_try_fetch_message(interaction.channel, generate.result.message_id)
        if message is None:
            self.logger.error("Failed to fetch message")
            await interaction.response.defer(ephemeral=True)

        embeds = await self.main_service.refresh_clan_battle_boss_embeds(guild_id, message.id)
        if not embeds.is_success:
            interaction.response.defer(ephemeral=True)
            self.logger.error(embeds.error_messages)
            return

        await message.edit(content="", embeds=embeds.result, view=create_view())


# PATK Button
class BookPatkButton(Button):
    def __init__(self, message_id: int, disable: bool):
        self.main_service = MainService()
        self.logger = KuriLogger()
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
        guild_id = interaction.guild_id
        message_id = self.message_id

        insert_result = await self.main_service.insert_boss_book_entry(guild_id, message_id, user_id, display_name,
                                                                       self.attack_type)
        if not insert_result.is_success:
            interaction.response.defer(ephemeral=True)
            self.logger.error(insert_result.error_messages)
            return

        message = await utils.discord_try_fetch_message(interaction.channel, message_id)
        if message is None:
            interaction.response.defer(ephemeral=True)
            self.logger.error("Could not fetch message")
            return

        embeds = await self.main_service.refresh_clan_battle_boss_embeds(guild_id, message_id)
        if not insert_result.is_success:
            interaction.response.defer(ephemeral=True)
            self.logger.error(embeds.error_messages)
            return

        await message.edit(embeds=embeds.result, view=create_view())
        await utils.discord_close_response(interaction=interaction)
        await interaction.channel.send(content=f"{display_name} {self.local_emoji.value} added to book list.",
                                       delete_after=config.MESSAGE_DEFAULT_DELETE_AFTER_SHORT)


# MATK Button
class BookMatkButton(Button):
    def __init__(self, message_id: int, disable: bool):
        self.main_service = MainService()
        self.logger = KuriLogger()
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
        guild_id = interaction.guild_id
        message_id = self.message_id

        insert_result = await self.main_service.insert_boss_book_entry(guild_id, message_id, user_id, display_name,
                                                                       self.attack_type)
        if not insert_result.is_success:
            interaction.response.defer(ephemeral=True)
            self.logger.error(insert_result.error_messages)
            return

        message = await utils.discord_try_fetch_message(interaction.channel, message_id)
        if message is None:
            interaction.response.defer(ephemeral=True)
            self.logger.error("Could not fetch message")
            return

        embeds = await self.main_service.refresh_clan_battle_boss_embeds(guild_id, message_id)
        if not insert_result.is_success:
            interaction.response.defer(ephemeral=True)
            self.logger.error(embeds.error_messages)
            return

        await message.edit(embeds=embeds.result, view=create_view())
        await utils.discord_close_response(interaction=interaction)
        await interaction.channel.send(content=f"{display_name} {self.local_emoji.value} added to book list.",
                                       delete_after=config.MESSAGE_DEFAULT_DELETE_AFTER_SHORT)


# Leftover Button
class BookLeftoverButton(Button):
    def __init__(self, leftover: ClanBattleLeftover, message_id: int):
        self.main_service = MainService()
        self.logger = KuriLogger()
        self.local_emoji = EmojiEnum.CARRY
        self.attack_type = AttackTypeEnum.CARRY
        self.message_id = message_id
        self.parent_overall_id = leftover.clan_battle_overall_entry_id
        self.label_string = f"{leftover.attack_type.value} {leftover.leftover_time}s ({leftover.clan_battle_boss_name})"
        self.leftover_time = leftover.leftover_time

        super().__init__(label=self.label_string,
                         style=discord.ButtonStyle.blurple,
                         emoji=self.local_emoji.value,
                         row=1)

    async def callback(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        display_name = interaction.user.display_name
        guild_id = interaction.guild_id
        message_id = self.message_id
        leftover_time = self.leftover_time
        attack_type = self.attack_type
        parent_overall_id = self.parent_overall_id

        insert_result = await self.main_service.insert_boss_book_entry(guild_id, message_id, user_id, display_name,
                                                                       attack_type, parent_overall_id, leftover_time)
        if not insert_result.is_success:
            interaction.response.defer(ephemeral=True)
            self.logger.error(insert_result.error_messages)
            return

        message = await utils.discord_try_fetch_message(interaction.channel, message_id)
        if message is None:
            interaction.response.defer(ephemeral=True)
            self.logger.error("Could not fetch message")
            return

        embeds = await self.main_service.refresh_clan_battle_boss_embeds(guild_id, message_id)
        if not insert_result.is_success:
            interaction.response.defer(ephemeral=True)
            self.logger.error(embeds.error_messages)
            return

        await message.edit(embeds=embeds.result, view=create_view())
        await utils.discord_close_response(interaction=interaction)
        await interaction.channel.send(content=f"{display_name} {self.local_emoji.value} added to book list.",
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


def create_view() -> View:
    view = View(timeout=None)
    view.add_item(BookButton())
    view.add_item(CancelButton())
    view.add_item(EntryButton())
    view.add_item(DoneButton())
    view.add_item(DeadButton())
    return view
