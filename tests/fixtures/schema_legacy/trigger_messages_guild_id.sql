CREATE TABLE `triggerMessages` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `guildId` varchar(20) DEFAULT NULL,
  `trigger` varchar(128) DEFAULT NULL,
  `response` varchar(1024) DEFAULT NULL,
  `caseSensitive` tinyint(1) DEFAULT 0,
  PRIMARY KEY (`id`),
  KEY `idx_guild` (`guildId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `triggerMessagesChannel` (
  `guild_id` varchar(20) NOT NULL,
  `channel_id` varchar(20) NOT NULL,
  `triggerId` int(11) NOT NULL,
  PRIMARY KEY (`guild_id`, `channel_id`, `triggerId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
