CREATE DATABASE IF NOT EXISTS `workprofile_db`;

USE workprofile_db;

CREATE TABLE IF NOT EXISTS `Person` (
    `id` INT(11) NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(100) NOT NULL,       
    `email` VARCHAR(100) UNIQUE NOT NULL, 
    `phone` VARCHAR(20) NOT NULL,       
    PRIMARY KEY (`id`),
    UNIQUE KEY `id` (`id`)
) ENGINE=MyISAM AUTO_INCREMENT=10001;


INSERT INTO `Person` (`name`, `email`, `phone`) VALUES 
('John Doe', 'john.doe@example.com', '111-222-3333'),
('Jane Doe', 'jane.doe@example.com', '444-555-6666'),
('Jack Doe', 'jack.doe@example.com', '777-888-9999');