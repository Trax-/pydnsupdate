__author__ = 'Trevor Obermann'

import json

import requests

API_key = 'AAb619912c519ef1786a6372f6e1ed77c5'
API_Token = '8a3786d1b9504086e8e3573642489c8caae03b3a'
my_url = 'https://api.dnspark.com/v2/dns/'
ns1_id = '14205172'  # ns1.ocsnet.com
ns2_id = '14205174'  # ns2.ocsnet.com
ns3_id = '14205176'  # ns3.ocsnet.com
domain_record_id = '14250700'  # ocsnet.com or @
domain_id = '477674'

payload = {'rname': 'ocsnet.com', 'rtype': 'A', 'ttl': '60', 'rdata': '74.248.229.45', 'dynamic': 'Y'}

r = requests.get(my_url + domain_record_id, auth=(API_key, API_Token))

# r = requests.post(my_url + domain_id, data=json.dumps(payload),
#                  auth=('AAb619912c519ef1786a6372f6e1ed77c5', '8a3786d1b9504086e8e3573642489c8caae03b3a'))

print(json.dumps(payload))
print(r.json())
