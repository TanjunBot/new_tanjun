CREATE TABLE IF NOT EXISTS `reports` (
    `id` INT AUTO_INCREMENT,
    `guild_id` VARCHAR(20),
    `user_id` VARCHAR(20),
    `reporterId` VARCHAR(20),
    `reason` VARCHAR(1024),
    PRIMARY KEY (`id`)
) ENGINE=InnoDB;
