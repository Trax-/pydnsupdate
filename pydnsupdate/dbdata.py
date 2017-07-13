import mysql.connector
from mysql.connector import connect
from mysql.connector import errorcode

from . import dnspark, aws53

__author__ = 'tlo'


class DbData(object):
    def __init__(self):

        try:
            self.db = connect(option_files='/home/tlo/.my.cnf')

        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Bad password or Username")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Non existent database")
            else:
                print(err)

        self.cursorquery = self.db.cursor(buffered=True)
        self.cursorinput = self.db.cursor(buffered=True)
        self.cursordelete = self.db.cursor(buffered=True)

        if self.check_table_empty('DNS_Park', 'record_id'):
            self.initialize_table_dnspark()

        self.initialize_tables_aws()

    def initialize_table_dnspark(self):

        key, password, base_url = self.get_api_key('DNS_Park')

        sql = ("INSERT INTO DNS_Park (record_id, domain_id, rname, ttl, rtype, "
               "rdata, dynamic, readonly, active, ordername, auth, last_update) "
               "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")

        js_data = dnspark.get_domain_data(key, password, base_url, 'ocsnet.com')

        for record in js_data:
            try:
                dynamic = dnspark.get_record_data(key, password, base_url, record['record_id'])['dynamic']
            except KeyError:
                dynamic = 'N'

            data = (record['record_id'], record['domain_id'], record['rname'], record['ttl'], record['rtype'],
                    record['rdata'], dynamic, record['readonly'], record['active'], record['ordername'],
                    record['auth'],
                    record['last_update'].replace('T', ' ').replace('Z', ''))

            self.cursorinput.execute(sql, data)
            self.db.commit()

    def initialize_tables_aws(self):

        key, password, base_url = self.get_api_key('AWS_Route53')

        route53 = aws53.get_session_client(key, password)

        zones = aws53.list_hosted_zones(route53)

        if self.get_zone_count() != aws53.get_hosted_zone_count(route53):
            self.insert_zone_aws(zones)

        for zone in zones['HostedZones']:

            zone_id = zone['Id']

            if self.get_row_count_by_zone_id(zone_id) > zone['ResourceRecordSetCount']:
                continue

            r_r_set = aws53.list_resource_record_sets(route53, zone_id)

            for record in r_r_set['ResourceRecordSets']:

                try:
                    for rr in record['ResourceRecords']:
                        address = rr['Value']

                        self.cursorquery.execute("CALL do_aws_insert('{}', '{}', {}, '{}', '{}')".format(
                            zone_id, record['Name'], record['TTL'], record['Type'], address))

                        self.db.commit()
                except KeyError:

                    at = record['AliasTarget']

                    address = "ALIAS {} ({})".format(at['DNSName'], at['HostedZoneId'])

                    self.cursorquery.execute("CALL do_aws_insert('{}', '{}', {}, '{}', '{}')".format(
                        zone_id, record['Name'], 0, record['Type'], address))

                    self.db.commit()

    def check_table_empty(self, table, field):

        sql = f"SELECT {field} FROM {table} LIMIT 1"
        self.cursorquery.execute(sql)
        return self.cursorquery.rowcount != 1

    def delete_record_dnspark(self, record_id):

        sql = f"DELETE FROM DNS_Park WHERE record_id = {str(record_id)}"
        self.cursordelete.execute(sql)
        self.db.commit()

    def get_api_key(self, service_table):

        sql = f"SELECT api_key_id, api_password, base_url " \
              f"FROM service_api WHERE service_table_name = '{service_table}'"

        self.cursorquery.execute(sql)
        if self.cursorquery.rowcount == 0:
            return None
        else:
            return self.cursorquery.fetchall()[0]

    def get_current(self):
        self.cursorquery.execute("SELECT * FROM latest")
        return self.cursorquery.fetchall()

    def get_names_to_update_aws(self, name, new_address):

        sql = f"CALL get_aws_names_to_update('{name}', '{new_address}');"
        for result in self.cursorquery.execute(sql, multi=True):
            if result.with_rows:
                return self.cursorquery.fetchall()
            else:
                return None

    def get_names_to_update_dnspark(self, name, new_address):

        sql = f"SELECT rname, rtype, ttl, dynamic, record_id " \
              f"FROM dnspark_names " \
              f"WHERE name = '{name}' AND rdata != '{new_address}'"

        self.cursorquery.execute(sql)

        if self.cursorquery.rowcount == 0:
            return None
        else:
            return self.cursorquery.fetchall()

    def get_names_to_update_internal(self, name):

        sql = f"CALL get_internal_names_to_update('{name}')"

        self.cursorquery.execute(sql)

        if self.cursorquery.rowcount == 0:
            return None
        else:
            return self.cursorquery.fetchall()

    def get_row_count(self, table, field):
        sql = f"SELECT COUNT({field}) FROM {table}"
        self.cursorquery.execute(sql)
        return self.cursorquery.fetchall()[0][0]

    def get_row_count_by_zone_id(self, zone_id):

        sql = f"SELECT COUNT(a.record_id) " \
              f"FROM AWS_Route53 AS a " \
              f"JOIN AWS_Route53_zones AS b " \
              f"ON a.hosted_zone_id = b.record_id " \
              f"WHERE b.zone_id = '{zone_id}'"

        self.cursorquery.execute(sql)
        return self.cursorquery.fetchall()[0][0]

    def get_zone_count(self):
        self.cursorquery.execute("SELECT COUNT(zone_id) FROM AWS_Route53_zones")
        return self.cursorquery.fetchall()[0][0]

    def insert_zone_aws(self, zones):

        sql = ("REPLACE INTO AWS_Route53_zones (zone_id, name, record_count, private_zone, comment) "
               "VALUES (%s, %s, %s, %s, %s)")

        for zone in zones['HostedZones']:
            try:
                comment = zone['Config']['Comment']
            except KeyError:
                comment = ''

            data = (zone['Id'], zone['Name'], zone['ResourceRecordSetCount'],
                    str(zone['Config']['PrivateZone']), comment)

            self.cursorinput.execute(sql, data)
            self.db.commit()

    def insert_new(self, router_id, new_address):

        sql = f"CALL do_internal_update({router_id}, '{new_address}')"
        self.cursorquery.execute(sql)
        self.db.commit()

    def save_new_dnspark(self, record_id, router_address, last_update):

        sql = f"UPDATE DNS_Park SET rdata='{router_address}', last_update='{last_update}' WHERE record_id={record_id}"

        self.cursorinput.execute(sql)
        self.db.commit()

    def update_aws_values(self, value_id, router_address, last_update):

        sql = f"UPDATE AWS_Route53_values SET value = '{router_address}', last_update = '{last_update}' WHERE " \
              f"value_id = '{value_id}' "

        self.cursorinput.execute(sql)

    def close(self):
        self.cursorquery.close()
        self.cursorinput.close()
        self.cursordelete.close()
        self.db.close()
