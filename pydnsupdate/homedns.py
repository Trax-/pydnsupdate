__author__ = 'tlo'

import dns.resolver
import dns.query
import dns.tsigkeyring
import dns.update

keyring = dns.tsigkeyring.from_text({
    'dhcpupdater': 'K0HRYpjukbEaXOuc/867Lw=='
})


def lookup(hostname):
    answers = dns.resolver.query(hostname, 'A')

    return answers


def dnsupdate(answers, name):
    update = dns.update.Update('ocsnet.com', keyring=keyring)

    update.replace(name, 86400, 'A', answers[0].address)

    response = dns.query.tcp(update, '198.147.254.17')

    print(response)