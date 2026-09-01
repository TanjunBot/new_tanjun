CREATE TABLE IF NOT EXISTS `giveaway` (
    `guild_id` VARCHAR(20) NOT NULL,
    `title` VARCHAR(128) NOT NULL,
    `endtime` DATETIME NOT NULL,
    `ended` TINYINT(1) DEFAULT 0
) ENGINE=InnoDB;
