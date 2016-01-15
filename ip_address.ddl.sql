DROP SCHEMA IF EXISTS D_DNS;
CREATE SCHEMA IF NOT EXISTS D_DNS;

USE D_DNS;

DROP TABLE IF EXISTS D_DNS.routers;
CREATE TABLE IF NOT EXISTS D_DNS.routers (
  router_id INTEGER AUTO_INCREMENT UNIQUE NOT NULL
  COMMENT 'Table Primary Key',
  name      VARCHAR(10)                   NOT NULL
  COMMENT 'DNS name of router',
  command   VARCHAR(30)                   NOT NULL
  COMMENT 'Command string to obtain address',
  PRIMARY KEY (router_id)
)
  ENGINE = InnoDB;

DROP TABLE IF EXISTS D_DNS.router_names;
CREATE TABLE D_DNS.router_names (
  name_id   MEDIUMINT(8) UNSIGNED AUTO_INCREMENT UNIQUE NOT NULL
  COMMENT 'primary key',
  router_id INTEGER                                     NOT NULL
  COMMENT 'Router key',
  ext_name  VARCHAR(20)                                 NOT NULL
  COMMENT 'Names to be updated',
  PRIMARY KEY (name_id)
)
  ENGINE InnoDB;

DROP TABLE IF EXISTS D_DNS.ip_address;
CREATE TABLE IF NOT EXISTS D_DNS.ip_address (
  address_id INTEGER AUTO_INCREMENT NOT NULL UNIQUE
  COMMENT 'Table primary key',
  router_id  INTEGER                NOT NULL
  COMMENT 'Router key',
  ip_address VARCHAR(50)            NOT NULL UNIQUE
  COMMENT 'Device address',
  updated    TIMESTAMP              NOT NULL
  COMMENT 'Date/Time of last update',
  PRIMARY KEY (address_id)
)
  ENGINE InnoDB;

DROP TABLE IF EXISTS D_DNS.service_api;
CREATE TABLE IF NOT EXISTS D_DNS.service_api (
  service_table_name VARCHAR(50) NOT NULL
  COMMENT 'API Service provider name',
  api_key_id         VARCHAR(50) NOT NULL
  COMMENT 'API key id',
  api_password       VARCHAR(50) NOT NULL
  COMMENT 'API password or token',
  base_url           VARCHAR(50) NOT NULL
  COMMENT 'Base url',
  PRIMARY KEY (api_key_id)
)
  ENGINE InnoDB;

DROP TABLE IF EXISTS D_DNS.DNS_Park;
CREATE TABLE IF NOT EXISTS D_DNS.DNS_Park (
  record_id   MEDIUMINT(8) UNSIGNED      NOT NULL
  COMMENT 'DNS Park host id',
  domain_id   INTEGER                    NOT NULL
  COMMENT 'DNS PArk domain id',
  rname       VARCHAR(54)                NOT NULL
  COMMENT 'host name to update',
  ttl         INTEGER                    NOT NULL
  COMMENT 'Time to live value for host',
  rtype       VARCHAR(10)                NOT NULL
  COMMENT 'DNS Recod type indicator',
  rdata       VARCHAR(256)               NOT NULL
  COMMENT 'Mostly the ip address but depends on the rtype above',
  dynamic     ENUM('N', 'Y') DEFAULT 'N' NOT NULL
  COMMENT 'Dynamically updated hosts',
  readonly    ENUM('N', 'Y')             NOT NULL
  COMMENT 'Y or N to indicate writeable',
  active      ENUM('N', 'Y')             NOT NULL
  COMMENT 'Most likely all records are active but ...',
  ordername   VARCHAR(43)
  COMMENT 'Not sure what this field is about',
  auth        ENUM('1')                  NOT NULL
  COMMENT 'No clue but seems to be always 1',
  last_update DATETIME                   NOT NULL
  COMMENT 'Date of the last update',
  PRIMARY KEY (record_id)
)
  ENGINE InnoDB;

DROP TABLE IF EXISTS D_DNS.AWS_Route53;
CREATE TABLE IF NOT EXISTS D_DNS.AWS_Route53 (
  record_id      MEDIUMINT UNSIGNED AUTO_INCREMENT UNIQUE                                  NOT NULL
  COMMENT 'hostname record id',
  name           VARCHAR(58)                                                               NOT NULL
  COMMENT 'host name',
  type           ENUM('SOA', 'A', 'TXT', 'NS', 'CNAME', 'MX', 'PTR', 'SRV', 'SPF', 'AAAA') NOT NULL
  COMMENT 'RR type',
  ttl            INTEGER                                                                   NOT NULL
  COMMENT 'Time to live value for host',
  hosted_zone_id MEDIUMINT UNSIGNED                                                        NOT NULL
  COMMENT 'Hosted zone id each domain',
  PRIMARY KEY (record_id)
)
  ENGINE InnoDB;

DROP TABLE IF EXISTS AWS_Route53_aliases;
CREATE TABLE IF NOT EXISTS AWS_Route53_aliases (
  alias_id               MEDIUMINT UNSIGNED    AUTO_INCREMENT UNIQUE NOT NULL,
  AWS_record_id          MEDIUMINT UNSIGNED                          NOT NULL,
  hosted_zone_id         VARCHAR(20)                                 NOT NULL,
  dns_name               VARCHAR(54),
  evaluate_target_health ENUM('TRUE', 'FALSE') DEFAULT 'FALSE',
  PRIMARY KEY (alias_id),
  INDEX (AWS_record_id),
  FOREIGN KEY (AWS_record_id)
  REFERENCES AWS_Route53 (record_id)
    ON UPDATE CASCADE
    ON DELETE CASCADE
)
  ENGINE InnoDB;

DROP TABLE IF EXISTS D_DNS.AWS_Route53_values;
CREATE TABLE IF NOT EXISTS D_DNS.AWS_Route53_values (
  value_id      INTEGER            NOT NULL AUTO_INCREMENT,
  AWS_record_id MEDIUMINT UNSIGNED NOT NULL,
  value         VARCHAR(256)       NOT NULL,
  PRIMARY KEY (value_id),
  INDEX (AWS_record_id),
  FOREIGN KEY (AWS_record_id)
  REFERENCES AWS_Route53 (record_id)
    ON UPDATE CASCADE
    ON DELETE RESTRICT
)
  ENGINE InnoDB;

DROP TABLE IF EXISTS D_DNS.AWS_Route53_zones;
CREATE TABLE IF NOT EXISTS D_DNS.AWS_Route53_zones (
  record_id    MEDIUMINT UNSIGNED    AUTO_INCREMENT UNIQUE NOT NULL,
  zone_id      VARCHAR(26) UNIQUE,
  name         VARCHAR(12)                                 NOT NULL,
  record_count TINYINT                                     NOT NULL,
  private_zone ENUM('True', 'False') DEFAULT 'False',
  comment      VARCHAR(50),
  PRIMARY KEY (record_id)
)
  ENGINE InnoDB;

ALTER TABLE D_DNS.DNS_Park
ADD INDEX routers_ordername_idx (ordername ASC);

ALTER TABLE D_DNS.ip_address
ADD INDEX ip_address_router_id_idx (router_id ASC);

ALTER TABLE D_DNS.ip_address
ADD CONSTRAINT ip_address_router_id FOREIGN KEY (router_id) REFERENCES D_DNS.routers (router_id)
  ON UPDATE CASCADE
  ON DELETE CASCADE;

ALTER TABLE D_DNS.AWS_Route53
ADD INDEX (hosted_zone_id),
ADD CONSTRAINT FOREIGN KEY (hosted_zone_id)
REFERENCES AWS_Route53_zones (record_id)
  ON UPDATE CASCADE
  ON DELETE CASCADE;


CREATE OR REPLACE
  ALGORITHM = UNDEFINED
  DEFINER = 'tlo'@'%'
  SQL SECURITY DEFINER
VIEW latest AS
  SELECT
    D_DNS.routers.name          AS 'name',
    D_DNS.routers.command       AS 'command',
    D_DNS.routers.router_id     AS 'router_id',
    D_DNS.ip_address.ip_address AS 'address',
    D_DNS.ip_address.updated    AS 'updated'
  FROM (D_DNS.routers
    JOIN D_DNS.ip_address ON D_DNS.routers.router_id = D_DNS.ip_address.router_id)
  WHERE D_DNS.routers.router_id IN (1, 2, 3)
  ORDER BY D_DNS.ip_address.updated DESC
  LIMIT 0, 3;

CREATE PROCEDURE do_aws_insert(IN p_zone_id VARCHAR(26), IN p_name VARCHAR(60), IN p_ttl INT,
                               IN p_type    ENUM('SOA', 'A', 'TXT', 'NS', 'CNAME', 'MX', 'PTR', 'SRV', 'SPF', 'AAAA'),
                               IN p_value   VARCHAR(256))

  BEGIN
    SET @zone_id = (SELECT record_id
                    FROM AWS_Route53_zones
                    WHERE zone_id = p_zone_id);

    INSERT INTO AWS_Route53 (name, type, ttl, hosted_zone_id) VALUES (p_name, p_type, p_ttl, @zone_id);

    SET @last_id = (SELECT LAST_INSERT_ID());

    INSERT INTO AWS_Route53_values (AWS_record_id, value) VALUES (@last_id, p_value);

  END;

CREATE PROCEDURE do_internal_update(IN p_router_id INT, IN p_ip_address VARCHAR(50))
  BEGIN
    SET @date_now = NOW();

    UPDATE ip_address
    SET active = 'N'
    WHERE active = 'Y';

    INSERT INTO ip_address (router_id, ip_address, updated, active) VALUES (p_router_id, p_ip_address, @date_now, 'Y');

  END;

# Initialize routers table data
INSERT INTO routers (name, command) VALUES ('cisco', 'ssh tlo@eclipse ./checkip');
INSERT INTO routers (name, command) VALUES ('adsl1', 'ssh tlo@apogee ./checkip');
INSERT INTO routers (name, command) VALUES ('adsl2', 'ssh tlo@dragon ./checkip');

# Initialize existing addresses
INSERT INTO ip_address (router_id, ip_address, updated) VALUES (1, '198.147.254.1', '2015-01-31 11:12:26');
INSERT INTO ip_address (router_id, ip_address, updated) VALUES (2, '198.147.254.65', '2015-01-31 11:12:26');
INSERT INTO ip_address (router_id, ip_address, updated) VALUES (3, '198.147.254.129', '2015-01-31 11:12:26');
INSERT INTO ip_address (router_id, ip_address, updated) VALUES (1, '96.33.83.189', '2015-01-31 13:12:03');
INSERT INTO ip_address (router_id, ip_address, updated) VALUES (2, '74.177.75.236', '2015-01-31 13:12:19');
INSERT INTO ip_address (router_id, ip_address, updated) VALUES (3, '74.177.75.149', '2015-01-31 13:12:29');

# Initialize API table
INSERT INTO service_api (service_table_name, api_key_id, api_password, base_url)
VALUES ('AWS_Route53', 'AKIAJ7QEQBCUO4IPYDSQ', 's982onKlwbKO/nr/sakvVsYrCOi/R1+8IuEqzfsM',
        'https://route53.amazonaws.com');

INSERT INTO service_api (service_table_name, api_key_id, api_password, base_url)
VALUES ('DNS_Park', 'AAb619912c519ef1786a6372f6e1ed77c5', '8a3786d1b9504086e8e3573642489c8caae03b3a',
        'https://api.dnspark.com/v2/dns/');

# Initialize Router names lookup table
INSERT INTO router_names (router_id, ext_name) VALUES (1, 'ns1');
INSERT INTO router_names (router_id, ext_name) VALUES (1, 'mx1');
INSERT INTO router_names (router_id, ext_name) VALUES (2, 'ns2');
INSERT INTO router_names (router_id, ext_name) VALUES (2, 'mx2');
INSERT INTO router_names (router_id, ext_name) VALUES (3, 'ns3');
INSERT INTO router_names (router_id, ext_name) VALUES (3, 'mx3');
INSERT INTO router_names (router_id, ext_name) VALUES (3, 'www');
INSERT INTO router_names (router_id, ext_name) VALUES (3, 'ocsnet.com');

