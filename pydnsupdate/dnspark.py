import requests as req

__author__ = 'Trevor Obermann'


def get_domain_data(key, password, base_url, domain_name):
    js = req.get(base_url + domain_name, auth=(key, password)).json()

    if js['message'] == 'OK':
        return js['records']


def get_record_data(key, password, base_url, record_id):
    js = req.get(base_url + str(record_id), auth=(key, password)).json()

    if js['message'] == 'OK':
        return js['records'][0]  # Should only ever be one record


def delete_record(db, key, password, base_url, record_id):
    js = req.delete(base_url + str(record_id), auth=(key, password)).json()

    if js['status'] == 200:
        print(js['message'])
        db.delete_record_dnspark(record_id)
    else:
        print(js['message'])


def update(db, router_name, new_address):
    key, password, base_url = db.get_api_key('DNS_Park')

    names = db.get_names_to_update_dnspark(router_name, new_address)

    if names is not None:
        for (rname, rtype, ttl, dynamic, record_id) in names:

            put_data = {'rname': rname + '.ocsnet.com', 'rtype': rtype, 'ttl': str(ttl), 'rdata': new_address,
                        'dynamic': dynamic}

            js = req.put(base_url + str(record_id), json=put_data, auth=(key, password)).json()

            if js['status'] == 200:
                last_update = js['records'][0]['last_update'].replace('T', ' ').replace('Z', '')

                db.save_new_dnspark(record_id, new_address, last_update)
                print(js['message'])
            else:
                print(js['message'])
    else:
        print('No dnspark update needed')
