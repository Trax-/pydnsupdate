

def get_all_addresses(client):
    stdin, stdout, stderr = client.exec_command('./addresses.sh')
    result = stdout.read().decode().split('\n')
    del result[4]
    return result
