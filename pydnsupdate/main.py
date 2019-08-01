from pydnsupdate import aws53, dbdata, homedns, snmpdata

__author__ = 'tlo'


def main():
    db = dbdata.DbData()
    rows = db.get_current()

    router_name = rows[0][0]

    snmp_session = snmpdata.get_session(router_name)

    saved_address_list_ipv4 = (rows[0][4] + ':' + rows[1][4]).split(':')
    saved_address_list_ipv6 = (rows[2][4] + '^' + rows[3][4]).split('^')

    saved_address_list_ipv4.sort()
    saved_address_list_ipv6.sort()

    router_address_list_ipv4 = snmpdata.get_ip4_addresses(snmp_session)
    for ipv4 in router_address_list_ipv4:

        if ipv4.startswith('127') or ipv4.startswith('198') or ipv4.startswith('192'):
            router_address_list_ipv4.remove(ipv4)

    router_address_list_ipv4.sort()

    router_address_list_ipv6 = snmpdata.get_ip6_addresses(snmp_session)
    router_address_list_ipv6.sort()

    router_id = rows[0][2]

    for idx in range(0, 2):
        print(f"{router_name}'s listed IP: {saved_address_list_ipv4[idx]} assigned IP {router_address_list_ipv4[idx]}")
        print(f"{router_name}'s listed IP: {saved_address_list_ipv6[idx]} assigned IP {router_address_list_ipv6[idx]}")

    for address4 in router_address_list_ipv4:
        if address4 not in saved_address_list_ipv4:
            aws53.update(db, router_address_list_ipv4, 'A')
            homedns.update(db, router_name, router_address_list_ipv4, 'A')
            db.insert_new(router_id, router_address_list_ipv4, 'A')

    for address6 in router_address_list_ipv6:
        if address6 not in saved_address_list_ipv6:
            aws53.update(db, router_address_list_ipv6, 'AAAA')
            homedns.update(db, router_name, router_address_list_ipv6, 'AAAA')
            db.insert_new(router_id, router_address_list_ipv6, 'AAAA')

    db.close()


if __name__ == '__main__':
    main()
