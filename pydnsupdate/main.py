import subprocess

from pydnsupdate import aws53, dbdata, dnspark, homedns

__author__ = 'tlo'


def main():
    db = dbdata.DbData()
    rows = db.get_current()

    for (name, command, command2, router_id, oid, address, updated) in rows:

        # Old syntax -> command += " {} {}".format(name, oid)
        command += f" {name} {oid}"

        try:
            router_address = list(
                subprocess.check_output(command, shell=True, universal_newlines=True).rstrip().split())
        except subprocess.CalledProcessError as err:
            if err.returncode != 0:
                router_address = list(
                    subprocess.check_output(command2, shell=True, universal_newlines=True).rstrip().split())
        print(f"{name}'s listed IP: {address} assigned IP {router_address[0]}")

        if router_address[0] != address:
            dnspark.update(db, name, router_address[0])
            aws53.update(db, name, router_address[0])
            homedns.update(db, name, router_address[0])
            db.insert_new(router_id, router_address[0])

    db.close()
    # (name, command, router_id, address, updated)


if __name__ == '__main__':
    main()
