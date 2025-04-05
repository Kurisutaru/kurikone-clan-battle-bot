# repository.py
import mariadb

from database import MariaDBConnectionPool
from models import *

class GuildChannelRepository:
    def __init__(self):
        self.pool = MariaDBConnectionPool()

    def get_guild_channel_by_guild_channel_id(self, guild_id: int):
        try:
            with MariaDBConnectionPool() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        SELECT guild_id,
                               category_id,
                               report_channel_id,
                               boss_1_channel_id,
                               boss_2_channel_id,
                               boss_3_channel_id,
                               boss_4_channel_id,
                               boss_5_channel_id,
                               tl_shifter_channel_id
                        FROM guild_channel
                        WHERE guild_id = ?
                        """,
                        (guild_id,)
                    )
                    result = cursor.fetchone()
                    if result:
                        return GuildChannel(GuildId=result['guild_id'],
                                          CategoryId=result['category_id'],
                                          ReportChannelId=result['report_channel_id'],
                                          Boss1ChannelId=result['boss_1_channel_id'],
                                          Boss2ChannelId=result['boss_2_channel_id'],
                                          Boss3ChannelId=result['boss_3_channel_id'],
                                          Boss4ChannelId=result['boss_4_channel_id'],
                                          Boss5ChannelId=result['boss_5_channel_id'],
                                          TlShifterChannelId=result['tl_shifter_channel_id']
                                          )
                    return None
        except mariadb.Error as e:
            print(f"Database error: {e}")

    def insert_guild_channel(self, guild_channel: GuildChannel):
        try:
            with MariaDBConnectionPool() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        INSERT INTO guild_channel (guild_id, category_id, report_channel_id, boss_1_channel_id, boss_2_channel_id,
                           boss_3_channel_id, boss_4_channel_id, boss_5_channel_id, tl_shifter_channel_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """,
                        (guild_channel.GuildId,
                         guild_channel.CategoryId,
                         guild_channel.ReportChannelId,
                         guild_channel.Boss1ChannelId,
                         guild_channel.Boss2ChannelId,
                         guild_channel.Boss3ChannelId,
                         guild_channel.Boss4ChannelId,
                         guild_channel.Boss5ChannelId,
                         guild_channel.TlShifterChannelId)
                    )
                    conn.commit()
        except mariadb.Error as e:
            conn.rollback()

    def update_guild_channel(self, guild_channel: GuildChannel):
        try:
            with MariaDBConnectionPool() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        UPDATE guild_channel
                            SET category_id = ?, 
                                report_channel_id = ?, 
                                boss_1_channel_id = ?, 
                                boss_2_channel_id = ?, 
                                boss_3_channel_id = ?, 
                                boss_4_channel_id = ?, 
                                boss_5_channel_id = ?, 
                                tl_shifter_channel_id = ?
                        WHERE guild_id = ?
                        """,
                        (guild_channel.CategoryId,
                         guild_channel.ReportChannelId,
                         guild_channel.Boss1ChannelId,
                         guild_channel.Boss2ChannelId,
                         guild_channel.Boss3ChannelId,
                         guild_channel.Boss4ChannelId,
                         guild_channel.Boss5ChannelId,
                         guild_channel.TlShifterChannelId,
                         guild_channel.GuildId)
                    )
                    conn.commit()
        except mariadb.Error as e:
            conn.rollback()

class ChannelMessageRepository:
    def __init__(self):
        self.pool = MariaDBConnectionPool()

    def insert_channel_message(self, channel_message: ChannelMessage):
        try:
            with MariaDBConnectionPool() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        INSERT INTO channel_message (channel_id, message_id) 
                        VALUES (?, ?)
                        """,
                        (channel_message.ChannelId,
                         channel_message.MessageId)
                    )
                    conn.commit()
        except mariadb.Error as e:
            conn.rollback()
            print(f"Database error: {e}")

    def update_channel_message(self, channel_message: ChannelMessage):
        try:
            with MariaDBConnectionPool() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        UPDATE channel_message 
                            SET message_id = ?
                        WHERE channel_id = ?
                        """,
                        (channel_message.MessageId,
                         channel_message.ChannelId,)
                    )
                    conn.commit()
        except mariadb.Error as e:
            conn.rollback()
            print(f"Database error: {e}")

    def get_channel_message_by_channel_id(self, channel_id: int):
        try:
            with MariaDBConnectionPool() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        SELECT channel_id,
                               message_id
                        FROM channel_message
                        WHERE channel_id = ?
                        """,
                        (channel_id,)
                    )
                    result = cursor.fetchone()
                    if result:
                        return ChannelMessage(
                            ChannelId=result['channel_id'],
                            MessageId=result['message_id']
                        )
                    return None
        except mariadb.Error as e:
            print(f"Database error: {e}")

class ClanBattleBossEntryRepository:
    def __init__(self):
        self.pool = MariaDBConnectionPool()

    def insert_clan_battle_boss_entry(self, clan_battle_boss_entry: ClanBattleBossEntry):
        try:
            with MariaDBConnectionPool() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        INSERT INTO clan_battle_boss_entry (message_id, boss_id, name, image, round, current_health, max_health) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """,
                        (clan_battle_boss_entry.MessageId,
                         clan_battle_boss_entry.BossId,
                         clan_battle_boss_entry.Name,
                         clan_battle_boss_entry.Image,
                         clan_battle_boss_entry.Round,
                         clan_battle_boss_entry.CurrentHealth,
                         clan_battle_boss_entry.MaxHealth)
                    )
                conn.commit()
        except mariadb.Error as e:
            conn.rollback()
            print(f"Database error: {e}")

    def get_last_by_message_id(self, message_id: int):
        try:
            with MariaDBConnectionPool() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        SELECT clan_battle_boss_entry_id,
                               message_id,
                               boss_id,
                               name,
                               image,
                               round,
                               current_health,
                               max_health
                        FROM clan_battle_boss_entry
                        WHERE message_id = ?
                        ORDER BY clan_battle_boss_entry_id DESC
                        LIMIT 1
                        """,
                        (message_id,)
                    )
                    result = cursor.fetchone()
                    if result:
                        return ClanBattleBossEntry(ClanBattleBossEntryId=result['clan_battle_boss_entry_id'],
                                         MessageId=result['message_id'],
                                         BossId=result['boss_id'],
                                         Name=result['name'],
                                         Image=result['image'],
                                         Round=result['round'],
                                         CurrentHealth=result['current_health'],
                                         MaxHealth=result['max_health']
                                         )
                    return None
        except mariadb.Error as e:
            print(f"Database error: {e}")

    def update_on_attack(self, clan_battle_boss_entry_id: int, current_health: int):
        try:
            with MariaDBConnectionPool() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        UPDATE clan_battle_boss_entry 
                        SET current_health = ?
                        WHERE clan_battle_boss_entry_id = ?
                        """,
                        (current_health,
                         clan_battle_boss_entry_id)
                    )
                    conn.commit()
        except mariadb.Error as e:
            conn.rollback()
            print(f"Database error: {e}")

class ClanBattleBossPlayerEntryRepository:
    def __init__(self):
        self.pool = MariaDBConnectionPool()

    def get_all_by_message_id(self, message_id: int):
        try:
            with MariaDBConnectionPool() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        SELECT CBPE.clan_battle_boss_player_entry_id,
                               CBPE.clan_battle_boss_entry_id,
                               CBPE.player_id,
                               CBPE.player_name,
                               CBPE.attack_type,
                               CBPE.damage,
                               CBPE.is_done_entry
                        FROM clan_battle_boss_player_entry CBPE
                                 JOIN clan_battle_boss_entry CBE ON CBPE.clan_battle_boss_entry_id = CBE.clan_battle_boss_entry_id
                        WHERE CBE.message_id = ?
                        """,
                        (message_id,)
                    )
                    result = cursor.fetchall()
                    if result:
                        entries = []
                        for row in result:
                            entry = ClanBattleBossPlayerEntry(
                                ClanBattleBossPlayerEntryId=row['clan_battle_boss_player_entry_id'],
                                ClanBattleBossEntryId=row['clan_battle_boss_entry_id'],
                                PlayerId=row['player_id'],
                                PlayerName=row['player_name'],
                                AttackType=row['attack_type'],
                                Damage=row['damage'],
                                IsDoneEntry=row['is_done_entry']
                            )
                            entries.append(entry)
                        return entries
                    return []
        except mariadb.Error as e:
            print(f"Database error: {e}")

    def get_all_by_message_id_and_book_type(self, message_id: int, book_type: int):
        try:
            with MariaDBConnectionPool() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        SELECT CBPE.clan_battle_boss_player_entry_id,
                               CBPE.clan_battle_boss_entry_id,
                               CBPE.player_id,
                               CBPE.player_name,
                               CBPE.attack_type,
                               CBPE.damage,
                               CBPE.is_done_entry
                        FROM clan_battle_boss_player_entry CBPE
                                 JOIN clan_battle_boss_entry CBE ON CBPE.clan_battle_boss_entry_id = CBE.clan_battle_boss_entry_id
                        WHERE CBE.message_id = ?
                          AND CBPE.is_done_entry = ?
                        """,
                        (message_id,
                         book_type)
                    )
                    result = cursor.fetchall()
                    if result:
                        entries = []
                        for row in result:
                            entry = ClanBattleBossPlayerEntry(
                                ClanBattleBossPlayerEntryId=row['clan_battle_boss_player_entry_id'],
                                ClanBattleBossEntryId=row['clan_battle_boss_entry_id'],
                                PlayerId=row['player_id'],
                                PlayerName=row['player_name'],
                                AttackType=row['attack_type'],
                                Damage=row['damage'],
                                IsDoneEntry=row['is_done_entry']
                            )
                            entries.append(entry)
                        return entries
                    return []
        except mariadb.Error as e:
            print(f"Database error: {e}")

    def get_single_book_by_message_id_and_player_id(self, message_id: int, player_id: int):
        try:
            with MariaDBConnectionPool() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        SELECT CBPE.clan_battle_boss_player_entry_id,
                               CBPE.clan_battle_boss_entry_id,
                               CBPE.player_id,
                               CBPE.player_name,
                               CBPE.attack_type,
                               CBPE.damage,
                               CBPE.is_done_entry
                        FROM clan_battle_boss_player_entry CBPE
                                 JOIN clan_battle_boss_entry CBE ON CBPE.clan_battle_boss_entry_id = CBE.clan_battle_boss_entry_id
                        WHERE CBE.message_id = ?
                          AND CBPE.player_id = ?
                          AND CBPE.is_done_entry = 0
                        """,
                        (message_id,
                         player_id)
                    )
                    result = cursor.fetchone()
                    if result:
                        return ClanBattleBossPlayerEntry(
                            ClanBattleBossPlayerEntryId=result['clan_battle_boss_player_entry_id'],
                            ClanBattleBossEntryId=result['clan_battle_boss_entry_id'],
                            PlayerId=result['player_id'],
                            PlayerName=result['player_name'],
                            AttackType=result['attack_type'],
                            Damage=result['damage'],
                            IsDoneEntry=result['is_done_entry']
                        )
                    return None
        except mariadb.Error as e:
            print(f"Database error: {e}")

    def delete_book_by_message_id_and_player_id(self, clan_battle_boss_player_entry_id: int):
        try:
            with MariaDBConnectionPool() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        DELETE
                        FROM clan_battle_boss_player_entry
                        WHERE clan_battle_boss_player_entry_id = ?
                        """,
                        (clan_battle_boss_player_entry_id,
                         )
                    )
                    conn.commit()
        except mariadb.Error as e:
            conn.rollback()
            print(f"Database error: {e}")

    def insert_clan_battle_boss_player_book_entry(self, clan_battle_boss_player_entry: ClanBattleBossPlayerEntry):
        try:
            with MariaDBConnectionPool() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        INSERT INTO KurikoneCbBot.clan_battle_boss_player_entry (clan_battle_boss_entry_id, player_id, player_name, attack_type, damage,
                                            is_done_entry)
                        VALUES (?, ?, ?, ?, ?, ?)
                        """,
                        (clan_battle_boss_player_entry.ClanBattleBossEntryId,
                         clan_battle_boss_player_entry.PlayerId,
                         clan_battle_boss_player_entry.PlayerName,
                         clan_battle_boss_player_entry.AttackType,
                         clan_battle_boss_player_entry.Damage,
                         clan_battle_boss_player_entry.IsDoneEntry)
                    )
                    conn.commit()
        except mariadb.Error as e:
            conn.rollback()
            print(f"Database error: {e}")

    def update_clan_battle_boss_player_done_entry(self, clan_battle_boss_player_entry: ClanBattleBossPlayerEntry):
        try:
            with MariaDBConnectionPool() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        UPDATE clan_battle_boss_player_entry 
                            SET damage = ?,
                                is_done_entry = 1
                        WHERE clan_battle_boss_player_entry_id = ?
                        """,
                        (clan_battle_boss_player_entry.Damage,
                         clan_battle_boss_player_entry.ClanBattleBossPlayerEntryId)
                    )
                    conn.commit()
        except mariadb.Error as e:
            conn.rollback()
            print(f"Database error: {e}")


class ClanBattlePeriodRepository:
    def __init__(self):
        self.pool = MariaDBConnectionPool()

    def get_current_running_clan_battle_period(self):
        try:
            with MariaDBConnectionPool() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        SELECT clan_battle_period_id,
                               clan_battle_period_name,
                               date_from,
                               date_to,
                               boss1_id,
                               boss2_id,
                               boss3_id,
                               boss4_id,
                               boss5_id
                        FROM clan_battle_period
                        WHERE SYSDATE() BETWEEN date_from AND date_to
                        """
                    )
                    result = cursor.fetchone()
                    if result:
                        return ClanBattlePeriod(
                            ClanBattlePeriodId=result['clan_battle_period_id'],
                            ClanBattlePeriodName=result['clan_battle_period_name'],
                            DateFrom=result['date_from'],
                            DateTo=result['date_to'],
                            Boss1Id=result['boss1_id'],
                            Boss2Id=result['boss2_id'],
                            Boss3Id=result['boss3_id'],
                            Boss4Id=result['boss4_id'],
                            Boss5Id=result['boss5_id']
                        )
                    return None
        except mariadb.Error as e:
            print(f"Database error: {e}")


class ClanBattleBossRepository:
    def __init__(self):
        self.pool = MariaDBConnectionPool()

    def get_one_by_clan_battle_boss_id(self, clan_battle_boss_id: int):
        try:
            with MariaDBConnectionPool() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        SELECT clan_battle_boss_id,
                               name,
                               description,
                               image_path,
                               position
                        FROM clan_battle_boss
                        WHERE clan_battle_boss_id = ?
                        """,
                        (clan_battle_boss_id,)
                    )
                    result = cursor.fetchone()
                    if result:
                        return ClanBattleBoss(
                            ClanBattleBossId=result['clan_battle_boss_id'],
                            Name=result['name'],
                            Description=result['description'],
                            ImagePath=result['image_path'],
                            Position=result['position']
                        )
                    return None
        except mariadb.Error as e:
            print(f"Database error: {e}")

class ClanBattleBossHealthRepository:
    def __init__(self):
        self.pool = MariaDBConnectionPool()

    def get_one_by_position_and_round(self, position: int, round: int):
        try:
            with MariaDBConnectionPool() as conn:
                with conn.cursor(dictionary=True) as cursor:
                    cursor.execute(
                        """
                        SELECT clan_battle_boss_health_id,
                               position,
                               round_from,
                               round_to,
                               health
                        FROM clan_battle_boss_health
                        WHERE position = ?
                        AND ? BETWEEN round_from AND round_to
                        """,
                        (position, round,)
                    )
                    result = cursor.fetchone()
                    if result:
                        return ClanBattleBossHealth(
                            ClanBattleBossHealthId=result['clan_battle_boss_health_id'],
                            Position=result['position'],
                            RoundFrom=result['round_from'],
                            RoundTo=result['round_to'],
                            Health=result['health']
                        )
                    return None
        except mariadb.Error as e:
            print(f"Database error: {e}")