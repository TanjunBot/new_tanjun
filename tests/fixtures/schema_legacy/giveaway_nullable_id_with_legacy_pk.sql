CREATE TABLE IF NOT EXISTS `giveaway` (
    `giveaway_id` INT UNSIGNED NULL,
    `giveawayId` INT UNSIGNED NOT NULL AUTO_INCREMENT,
    `guildId` VARCHAR(20) NOT NULL,
    `channelId` VARCHAR(20) DEFAULT NULL,
    `title` VARCHAR(128) NOT NULL,
    `endtime` DATETIME NOT NULL,
    `ended` TINYINT(1) DEFAULT 0,
    PRIMARY KEY (`giveawayId`)
) ENGINE=InnoDB;

INSERT INTO `giveaway` (`giveawayId`, `guildId`, `title`, `endtime`)
VALUES (7, '111', 'Legacy giveaway', '2030-01-01 00:00:00');
