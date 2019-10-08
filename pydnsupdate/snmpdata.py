from easysnmp import Session


def get_session(name, version=2):
    session = Session(name, version, use_sprint_value=True)

    return session


def get_ip4_addresses(sess):
    addresses = sess.walk('IP-MIB::ipAdEntAddr')

    del addresses[0]
    del addresses[2:]

    return (addresses[0].value + ':' + addresses[1].value).split(':')


def get_ip6_addresses(sess):

    ip_addresses = []

    items = sess.get('hrSWRunParameters.41411')
    ip_addresses.append(items.value.split()[6])
    items = sess.get('hrSWRunParameters.42041')
    ip_addresses.append(items.value.split()[6])

    return ip_addresses
