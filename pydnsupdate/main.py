from pydnsupdate import aws53, dbdata, homedns, sshdata

__author__ = 'tlo'


def main():
    db = dbdata.DbData()
    rows = db.get_current()

    router_name = rows[0][0]
    saved_address_list = []

    for row in rows:
        saved_address_list.append(row[4])

    ssh_session = sshdata.get_client(router_name)
    router_address_list = sshdata.get_all_addresses(ssh_session)
    ssh_session.close()

    for ip_address in router_address_list:

        if ip_address.startswith('127') or ip_address.startswith('198') or ip_address.startswith('192'):
            router_address_list.remove(ip_address)

    router_id = rows[0][2]

    for idx in range(0, 4):
        print(f"{router_name}'s listed IP: {saved_address_list[idx]} assigned IP {router_address_list[idx]}")

    if router_address_list != saved_address_list:
        for address4 in router_address_list[0:2]:
            if address4 not in saved_address_list:
                aws53.update(db, address4, 'A')
                homedns.update(db, router_name, address4, 'A')
                db.insert_new(router_id, address4, 'A')

        for address6 in router_address_list[2:4]:
            if address6 not in saved_address_list:
                aws53.update(db, address6, 'AAAA')
                homedns.update(db, router_name, address6, 'AAAA')
                db.insert_new(router_id, address6, 'AAAA')

    db.close()


if __name__ == '__main__':
    main()
