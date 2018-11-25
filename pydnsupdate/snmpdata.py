from easysnmp import Session
import ipaddress


def get_session(name, version=2):
    session = Session(name, version, use_sprint_value=True)

    return session


def get_ip4_addresses(sess):
    addresses = sess.walk('IP-MIB::ipAdEntAddr')

    del addresses[2:]

    return (addresses[0].value + ':' + addresses[1].value).split(':')


def get_ip6_addresses(sess):
    hexlist = list()

    items = sess.walk('IP-MIB::ipAddressType.2.16.38')

    del items[1:3]

    for item in items:

        ipv6addresses = list(map(int, item.oid_index.split('.')[2:]))

        for idx in range(0, len(ipv6addresses), 2):
            if ipv6addresses[idx + 1] == 67:
                hexlist.append(f'{0:02x}' + f'{1:02x}')
            else:
                hexlist.append(f'{ipv6addresses[idx]:02x}' + f'{ipv6addresses[idx + 1]:02x}')
    return list({str(ipaddress.IPv6Address(str.join(':', hexlist)[:39])),
                 str(ipaddress.IPv6Address(str.join(':', hexlist)[40:]))})
