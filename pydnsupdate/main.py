import subprocess

import aws53
import dbdata
import dnspark
import homedns

__author__ = 'tlo'

db = dbdata.DbData()
query = db.get_current()

for (name, command, router_id, address, updated) in query:

    router_address = subprocess.check_output(command, shell=True, universal_newlines=True).rstrip()

    if router_address != address:
        dnspark.update(db, name, router_address)
        aws53.update(db, name, router_address)
        homedns.update(db, name, router_address)
        db.save_new(router_id, router_address)

        # dnsaddress = homedns.lookup(name)
        #
        # if router_address != dnsaddress[0].address:
        #     homedns.dnsupdate(dnsaddress, name)

db.close()
