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


def update(db, router_name, new_address):
    key, password, base_url = db.get_api_key('AWS_Route53')

    route53 = get_session_client(key, password)

    names = db.get_names_to_update_aws(router_name, new_address)

    if names is None:
        print("No updates to process")
        return

    changes = []
    count = 0

    for name in names:
        zone_id = name[4]
        changes.append({
            'Action': 'UPSERT',
            'ResourceRecordSet': {
                'Name': name[0],
                'Type': name[1],
                'TTL': name[2],
                'ResourceRecords': [{'Value': new_address}]
            }
        })

        try:
            if count + 1 <= len(names) and zone_id != names[count + 1][4]:
                batch = {'Comment': 'Change by pyDNSUpdate issued by OCSNET', 'Changes': changes}

                reply = route53.change_resource_record_sets(HostedZoneId=zone_id, ChangeBatch=batch)
                if reply['ResponseMetadata']['HTTPStatusCode'] == 200:
                    db.update_aws_values(name[3], new_address, reply['ChangeInfo']['SubmittedAt'])
                changes = []
        except IndexError:
            batch = {'Comment': 'Change by pyDNSUpdate issued by OCSNET', 'Changes': changes}
            reply = route53.change_resource_record_sets(HostedZoneId=zone_id, ChangeBatch=batch)
            if reply['ResponseMetadata']['HTTPStatusCode'] == 200:
                db.update_aws_values(name[3], new_address, reply['ChangeInfo']['SubmittedAt'])

        count += 1
    db.db.commit()


def get_session_client(key, password):
    aws = Session(aws_access_key_id=key, aws_secret_access_key=password)
    return aws.client('route53')
