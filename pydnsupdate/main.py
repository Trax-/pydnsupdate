from pydnsupdate import aws53, dbdata, homedns, snmpdata

__author__ = 'tlo'


def main():
    db = dbdata.DbData()
    rows = db.get_current()

    snmp_session = snmpdata.get_session(rows[0][0])

    saved_address4 = (rows[0][4] + ':' + rows[1][4]).split(':')
    saved_address6 = (rows[2][4] + '^' + rows[3][4]).split('^')

    saved_address4.sort()
    saved_address6.sort()

    router_address4 = snmpdata.get_ip4_addresses(snmp_session)
    for ipv4 in router_address4:

        if ipv4.startswith('127') or ipv4.startswith('198') or ipv4.startswith('192'):
            router_address4.remove(ipv4)

    router_address4.sort()

    router_address6 = snmpdata.get_ip6_addresses(snmp_session)
    router_address6.sort()

    name = rows[0][0]
    router_id = rows[0][2]

    for idx in range(0, 2):
        print(f"{name}'s listed IP: {saved_address4[idx]} assigned IP {router_address4[idx]}")
        print(f"{name}'s listed IP: {saved_address6[idx]} assigned IP {router_address6[idx]}")

    if saved_address4 != router_address4:
        aws53.update(db, name, router_address4)
        homedns.update(db, name, router_address4)
        db.insert_new(router_id, router_address4)

    if saved_address6 != router_address6:
        aws53.update(db, name, router_address6, 6)
        homedns.update(db, name, router_address6, 6)
        db.insert_new(router_id, router_address6, 6)


    db.close()


def testroute():
    name = 'adsl2'
    new_address = '98.1.2.4'

    fred = dbdata.DbData()

    names = fred.get_names_to_update_aws(name, new_address)

    for name in names:
        print(name)


if __name__ == '__main__':
    main()
