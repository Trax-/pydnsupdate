from setuptools import setup

__author__ = 'Trevor Obermann'

setup(name='pydnsupdate',
      version='0.1',
      description='Dynamic DNS updater program',
      url='tlo@ocelot:/mnt/git/PyDNSUpdate.git',
      author='Trevor Obermann',
      author_email='tlo@ocsnet.com',
      license='MIT',
      packages=['pydnsupdate'],
      install_requires=[
          'requests', 'boto3', 'mysql-connector-python', 'dnspython3'
      ],
      zip_safe=False)
