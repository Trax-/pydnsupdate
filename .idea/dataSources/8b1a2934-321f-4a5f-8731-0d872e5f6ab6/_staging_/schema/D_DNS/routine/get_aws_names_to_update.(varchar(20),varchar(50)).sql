CREATE PROCEDURE get_aws_names_to_update(IN p_name VARCHAR(50), IN p_new_address VARCHAR(50))
  BEGIN
    SELECT
      AWS_Route53.name AS host,
      type,
      ttl,
      v.value_id,
      zone_id
    FROM AWS_Route53_values v
      JOIN AWS_Route53 ON record_id = AWS_record_id
      JOIN AWS_Route53_zones ON hosted_zone_id = AWS_Route53_zones.record_id
    WHERE type = 'A' AND LEFT(AWS_Route53.name, 3) IN (SELECT LEFT(ext_name, 3)
                                                       FROM router_names
                                                         JOIN routers ON routers.router_id = router_names.router_id
                                                       WHERE routers.name = p_name) AND value != p_new_address
          AND LEFT(value, 5) != 'ALIAS';
  END;
