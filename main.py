import subprocess

from pydnsupdate import dbdata, homedns, dnspark, aws53

__author__ = 'tlo'

db = dbdata.DbData()
query = db.get_current()

for (name, command, router_id, address, updated) in query:

    router_address = subprocess.check_output(command, shell=True, universal_newlines=True).rstrip()

    print("{}'s listed IP: {} assigned IP {}".format(name, address, router_address))

    if router_address != address:
        dnspark.update(db, name, router_address)
        aws53.update(db, name, router_address)
        homedns.update(db, name, router_address)
        db.insert_new(router_id, router_address)

db.close()
