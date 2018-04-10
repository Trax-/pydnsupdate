import subprocess

from pydnsupdate import aws53, dbdata, homedns

__author__ = 'tlo'


def main():
    db = dbdata.DbData()
    rows = db.get_current()

    for (name, command, router_id, oid, address, updated) in rows:

        command += f" {name} {oid}"

        router_address = list(
            subprocess.check_output(command, shell=True, universal_newlines=True).rstrip().split())

        for i in range(len(router_address) - 1, 0, -1):
            test = str(router_address[i])
            if test.startswith('127') or test.startswith('198') or test.startswith('192'):
                router_address.remove(test)

        print(f"{name}'s listed IP: {address} assigned IP {router_address}")

        if address not in router_address:
            aws53.update(db, name, router_address)
            homedns.update(db, name, router_address)
            db.insert_new(router_id, router_address)

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
