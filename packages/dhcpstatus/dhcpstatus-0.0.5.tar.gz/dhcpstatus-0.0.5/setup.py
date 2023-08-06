import setuptools

with open('requirements.txt') as f:
    required = f.read().splitlines()

URL = 'https://pypi.org/project/dhcpstatus/'

setuptools.setup(
    url=URL,
    install_requires=required,
    entry_points={
        'console_scripts': ['dhcpstatus_subnet = dhcpstatus.dhcp_status:main_subnet_status']})
