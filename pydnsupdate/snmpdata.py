import ipaddress
from easysnmp import Session


def get_session(name, version=2):
    session = Session(name, version, use_sprint_value=True)

    return session


def get_ip4_addresses(sess):
    addresses = sess.walk('IP-MIB::ipAdEntAddr')

    del addresses[2:]

    return (addresses[0].value + ':' + addresses[1].value).split(':')


def get_ip6_addresses(sess):
    hexlist = []
    ip_addresses = []

    items = sess.walk('IP-MIB::ipAddressType.2.16.38')

    del items[1:3]

    for item in items:

        ipv6addresses = list(map(int, item.oid_index.split('.')[2:]))

        for octet in ipv6addresses:
            hexlist.append(f'{octet:02x}')
        if hexlist[8:14] == ['00', '00', '00', '00', '00', '00'] and ipv6addresses[15] != 1:
            hexlist.pop(15)
            hexlist.append(f'{1:02x}')

        result = ipaddress.IPv6Address(
            f'{hexlist[0]}{hexlist[1]}:{hexlist[2]}{hexlist[3]}:{hexlist[4]}{hexlist[5]}:{hexlist[6]}{hexlist[7]}:'
            f'{hexlist[8]}{hexlist[9]}:{hexlist[10]}{hexlist[11]}:{hexlist[12]}{hexlist[13]}:{hexlist[14]}{hexlist[15]}')

        ip_addresses.append(result.compressed)
        hexlist = []

    return ip_addresses
