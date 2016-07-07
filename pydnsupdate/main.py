import subprocess

from pydnsupdate import dbdata, homedns, dnspark, aws53

__author__ = 'tlo'

db = dbdata.DbData()
rows = db.get_current()

for (name, command, router_id, oid, address, updated) in rows:

    command += " {} {}".format(name, oid)
    router_address = list(subprocess.check_output(command, shell=True, universal_newlines=True).rstrip().split())

    print("{}'s listed IP: {} assigned IP {}".format(name, address, router_address[0]))

    if router_address[0] != address:
        dnspark.update(db, name, router_address[0])
        aws53.update(db, name, router_address[0])
        homedns.update(db, name, router_address[0])
        db.insert_new(router_id, router_address[0])

db.close()
# (name, command, router_id, address, updated)
