import paramiko


def get_client(router):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.get_host_keys()

    ssh_client.connect(hostname=router, username='ocelot')

    return ssh_client


def get_all_addresses(client):
    stdin, stdout, stderr = client.exec_command('./addresses.sh')
    result = stdout.read().decode().split('\n')
    del result[4]
    return result


def close_client(client):
    client.close()
