from datetime import datetime
from enum import Enum

import attr


@attr.s
class GuildChannel:
    GuildId: int = attr.ib(default=None)
    CategoryId: int = attr.ib(default=None)
    ReportChannelId: int = attr.ib(default=None)
    Boss1ChannelId: int = attr.ib(default=None)
    Boss2ChannelId: int = attr.ib(default=None)
    Boss3ChannelId: int = attr.ib(default=None)
    Boss4ChannelId: int = attr.ib(default=None)
    Boss5ChannelId: int = attr.ib(default=None)
    TlShifterChannelId: int = attr.ib(default=None)


@attr.s
class ChannelMessage:
    ChannelId: int = attr.ib(default=None)
    MessageId: int = attr.ib(default=None)


@attr.s
class ClanBattleBossEntry:
    ClanBattleBossEntryId: int = attr.ib(default=None)
    MessageId: int = attr.ib(default=None)
    BossId: int = attr.ib(default=None)
    Name: str = attr.ib(default=None)
    Image: str = attr.ib(default=None)
    Round: int = attr.ib(default=None)
    CurrentHealth: int = attr.ib(default=None)
    MaxHealth: int = attr.ib(default=None)


@attr.s
class ClanBattleBossPlayerEntry:
    ClanBattleBossPlayerEntryId: int = attr.ib(default=None)
    ClanBattleBossEntryId: int = attr.ib(default=None)
    PlayerId: int = attr.ib(default=None)
    PlayerName: str = attr.ib(default=None)
    AttackType: str = attr.ib(default=None)
    Damage: int = attr.ib(default=None)
    IsDoneEntry: bool = attr.ib(default=None)


@attr.s
class ClanBattleBoss:
    ClanBattleBossId: int = attr.ib(default=None)
    Name: str = attr.ib(default=None)
    Description: str = attr.ib(default=None)
    ImagePath: str = attr.ib(default=None)
    Position: int = attr.ib(default=None)


@attr.s
class ClanBattleBossHealth:
    ClanBattleBossHealthId: int = attr.ib(default=None)
    Position: int = attr.ib(default=None)
    RoundFrom: int = attr.ib(default=None)
    RoundTo: int = attr.ib(default=None)
    Health: int = attr.ib(default=None)


@attr.s
class ClanBattlePeriod:
    ClanBattlePeriodId: int = attr.ib(default=None)
    ClanBattlePeriodName: str = attr.ib(default=None)
    DateFrom: datetime = attr.ib(default=None)
    DateTo: datetime = attr.ib(default=None)
    Boss1Id: int = attr.ib(default=None)
    Boss2Id: int = attr.ib(default=None)
    Boss3Id: int = attr.ib(default=None)
    Boss4Id: int = attr.ib(default=None)
    Boss5Id: int = attr.ib(default=None)


@attr.s
class ClanBattleOverallPlayerEntry:
    ClanBattleOverallPlayerEntryId: int = attr.ib(default=None)
    ClanBattlePeriodId: int = attr.ib(default=None)
    PlayerId: int = attr.ib(default=None)
    PlayerName: str = attr.ib(default=None)
    Position: int = attr.ib(default=None)
    Damage: int = attr.ib(default=None)
    IsLeftover: bool = attr.ib(default=None)
    ParentCbOverallId: int = attr.ib(default=None)


class BookType(Enum):
    BOOK = 0
    DONE = 1


# Enums for better readability
class Emoji(Enum):
    PATK = "🥊"
    MATK = "📗"
    CANCEL = "❌"
    DONE = "✅"
    BOOK = "⚔️"
    ENTRY = "📝"
    FINISH = "🏁"
