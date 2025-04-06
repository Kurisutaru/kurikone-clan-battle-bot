from datetime import datetime

import attr
from enums import *


@attr.s
class Guild:
    GuildId: int = attr.ib(default=None)
    GuildName: str = attr.ib(default=None)


@attr.s
class Channel:
    ChannelId: int = attr.ib(default=None)
    GuildId: int = attr.ib(default=None)
    ChannelType: ChannelEnum = attr.ib(default=None, converter=lambda x: ChannelEnum[x] if isinstance(x, str) else x)


@attr.s
class ChannelMessage:
    ChannelId: int = attr.ib(default=None)
    MessageId: int = attr.ib(default=None)


@attr.s
class ClanBattleBossEntry:
    ClanBattleBossEntryId: int = attr.ib(default=None)
    MessageId: int = attr.ib(default=None)
    ClanBattlePeriodId: int = attr.ib(default=None)
    ClanBattleBossId: int = attr.ib(default=None)
    Name: str = attr.ib(default=None)
    Image: str = attr.ib(default=None)
    Round: int = attr.ib(default=None)
    CurrentHealth: int = attr.ib(default=None)
    MaxHealth: int = attr.ib(default=None)


@attr.s
class ClanBattleBossBook:
    ClanBattleBossBookId: int = attr.ib(default=None)
    ClanBattleBossEntryId: int = attr.ib(default=None)
    PlayerId: int = attr.ib(default=None)
    PlayerName: str = attr.ib(default=None)
    AttackType: AttackTypeEnum = attr.ib(default=None, converter=lambda x: AttackTypeEnum[x] if isinstance(x, str) else x)
    Damage: int = attr.ib(default=0)
    ClanBattleOverallEntryId: int = attr.ib(default=None)
    LeftoverTime: int = attr.ib(default=0)
    EntryDate: datetime = attr.ib(default=None)


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
class ClanBattleOverallEntry:
    ClanBattleOverallEntryId: int = attr.ib(default=None)
    GuildId: int = attr.ib(default=None)
    ClanBattlePeriodId: int = attr.ib(default=None)
    ClanBattleBossId: int = attr.ib(default=None)
    PlayerId: int = attr.ib(default=None)
    PlayerName: str = attr.ib(default=None)
    Round: int = attr.ib(default=None)
    AttackType: AttackTypeEnum = attr.ib(default=None,
                                         converter=lambda x: AttackTypeEnum[x] if isinstance(x, str) else x)
    Damage: int = attr.ib(default=None)
    LeftoverTime: int = attr.ib(default=None)
    OverallParentEntryId: int = attr.ib(default=None)
    EntryDate: datetime = attr.ib(default=None)


@attr.s
class ClanBattleLeftover:
    ClanBattleOverallEntryId: int = attr.ib(default=None)
    ClanBattleBossId: int = attr.ib(default=None)
    ClanBattleBossName: str = attr.ib(default=None)
    PlayerId: int = attr.ib(default=None)
    AttackType: AttackTypeEnum = attr.ib(default=None,
                                         converter=lambda x: AttackTypeEnum[x] if isinstance(x, str) else x)
    LeftoverTime: int = attr.ib(default=None)
    OverallParentEntryId: int = attr.ib(default=None)
