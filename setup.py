from setuptools import setup, find_packages

__author__ = 'Trevor Obermann'

setup(
    name='pydnsupdate',
    version='0.3',
    description='Dynamic DNS updater program',
    url='tlo@ocelot:/mnt/git/PyDNSUpdate.git',
    author='Trevor Obermann',
    author_email='tlo@ocsnet.com',
    license='MIT',
    packages=find_packages(),
    install_requires=[
        'requests', 'boto3', 'mysql-connector-python', 'dnspython3'
    ],
    scripts=['bin/pydnsupdate-run'],
    zip_safe=False
)
