from setuptools import setup, find_packages

__author__ = 'Trevor Obermann'

setup(
    name='pydnsupdate',
    version='4.7',
    description='Dynamic DNS updater program',
    url='tlo@ocelot:/srv/git/PyDNSUpdate.git',
    author='Trevor Obermann',
    author_email='tlo@ocsnet.com',
    license='MIT',
    packages=find_packages(),
    entry_points={'console_scripts': ['pydnsupdate = pydnsupdate.main:main']},
    install_requires=[
        'requests', 'boto3', 'mysql-connector-python', 'dnspython', 'asyncssh', 'setuptools'
    ],
    zip_safe=False
)
