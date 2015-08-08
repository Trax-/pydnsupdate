__author__ = 'tlo'

import subprocess

import aws53
import dbdata
import homedns

db = dbdata.DbData()
query = db.getcurrent()

for (name, command, address, routerid, timestamp) in query:

    router_address = subprocess.check_output(command, shell=True, universal_newlines=True).rstrip()

    if router_address != address:
        aws53.update(name, router_address)  # TODO add code to update mx server when appropriate
        db.savenew(routerid, router_address)

    dnsaddress = homedns.lookup(name)

    if router_address != dnsaddress[0].address:
        homedns.dnsupdate(dnsaddress, name)

db.close()
