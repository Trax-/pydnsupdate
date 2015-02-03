__author__ = 'tlo'

import route53


def update(name, router_address):
    conn = route53.connect(
        aws_access_key_id='AKIAJCZTOPIGRZTB7A7Q',
        aws_secret_access_key='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'
    )

    zone = conn.get_hosted_zone_by_id('Z385NZ78OP57MX')  # ocsnet.info zone id

    name_to_match = name + '.ocsnet.info.'

    for record_set in zone.record_sets:
        if record_set.name == name_to_match:
            record_set.values = router_address
            record_set.save()
            print(record_set)
            print(record_set.records)
            break
