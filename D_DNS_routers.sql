INSERT INTO D_DNS.routers (router_id, name, command, OID, command2)
VALUES (1, 'rv320', 'snmpwalk -v2c -c public -OvQ ', 'IP-MIB::ipAdEntAddr');