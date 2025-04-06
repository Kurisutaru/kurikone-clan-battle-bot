create table KurikoneCbBot.channel_message
(
    channel_id bigint unsigned not null
        primary key,
    message_id bigint unsigned not null
);

create table KurikoneCbBot.clan_battle_boss
(
    clan_battle_boss_id int auto_increment
        primary key,
    name                varchar(250) not null,
    description         varchar(250) null,
    image_path          varchar(250) not null,
    position            int          not null
);

create table KurikoneCbBot.clan_battle_boss_book
(
    clan_battle_boss_book_id     bigint unsigned auto_increment
        primary key,
    clan_battle_boss_entry_id    bigint unsigned not null,
    player_id                    bigint unsigned not null,
    player_name                  varchar(2000)   not null,
    attack_type                  varchar(10)     not null,
    damage                       bigint unsigned not null,
    clan_battle_overall_entry_id int             null,
    entry_date                   datetime        not null
);

create table KurikoneCbBot.clan_battle_boss_data
(
    clan_battle_boss_data int auto_increment
        primary key,
    clan_battle_period_id int             not null,
    clan_battle_boss_id   int             not null,
    health1               bigint unsigned not null,
    health2               bigint unsigned not null,
    health3               bigint unsigned not null
);

create table KurikoneCbBot.clan_battle_boss_entry
(
    clan_battle_boss_entry_id bigint unsigned auto_increment
        primary key,
    message_id                bigint unsigned not null,
    boss_id                   bigint unsigned not null,
    name                      varchar(2000)   not null,
    image                     varchar(2000)   not null,
    round                     bigint unsigned not null,
    current_health            bigint unsigned not null,
    max_health                bigint unsigned not null
);

create table KurikoneCbBot.clan_battle_boss_health
(
    clan_battle_boss_health_id int auto_increment
        primary key,
    position                   int             not null,
    round_from                 int             not null,
    round_to                   int             not null,
    health                     bigint unsigned not null
);

create table KurikoneCbBot.clan_battle_overall_entry
(
    clan_battle_overal_entry_id int             not null
        primary key,
    guild_id                    bigint unsigned not null,
    clan_battle_period_id       int             not null,
    player_id                   datetime        not null,
    player_name                 datetime        not null,
    boss_id                     int             not null,
    round                       int             not null,
    damage                      int             not null,
    attack_type                 varchar(20)     not null,
    leftover_time               int             null,
    overall_parent_entry_id     int             null,
    entry_date                  datetime        not null
);

create table KurikoneCbBot.clan_battle_period
(
    clan_battle_period_id   int auto_increment
        primary key,
    clan_battle_period_name varchar(2000) not null,
    date_from               datetime      not null,
    date_to                 datetime      not null,
    boss1_id                int           not null,
    boss2_id                int           not null,
    boss3_id                int           not null,
    boss4_id                int           not null,
    boss5_id                int           not null
);

create table KurikoneCbBot.guild_channel
(
    guild_id              bigint unsigned not null
        primary key,
    category_id           bigint unsigned not null,
    report_channel_id     bigint unsigned not null,
    boss_1_channel_id     bigint unsigned not null,
    boss_2_channel_id     bigint unsigned not null,
    boss_3_channel_id     bigint unsigned not null,
    boss_4_channel_id     bigint unsigned not null,
    boss_5_channel_id     bigint unsigned not null,
    tl_shifter_channel_id bigint unsigned not null
);

create table KurikoneCbBot.master_boss_data
(
    boss_id               bigint unsigned auto_increment
        primary key,
    clan_battle_period_id int             not null,
    name                  varchar(2000)   not null,
    image                 varchar(2000)   not null,
    position              bigint unsigned not null,
    health1               bigint unsigned not null,
    health2               bigint unsigned not null,
    health3               bigint unsigned not null
);

