import dns.query
import dns.resolver
import dns.tsig
import dns.tsigkeyring as tsig
import dns.update

__author__ = 'tlo'


def lookup(hostname, qtype='A'):
    addr_list = []

    try:
        answers = dns.resolver.query(hostname, qtype)
        for rdata in answers:
            addr_list.append(rdata.address)
        return addr_list
    except dns.resolver.NoAnswer:
        return None


def update(db, host_name, new_address, qtype='A'):
    key, password, base_url = db.get_api_key('DNS_Eclipse')

    keyring = tsig.from_text({key: password})

    names = db.get_names_to_update_internal(host_name)

    for name in names:

        if name[0][0:6] == 'ocsnet' or name[0] == 'www':
            continue

        fqdn = name[0] + '.ocsnet.com.'

        answer = lookup(fqdn, qtype)
        rr_update = dns.update.Update('ocsnet.com.', keyring=keyring, keyalgorithm=dns.tsig.HMAC_SHA256)

        if answer:
            if set(new_address) != set(answer):
                rr_update.delete(fqdn, qtype)
                for addr in new_address:
                    rr_update.add(fqdn, 86400, qtype, addr)
                    response = dns.query.udp(rr_update, '198.147.254.14')
                    print(response)


def aws_lookup(hostname, qtype='A'):
    address_list = []

    try:
        answers = dns.resolver.query(hostname, qtype)
        for rdata in answers:
            address_list.append(rdata.address)
        return address_list
    except dns.resolver.NoAnswer:
        return None
