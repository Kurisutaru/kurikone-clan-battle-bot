from datetime import datetime

from attrs import field, define

from enums import *


@define
class Guild:
    GuildId: int = field(default=None)
    GuildName: str = field(default=None)


@define
class Channel:
    ChannelId: int = field(default=None)
    GuildId: int = field(default=None)
    ChannelType: ChannelEnum = field(default=None, converter=lambda x: ChannelEnum[x] if isinstance(x, str) else x)


@define
class ChannelMessage:
    ChannelId: int = field(default=None)
    MessageId: int = field(default=None)


@define
class ClanBattleBossEntry:
    ClanBattleBossEntryId: int = field(default=None)
    MessageId: int = field(default=None)
    ClanBattlePeriodId: int = field(default=None)
    ClanBattleBossId: int = field(default=None)
    Name: str = field(default=None)
    Image: str = field(default=None)
    Round: int = field(default=None)
    CurrentHealth: int = field(default=None)
    MaxHealth: int = field(default=None)


@define
class ClanBattleBossBook:
    ClanBattleBossBookId: int = field(default=None)
    ClanBattleBossEntryId: int = field(default=None)
    PlayerId: int = field(default=None)
    PlayerName: str = field(default=None)
    AttackType: AttackTypeEnum = field(converter=lambda x: AttackTypeEnum[x] if isinstance(x, str) else x, default=None)
    Damage: int = field(default=None)
    ClanBattleOverallEntryId: int = field(default=None)
    LeftoverTime: int = field(default=None)
    EntryDate: datetime = field(default=None)


@define
class ClanBattleBoss:
    ClanBattleBossId: int = field(default=None)
    Name: str = field(default=None)
    Description: str = field(default=None)
    ImagePath: str = field(default=None)
    Position: int = field(default=None)


@define
class ClanBattleBossHealth:
    ClanBattleBossHealthId: int = field(default=None)
    Position: int = field(default=None)
    RoundFrom: int = field(default=None)
    RoundTo: int = field(default=None)
    Health: int = field(default=None)


@define
class ClanBattlePeriod:
    ClanBattlePeriodId: int = field(default=None)
    ClanBattlePeriodName: str = field(default=None)
    DateFrom: datetime = field(default=None)
    DateTo: datetime = field(default=None)
    Boss1Id: int = field(default=None)
    Boss2Id: int = field(default=None)
    Boss3Id: int = field(default=None)
    Boss4Id: int = field(default=None)
    Boss5Id: int = field(default=None)


@define
class ClanBattleOverallEntry:
    ClanBattleOverallEntryId: int = field(default=None)
    GuildId: int = field(default=None)
    ClanBattlePeriodId: int = field(default=None)
    ClanBattleBossId: int = field(default=None)
    PlayerId: int = field(default=None)
    PlayerName: str = field(default=None)
    Round: int = field(default=None)
    AttackType: AttackTypeEnum = field(converter=lambda x: AttackTypeEnum[x] if isinstance(x, str) else x, default=None)
    Damage: int = field(default=None)
    LeftoverTime: int = field(default=None)
    OverallParentEntryId: int = field(default=None)
    EntryDate: datetime = field(default=None)


@define
class ClanBattleLeftover:
    ClanBattleOverallEntryId: int = field(default=None)
    ClanBattleBossId: int = field(default=None)
    ClanBattleBossName: str = field(default=None)
    PlayerId: int = field(default=None)
    AttackType: AttackTypeEnum = field(converter=lambda x: AttackTypeEnum[x] if isinstance(x, str) else x, default=None)
    LeftoverTime: int = field(default=None)
    OverallParentEntryId: int = field(default=None)
