CREATE TABLE `afkMessages` (
  `userId` varchar(20) NOT NULL,
  `messageId` varchar(20) NOT NULL,
  `channelId` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`userId`,`messageId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE `autopublish` (
  `channelId` varchar(20) NOT NULL,
  PRIMARY KEY (`channelId`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
