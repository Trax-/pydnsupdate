import asyncio
import asyncssh
import sys

from pydnsupdate import aws53, dbdata, homedns

__author__ = 'tlo'


def main():
    db = dbdata.DbData()
    rows = db.get_current()

    router_name = rows[0][0]
    saved_address_list = []

    for row in rows:
        saved_address_list.append(row[4])

    try:
        router_address_list = asyncio.get_event_loop().run_until_complete(run_client(router_name))
    except (OSError, asyncssh.Error) as exc:
        sys.exit('SSH connection failed: ' + str(exc))

    # ssh_session = sshdata.get_client(router_name)
    # router_address_list = sshdata.get_all_addresses(ssh_session)
    # ssh_session.close()

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
                aws53.update(db, router_address_list[2:4], 'AAAA')
                homedns.update(db, router_name, address6, 'AAAA')
                db.insert_new(router_id, address6, 'AAAA')

    db.close()


async def run_client(router_name):
    async with asyncssh.connect(router_name, username='ocelot') as conn:
        result = await conn.run('./addresses.sh', check=True)
        result = result.stdout.split('\n')
        del result[4]
        return result


if __name__ == '__main__':
    main()
