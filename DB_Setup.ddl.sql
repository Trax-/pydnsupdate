DROP TABLE IF EXISTS AWS_Route53_values;
DROP TABLE IF EXISTS AWS_Route53;
DROP TABLE IF EXISTS AWS_Route53_zones;

CREATE TABLE AWS_Route53_zones
(
  record_id    MEDIUMINT UNSIGNED    AUTO_INCREMENT UNIQUE NOT NULL,
  zone_id      VARCHAR(26),
  name         VARCHAR(12)                                 NOT NULL,
  record_count TINYINT(4)                                  NOT NULL,
  private_zone ENUM('TRUE', 'FALSE') DEFAULT 'False',
  comment      VARCHAR(50)
);
CREATE INDEX record_id_idx ON AWS_Route53_zones (record_id);
CREATE INDEX zone_id ON AWS_Route53_zones (zone_id);

CREATE TABLE AWS_Route53
(
  record_id      MEDIUMINT(8) UNSIGNED AUTO_INCREMENT PRIMARY KEY                                         NOT NULL
  COMMENT 'hostname record id',
  name           VARCHAR(60)                                                                              NOT NULL,
  type           ENUM('SOA', 'A', 'TXT', 'NS', 'CNAME', 'MX', 'PTR', 'SRV', 'SPF', 'AAAA')                NOT NULL
  COMMENT 'RR type',
  ttl            INT(11),
  hosted_zone_id MEDIUMINT(8) UNSIGNED                                                                    NOT NULL
  COMMENT 'Hosted zone id each domain',
  CONSTRAINT AWS_Route53_ibfk_1 FOREIGN KEY (hosted_zone_id) REFERENCES AWS_Route53_zones (record_id)
);
CREATE INDEX hosted_zone_id ON AWS_Route53 (hosted_zone_id);
CREATE INDEX record_id ON AWS_Route53 (record_id);

CREATE TABLE AWS_Route53_values
(
  value_id      INT(11) AUTO_INCREMENT PRIMARY KEY   NOT NULL,
  AWS_record_id MEDIUMINT(8) UNSIGNED                NOT NULL,
  value         VARCHAR(256)                         NOT NULL,
  last_update   DATETIME,
  CONSTRAINT AWS_Route53_values_ibfk_1 FOREIGN KEY (AWS_record_id) REFERENCES AWS_Route53 (record_id)
);
CREATE INDEX AWS_record_id ON AWS_Route53_values (AWS_record_id);

CREATE TABLE DNS_Park
(
  record_id   MEDIUMINT(8) UNSIGNED PRIMARY KEY NOT NULL
  COMMENT 'DNS Park host id',
  domain_id   INT(11)                           NOT NULL
  COMMENT 'DNS PArk domain id',
  rname       VARCHAR(54)                       NOT NULL
  COMMENT 'host name to update',
  ttl         INT(11)                           NOT NULL
  COMMENT 'Time to live value for host',
  rtype       VARCHAR(10)                       NOT NULL
  COMMENT 'DNS Recod type indicator',
  rdata       VARCHAR(256)                      NOT NULL
  COMMENT 'Mostly the ip address but depends on the rtype above',
  dynamic     ENUM('N', 'Y') DEFAULT 'N'        NOT NULL
  COMMENT 'Dynamically updated hosts',
  readonly    ENUM('N', 'Y')                    NOT NULL
  COMMENT 'Y or N to indicate writeable',
  active      ENUM('N', 'Y')                    NOT NULL
  COMMENT 'Most likely all records are active but ...',
  ordername   VARCHAR(43) COMMENT 'Not sure what this field is about',
  auth        ENUM('1')                         NOT NULL
  COMMENT 'No clue but seems to be always 1',
  last_update DATETIME                          NOT NULL
  COMMENT 'Date of the last update'
);
CREATE INDEX routers_ordername_idx ON DNS_Park (ordername);

CREATE TABLE ip_address
(
  address_id INT(11) PRIMARY KEY NOT NULL
  COMMENT 'Table primary key',
  router_id  INT(11)             NOT NULL
  COMMENT 'Router key',
  ip_address VARCHAR(50)         NOT NULL
  COMMENT 'Device address',
  updated    DATETIME            NOT NULL
  COMMENT 'Date/Time of last update',
  active     ENUM('Y', 'N'),
  CONSTRAINT ip_address_router_id FOREIGN KEY (router_id) REFERENCES routers (router_id)
);
CREATE UNIQUE INDEX address_id ON ip_address (address_id);
CREATE UNIQUE INDEX ip_address ON ip_address (ip_address);
CREATE INDEX ip_address_router_id_idx ON ip_address (router_id);

CREATE TABLE router_names
(
  name_id   MEDIUMINT(8) UNSIGNED PRIMARY KEY NOT NULL
  COMMENT 'primary key',
  router_id INT(11)                           NOT NULL
  COMMENT 'Router key',
  ext_name  VARCHAR(20)                       NOT NULL
  COMMENT 'Names to be updated'
);
CREATE UNIQUE INDEX name_id ON router_names (name_id);

CREATE TABLE routers
(
  router_id INT(11) PRIMARY KEY NOT NULL
  COMMENT 'Table Primary Key',
  name      VARCHAR(10)         NOT NULL
  COMMENT 'DNS name of router',
  command   VARCHAR(30)         NOT NULL
  COMMENT 'Command string to obtain address'
);
CREATE UNIQUE INDEX router_id ON routers (router_id);

CREATE TABLE service_api
(
  service_table_name VARCHAR(50)             NOT NULL
  COMMENT 'API Service provider name',
  api_key_id         VARCHAR(50) PRIMARY KEY NOT NULL
  COMMENT 'API key id',
  api_password       VARCHAR(50)             NOT NULL
  COMMENT 'API password or token',
  base_url           VARCHAR(50)             NOT NULL
  COMMENT 'Base url'
);

DROP PROCEDURE IF EXISTS D_DNS.do_aws_insert;
CREATE DEFINER =`tlo`@`%` PROCEDURE `do_aws_insert`(IN p_zone_id VARCHAR(26), IN p_name VARCHAR(60), IN p_ttl INT,
                                                    IN p_type    ENUM('SOA', 'A', 'TXT', 'NS', 'CNAME', 'MX', 'PTR', 'SRV', 'SPF', 'AAAA'),
                                                    IN p_value   VARCHAR(256))
  BEGIN
    SET @zone_id = (SELECT record_id
                    FROM AWS_Route53_zones
                    WHERE zone_id = p_zone_id);

    IF p_ttl = 0
    THEN
      INSERT IGNORE INTO AWS_Route53 (name, type, hosted_zone_id) VALUES (p_name, p_type, @zone_id);
    ELSE
      INSERT IGNORE INTO AWS_Route53 (name, type, ttl, hosted_zone_id) VALUES (p_name, p_type, p_ttl, @zone_id);
    END IF;

    SET @last_id = (SELECT LAST_INSERT_ID());

    INSERT IGNORE INTO AWS_Route53_values (AWS_record_id, value) VALUES (@last_id, p_value);

  END;

DROP PROCEDURE IF EXISTS D_DNS.do_internal_update;
CREATE DEFINER =`tlo`@`%` PROCEDURE `do_internal_update`(IN p_router_id INT, IN p_ip_address VARCHAR(50))
  BEGIN
    SET @date_now = NOW();

    UPDATE ip_address
    SET active = 'N'
    WHERE router_id = p_ip_address;

    INSERT INTO ip_address (router_id, ip_address, updated, active) VALUES (p_router_id, p_ip_address, @date_now, 'Y');

  END;

CREATE
  ALGORITHM = UNDEFINED
  DEFINER = `tlo`@`%`
  SQL SECURITY DEFINER
VIEW `latest` AS
  SELECT
    `routers`.`name`          AS `name`,
    `routers`.`command`       AS `command`,
    `routers`.`router_id`     AS `router_id`,
    `routers`.`OID`           AS `oid`,
    `ip_address`.`ip_address` AS `address`,
    `ip_address`.`updated`    AS `updated`
  FROM
    (`routers`
      JOIN `ip_address` ON ((`routers`.`router_id` = `ip_address`.`router_id`)))
  WHERE
    (`ip_address`.`active` = 'Y')