import dns.query
import dns.resolver
import dns.tsig
import dns.tsigkeyring as tsig
import dns.update

__author__ = 'tlo'


def lookup(hostname, ip_version):
    if ip_version == 4:
        return dns.resolver.query(hostname, 'A')
    else:
        try:
            return dns.resolver.query(hostname, 'AAAA')
        except dns.resolver.NoAnswer:
            return None


def update(db, host_name, new_address, ip_version=4):
    key, password, base_url = db.get_api_key('DNS_Eclipse')

    keyring = tsig.from_text({key: password})

    names = db.get_names_to_update_internal(host_name)

    for name in names:

        if name[0][0:6] == 'ocsnet' or name[0] == 'www':
            continue

        fqdn = name[0] + '.ocsnet.com.'

        answer = lookup(fqdn, ip_version)
        rr_update = dns.update.Update('ocsnet.com.', keyring=keyring, keyalgorithm=dns.tsig.HMAC_SHA256)

        for index in range(0, len(new_address)):
            if answer:
                if ip_version == 4:
                    temp = answer.rrset.items[index].address
                    if temp not in new_address:
                        rr_update.delete(fqdn, 'A', temp)
                        rr_update.add(fqdn, 86400, 'A', new_address[index])
                        response = dns.query.udp(rr_update, '198.147.254.14')
                        print(response)

                else:
                    temp = answer.rrset.items[index].address
                    if temp not in new_address:
                        rr_update.delete(fqdn, 'AAAA', temp)
                        rr_update.add(fqdn, 86400, 'AAAA', new_address[index])
                        response = dns.query.udp(rr_update, '198.147.254.14')
                        print(response)

                    # else:
                    #     rr_update.add(fqdn, 86400, 'AAAA', new_address[index])
