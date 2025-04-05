CREATE DATABASE IF NOT EXISTS KurikoneCbBot;

CREATE OR REPLACE TABLE KurikoneCbBot.clan_battle_boss_entry
(
    clan_battle_boss_entry_id BIGINT UNSIGNED AUTO_INCREMENT
        PRIMARY KEY,
    message_id                BIGINT UNSIGNED NOT NULL,
    boss_id                   BIGINT UNSIGNED NOT NULL,
    name                      VARCHAR(2000)   NOT NULL,
    image                     VARCHAR(2000)   NOT NULL,
    round                     BIGINT UNSIGNED NOT NULL,
    current_health            BIGINT UNSIGNED NOT NULL,
    max_health                BIGINT UNSIGNED NOT NULL
);

CREATE OR REPLACE TABLE KurikoneCbBot.clan_battle_boss_player_entry
(
    clan_battle_boss_player_entry_id BIGINT UNSIGNED AUTO_INCREMENT
        PRIMARY KEY,
    clan_battle_boss_entry_id        BIGINT UNSIGNED NOT NULL,
    player_id                        BIGINT UNSIGNED NOT NULL,
    player_name                      VARCHAR(2000)   NOT NULL,
    attack_type                      VARCHAR(10)     NOT NULL,
    damage                           BIGINT UNSIGNED NOT NULL,
    is_done_entry                    TINYINT(1)      NOT NULL
);

CREATE OR REPLACE TABLE KurikoneCbBot.channel_message
(
    channel_id BIGINT UNSIGNED PRIMARY KEY,
    message_id BIGINT UNSIGNED NOT NULL
);

CREATE OR REPLACE TABLE KurikoneCbBot.guild_channel
(
    guild_id              BIGINT UNSIGNED NOT NULL
        PRIMARY KEY,
    category_id           BIGINT UNSIGNED NOT NULL,
    report_channel_id     BIGINT UNSIGNED NOT NULL,
    boss_1_channel_id     BIGINT UNSIGNED NOT NULL,
    boss_2_channel_id     BIGINT UNSIGNED NOT NULL,
    boss_3_channel_id     BIGINT UNSIGNED NOT NULL,
    boss_4_channel_id     BIGINT UNSIGNED NOT NULL,
    boss_5_channel_id     BIGINT UNSIGNED NOT NULL,
    tl_shifter_channel_id BIGINT UNSIGNED NOT NULL
);


CREATE OR REPLACE TABLE KurikoneCbBot.clan_battle_boss
(
    clan_battle_boss_id int auto_increment
        primary key,
    name                varchar(250) not null,
    description         varchar(250) null,
    image_path          varchar(250) not null,
    position            int          not null
);


CREATE OR REPLACE TABLE KurikoneCbBot.clan_battle_period
(
    clan_battle_period_id   INT AUTO_INCREMENT
        PRIMARY KEY,
    clan_battle_period_name VARCHAR(2000) NOT NULL,
    date_from               DATETIME      NOT NULL,
    date_to                 DATETIME      NOT NULL,
    boss1_id                INT           NOT NULL,
    boss2_id                INT           NOT NULL,
    boss3_id                INT           NOT NULL,
    boss4_id                INT           NOT NULL,
    boss5_id                INT           NOT NULL
);


CREATE OR REPLACE TABLE KurikoneCbBot.clan_battle_boss_health
(
    clan_battle_boss_health_id INT AUTO_INCREMENT
        PRIMARY KEY,
    position                   INT             NOT NULL,
    round_from                 INT             NOT NULL,
    round_to                   INT             NOT NULL,
    health                     BIGINT UNSIGNED NOT NULL
);

CREATE OR REPLACE TABLE KurikoneCbBot.clan_battle_overall_player_entry
(
    clan_battle_overall_player_entry INT AUTO_INCREMENT
        PRIMARY KEY,
    clan_battle_period_id            INT      NOT NULL,
    player_id                        DATETIME NOT NULL,
    player_name                      DATETIME NOT NULL,
    position                         INT      NOT NULL,
    damage                           INT      NOT NULL,
    is_leftover                      BOOL     NOT NULL,
    parent_cb_overall_id             INT      NULL
);