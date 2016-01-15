import dns.query
import dns.resolver
import dns.tsig
import dns.tsigkeyring as tsig
import dns.update

__author__ = 'tlo'


def lookup(hostname):
    return dns.resolver.query(hostname, 'A')


def update(db, host_name, new_address):
    key, password, base_url = db.get_api_key('DNS_Eclipse')

    keyring = tsig.from_text({key: password})

    names = db.get_names_to_update_internal(host_name, new_address)

    for name in names:

        fqdn = name[0] + '.ocsnet.com.'

        answer = lookup(fqdn)

        if answer.rrset.items[0].address != new_address:
            rr_update = dns.update.Update('ocsnet.com.', keyring=keyring, keyalgorithm=dns.tsig.HMAC_SHA256)

            rr_update.replace(fqdn, 86400, 'A', new_address)

            response = dns.query.udp(rr_update, '198.147.254.2')

            print(response)
