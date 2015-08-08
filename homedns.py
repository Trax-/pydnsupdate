__author__ = 'tlo'

import dns.resolver
import dns.query
import dns.update


def lookup(hostname):
    answers = dns.resolver.query(hostname, 'A')

    return answers


def dnsupdate(answers, name):
    update = dns.update.Update('ocsnet.com')

    update.replace(name, 86400, 'A', answers[0].address)

    response = dns.query.tcp(update, '198.147.254.2')

    print(response)