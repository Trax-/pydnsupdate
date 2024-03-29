import mariadb
from . import aws53

__author__ = 'tlo'


class DbData(object):
    def __init__(self):

        try:
            self.db = mariadb.connect(default_file='.pydnsupdate.cnf', force_ipv6=False)

        except mariadb.Error as err:
            print(f'Error connecting to the database {err}')
            quit()

        self.cursorquery = self.db.cursor()
        self.cursorinput = self.db.cursor()
        self.cursordelete = self.db.cursor()

        self._initialize_tables_aws()

    def _initialize_tables_aws(self):

        key, password, base_url = self.get_api_key('AWS_Route53')

        route53 = aws53.get_session_client(key, password)

        zones = aws53.list_hosted_zones(route53)

        zone_id = 0

        if self.get_zone_count() != len(zones['HostedZones']):
            self.insert_zone_aws(zones)

        for zone in zones['HostedZones']:

            self.cursorquery.callproc('get_db_zone_id', (zone['Id'],))
            for result in self.cursorquery.stored_results():
                if result.with_rows:
                    zone_id = result.fetchone()[0]

            db_row_count = self.get_row_count_by_zone_id(zone_id)
            aws_row_count = zone['ResourceRecordSetCount'] + 4  # Add 3 for NS records

            if zone_id == 1 or zone_id == 3:
                aws_row_count += 7  # Accounts for the different way AWS stores multi record recordsets

            if zone_id == 2:  # Add 1 more for MX record if ocsnet.com (zone_id=2)
                aws_row_count += 12

            if aws_row_count != db_row_count:

                if aws_row_count < db_row_count:
                    self.cursordelete.execute(f'DELETE FROM AWS_Route53 WHERE hosted_zone_id = {zone_id}')
                    self.db.commit()

                r_r_set = aws53.list_resource_record_sets(route53, zone['Id'])

                for record in r_r_set['ResourceRecordSets']:

                    try:
                        for rr in record['ResourceRecords']:
                            address = rr['Value']

                            self.cursorquery.callproc('do_aws_insert',
                                                      (zone_id, record['Name'], record['TTL'], record['Type'], address))
                            self.db.commit()
                    except KeyError:

                        at = record['AliasTarget']

                        address = f"ALIAS '{at['DNSName']}', ({at['HostedZoneId']})"

                        self.cursorquery.callproc('do_aws_insert',
                                                  (zone_id, record['Name'], 0, record['Type'], address))
                        self.db.commit()

    def check_table_empty(self, table, field):

        sql = f"SELECT {field} FROM {table} LIMIT 1"
        self.cursorquery.execute(sql)
        return self.cursorquery.rowcount != 1

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

    def get_names_to_update_aws(self, qtype):
        self.cursorquery.callproc('get_aws_names_to_update', (qtype,))
        for result in self.cursorquery.stored_results():
            if result.with_rows:
                return result.fetchall()
            else:
                return None

    def get_names_to_update_aws6(self):
        self.cursorquery.callproc('get_aws_names_to_update6')
        for result in self.cursorquery.stored_results():
            if result.with_rows:
                return result.fetchall()
            else:
                return None

    def get_names_to_update_internal(self, name):

        self.cursorquery.callproc('get_internal_names_to_update', (name,))
        for result in self.cursorquery.stored_results():
            if result.with_rows:
                return result.fetchall()
            else:
                return None

    def get_row_count(self, table, field):
        sql = f"SELECT COUNT({field}) FROM {table}"
        self.cursorquery.execute(sql)
        return self.cursorquery.fetchall()[0][0]

    def get_row_count_by_zone_id(self, zone_id):

        self.cursorquery.callproc('get_row_count_by_zone_id', (zone_id,))
        for result in self.cursorquery.stored_results():
            if result.with_rows:
                return result.fetchone()[0]
            else:
                return 0

    def get_zone_count(self):
        self.cursorquery.execute(
            "SELECT COUNT(zone_id) FROM AWS_Route53_zones")
        return self.cursorquery.fetchone()[0]

    def insert_zone_aws(self, zones):

        for zone in zones['HostedZones']:
            try:
                comment = zone['Config']['Comment']
            except KeyError:
                comment = ''

            sql = f"REPLACE INTO AWS_Route53_zones (zone_id, name, record_count, private_zone, comment) " \
                f"VALUES ('{zone['Id']}', '{zone['Name']}', {zone['ResourceRecordSetCount']}, " \
                f"'{zone['Config']['PrivateZone']}', '{comment}')"

            self.cursorinput.execute(sql)
            self.db.commit()

    def insert_new(self, router_id, new_address, ip_version):

        if ip_version == 'A':
            self.cursorquery.callproc('do_internal_update', (router_id, new_address[0], new_address[1]))
        else:
            self.cursorquery.callproc('do_internal_update6', (router_id, new_address))
        self.db.commit()

    def update_aws_values(self, name, router_address, last_update, addr_type):

        sql = f"SELECT record_id FROM AWS_Route53 WHERE name = '{name}' and type = '{addr_type}'"
        numrows = self.cursorquery.execute(sql)
        record = self.cursorquery.fetchall()
        counter = 0
        for address in router_address:
            sql = f"UPDATE AWS_Route53 SET value = '{address}'," \
                  f" last_update = '{last_update.strftime('%Y-%m-%d %H:%M:%S')}' WHERE " \
                  f"record_id = '{record[counter][0]}'"

            self.cursorinput.execute(sql)
            counter += 1
        self.db.commit()

    def close(self):
        self.cursorquery.close()
        self.cursorinput.close()
        self.cursordelete.close()
        self.db.close()
