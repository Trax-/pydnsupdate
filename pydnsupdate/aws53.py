from boto3.session import Session

__author__ = 'tlo'


def get_hosted_zone(key, password, base_url):
    pass


def get_hosted_zone_count(client):
    return client.get_hosted_zone_count()['HostedZoneCount']


def list_hosted_zones(client):
    return client.list_hosted_zones()


def list_resource_record_sets(client, zone_id):
    return client.list_resource_record_sets(HostedZoneId=zone_id)


def update(db, new_addresses, qtype):
    key, password, base_url = db.get_api_key('AWS_Route53')

    route53 = get_session_client(key, password)

    names = db.get_names_to_update_aws(qtype)

    if len(names) == 0:
        names = db.get_names_to_update_aws6()

    changes = []
    count = 0

    for name, qtype, ttl, zone_id in names:
        changes.append({
            'Action': 'UPSERT',
            'ResourceRecordSet': {
                'Name': name,
                'Type': qtype,
                'TTL': ttl,
                'ResourceRecords': [{'Value': new_addresses[0]}, {'Value': new_addresses[1]}],
            }
        })
        try:
            if count + 1 <= len(names) and zone_id != names[count + 1][3]:
                batch = {'Comment': 'Change by pyDNSUpdate issued by OCSNET', 'Changes': changes}

                reply = route53.change_resource_record_sets(HostedZoneId=zone_id, ChangeBatch=batch)
                if reply['ResponseMetadata']['HTTPStatusCode'] == 200:
                    for change in changes:
                        db.update_aws_values(change['ResourceRecordSet']['Name'], new_addresses,
                                             reply['ChangeInfo']['SubmittedAt'], qtype)
                changes = []
        except IndexError:
            batch = {'Comment': 'Change by pyDNSUpdate issued by OCSNET', 'Changes': changes}
            reply = route53.change_resource_record_sets(HostedZoneId=zone_id, ChangeBatch=batch)
            if reply['ResponseMetadata']['HTTPStatusCode'] == 200:
                for change in changes:
                    db.update_aws_values(change['ResourceRecordSet']['Name'], new_addresses,
                                         reply['ChangeInfo']['SubmittedAt'], qtype)
        count += 1

    db.db.commit()


def get_session_client(key, password):
    aws = Session(aws_access_key_id=key, aws_secret_access_key=password)
    return aws.client('route53')
