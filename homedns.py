import dns.query
import dns.resolver
import dns.tsig
import dns.tsigkeyring as tsig
import dns.update

__author__ = 'tlo'


def lookup(hostname):
    answers = dns.resolver.query(hostname, 'A')

    return answers


def update(db, host_name, new_address):
    keyring = tsig.from_text({
        'pydnsupdate-key': 'WWNHdN13wxy7Pka2Up8M5cOSt5nFVsyhCv/2c2AgkK4='
    })

    names = db.get_names_to_update_internal(host_name, new_address)

    for name in names:
        fqdn = name[0] + '.ocsnet.com.'

        rr_update = dns.update.Update('ocsnet.com.', keyring=keyring, keyalgorithm=dns.tsig.HMAC_SHA256)

        rr_update.replace(fqdn, 86400, 'A', new_address)

        response = dns.query.udp(rr_update, '198.147.254.2')

        check = dns.resolver.query(fqdn)

        print(response)
