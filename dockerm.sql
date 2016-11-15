/*
Navicat MySQL Data Transfer

Source Server         : Docker
Source Server Version : 50714
Source Host           : localhost:3306
Source Database       : dockerm

Target Server Type    : MYSQL
Target Server Version : 50714
File Encoding         : 65001

Date: 2016-11-15 21:01:51
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for containers
-- ----------------------------
DROP TABLE IF EXISTS `containers`;
CREATE TABLE `containers` (
  `container_id` varchar(128) NOT NULL,
  `container_name` varchar(128) NOT NULL,
  `image_id` varchar(128) NOT NULL,
  `host_id` varchar(128) NOT NULL,
  `host_name` varchar(128) NOT NULL,
  `create_time` datetime NOT NULL,
  `status` varchar(45) NOT NULL,
  `info` json NOT NULL,
  `follow` int(4) unsigned NOT NULL DEFAULT '0',
  PRIMARY KEY (`container_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------
-- Table structure for container_state
-- ----------------------------
DROP TABLE IF EXISTS `container_state`;
CREATE TABLE `container_state` (
  `id` int(255) unsigned NOT NULL AUTO_INCREMENT,
  `container_id` varchar(255) NOT NULL,
  `cpu_percent` float(255,2) NOT NULL,
  `memory_usage` varchar(255) NOT NULL,
  `memory_limit` varchar(255) NOT NULL,
  `memory_percent` float(255,2) NOT NULL,
  `tx_packets` varchar(255) NOT NULL,
  `tx_bytes` varchar(255) NOT NULL,
  `tx_dropped` varchar(255) NOT NULL,
  `tx_errors` varchar(255) NOT NULL,
  `tx_speed` varchar(255) NOT NULL,
  `rx_packets` varchar(255) NOT NULL,
  `rx_bytes` varchar(255) NOT NULL,
  `rx_dropped` varchar(255) NOT NULL,
  `rx_errors` varchar(255) NOT NULL,
  `rx_speed` varchar(255) NOT NULL,
  `collect_time` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `collect_time` (`collect_time`) USING BTREE,
  KEY `container_id` (`container_id`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=66131 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for hosts
-- ----------------------------
DROP TABLE IF EXISTS `hosts`;
CREATE TABLE `hosts` (
  `id` int(32) NOT NULL AUTO_INCREMENT,
  `host_name` varchar(128) NOT NULL,
  `host_id` varchar(128) NOT NULL,
  `host_ip` varchar(32) NOT NULL,
  `host_redis_port` varchar(16) NOT NULL,
  `host_redis_pw` varchar(128) NOT NULL,
  `create_time` datetime NOT NULL,
  PRIMARY KEY (`id`,`host_id`,`host_name`),
  UNIQUE KEY `cluster_ip` (`host_ip`),
  UNIQUE KEY `cluster_id` (`host_id`)
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for images
-- ----------------------------
DROP TABLE IF EXISTS `images`;
CREATE TABLE `images` (
  `id` int(128) unsigned NOT NULL AUTO_INCREMENT,
  `image_id` varchar(128) NOT NULL,
  `image_name` json NOT NULL,
  `host_id` varchar(128) NOT NULL,
  `host_name` varchar(128) NOT NULL,
  `create_time` datetime NOT NULL ON UPDATE CURRENT_TIMESTAMP,
  `info` json NOT NULL,
  `history` json NOT NULL,
  PRIMARY KEY (`id`,`image_id`)
) ENGINE=InnoDB AUTO_INCREMENT=3186 DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for logs
-- ----------------------------
DROP TABLE IF EXISTS `logs`;
CREATE TABLE `logs` (
  `container_id` int(11) NOT NULL,
  `container_name` varchar(255) NOT NULL,
  `container_log` longtext
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for networks
-- ----------------------------
DROP TABLE IF EXISTS `networks`;
CREATE TABLE `networks` (
  `network_id` varchar(255) NOT NULL,
  `network_name` varchar(255) NOT NULL,
  `host_id` varchar(255) NOT NULL,
  `host_name` varchar(255) NOT NULL,
  `network_info` json NOT NULL,
  PRIMARY KEY (`network_name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for operation_log
-- ----------------------------
DROP TABLE IF EXISTS `operation_log`;
CREATE TABLE `operation_log` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `operation_time` datetime NOT NULL,
  `operation_msg` varchar(255) NOT NULL,
  `operation_user` varchar(255) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for system_info
-- ----------------------------
DROP TABLE IF EXISTS `system_info`;
CREATE TABLE `system_info` (
  `host_id` varchar(255) NOT NULL,
  `system_release` varchar(255) NOT NULL,
  `docker_version` varchar(255) NOT NULL,
  `cpu_info` varchar(255) NOT NULL,
  `mem_info` varchar(255) NOT NULL,
  `disk_info` varchar(255) NOT NULL,
  `ip` json DEFAULT NULL,
  PRIMARY KEY (`host_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- ----------------------------
-- Table structure for user
-- ----------------------------
DROP TABLE IF EXISTS `user`;
CREATE TABLE `user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `username` varchar(128) DEFAULT NULL,
  `password` varchar(128) DEFAULT NULL,
  `level` int(11) DEFAULT NULL,
  `email` varchar(128) NOT NULL,
  `confirmed` tinyint(4) NOT NULL,
  PRIMARY KEY (`id`,`email`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB AUTO_INCREMENT=55 DEFAULT CHARSET=utf8;
