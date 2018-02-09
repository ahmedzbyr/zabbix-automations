import os
from setuptools import setup

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "zabbix_snmp_trap_import_from_csv",
    version = "0.1.0",
    author = "Zubair AHMED",
    author_email = "ahmedzbyr@gmail.com",
    description = ("Module used to generate Zabbix import xml for snmp traps"),
    url='https://github.com/ahmedzbyr/zabbix_snmp_trap_import_from_csv',
    license = "BSD",
    py_modules=['zabbix_snmp_trap_import_from_csv'],
    long_description=read('README.txt'),
    classifiers=[
        "License :: OSI Approved :: BSD License",
    ],
)