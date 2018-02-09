#!/usr/bin/python

__author__ = 'ahmed'

import csv
import sys
from logging import exception
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
import datetime
import logging
from xml.dom import minidom
import argparse




# dictionary to hold IANA SMI numbers.
iana_smi_numbers = {
    '1': 'iso',
    '1.3': 'org',
    '1.3.6': 'dod',
    '1.3.6.1': 'internet',
    '1.3.6.1.1': 'directory',
    '1.3.6.1.2': 'mgmt',
    '1.3.6.1.2.1': 'mib-2',
    '1.3.6.1.2.1.2.2.1.3': 'ifType',
    '1.3.6.1.2.1.10': 'transmission',
    '1.3.6.1.2.1.10.23': 'transmissionppp',
    '1.3.6.1.2.1.27': 'application',
    '1.3.6.1.2.1.28': 'mta',
    '1.3.6.1.2.2': 'pib',
    '1.3.6.1.3': 'experimental',
    '1.3.6.1.4': 'private',
    '1.3.6.1.4.1': 'enterprises',
    '1.3.6.1.5': 'security',
    '1.3.6.1.6': 'SNMPv2',
    '1.3.6.1.6.1': 'snmpDomains',
    '1.3.6.1.6.2': 'snmpProxys',
    '1.3.6.1.6.3': 'snmpModules',
    '1.3.6.1.7': 'mail',
    '1.3.6.1.8': 'features'
}


def get_smi_number_to_name(smi_number):
    if smi_number not in iana_smi_numbers:
        logging.debug("smi_number %s, Not Found", smi_number)
        return False
    else:
        return iana_smi_numbers[smi_number]
    pass


# --------------------------------------------------------
# Generate Complete Export/Import XML File
# --------------------------------------------------------
def generate_items_xml_file_complete(alarm_list, host_name, host_group_name, host_interface):
    zabbix_export = Element('zabbix_export')
    version = SubElement(zabbix_export, 'version')
    version.text = '2.0'

    fmt = '%Y-%m-%dT%H:%M:%SZ'
    date = SubElement(zabbix_export, 'date')
    date.text = datetime.datetime.now().strftime(fmt)

    groups = SubElement(zabbix_export, 'groups')
    group_under_groups = SubElement(groups, 'group')
    name_under_group = SubElement(group_under_groups, 'name')
    name_under_group.text = host_group_name.upper()

    hosts = SubElement(zabbix_export, 'hosts')
    host_under_hosts = SubElement(hosts, 'host')
    host_under_host = SubElement(host_under_hosts, 'host')
    host_under_host.text = host_name.upper()

    name_under_host = SubElement(host_under_hosts, 'name')
    name_under_host.text = host_name.upper()
    SubElement(host_under_hosts, 'proxy')

    status_under_host = SubElement(host_under_hosts, 'status')
    status_under_host.text = '0'

    ipmi_authtype_under_host = SubElement(host_under_hosts, 'ipmi_authtype')
    ipmi_authtype_under_host.text = '-1'

    ipmi_privilege_under_host = SubElement(host_under_hosts, 'ipmi_privilege')
    ipmi_privilege_under_host.text = '2'

    SubElement(host_under_hosts, 'ipmi_username')
    SubElement(host_under_hosts, 'ipmi_password')
    SubElement(host_under_hosts, 'templates')

    groups_under_hosts = SubElement(host_under_hosts, 'groups')
    group_under_groups_host = SubElement(groups_under_hosts, 'group')
    name_group_under_groups_host = SubElement(group_under_groups_host, 'name')
    name_group_under_groups_host.text = host_group_name.upper()

    interfaces_under_host = SubElement(host_under_hosts, 'interfaces')
    interface_under_interfaces_host = SubElement(interfaces_under_host, 'interface')
    default_under_interface = SubElement(interface_under_interfaces_host, 'default')
    default_under_interface.text = '1'

    type_under_interface = SubElement(interface_under_interfaces_host, 'type')
    type_under_interface.text = '2'

    useip_under_interface = SubElement(interface_under_interfaces_host, 'useip')
    useip_under_interface.text = '1'

    ip_under_interface = SubElement(interface_under_interfaces_host, 'ip')
    ip_under_interface.text = host_interface

    SubElement(interface_under_interfaces_host, 'dns')
    port_under_interface = SubElement(interface_under_interfaces_host, 'port')
    port_under_interface.text = '161'

    interface_ref_under_interface = SubElement(interface_under_interfaces_host, 'interface_ref')
    interface_ref_under_interface.text = 'if1'

    SubElement(host_under_hosts, 'applications')
    items = SubElement(host_under_hosts, 'items')
    triggers = SubElement(zabbix_export, 'triggers')

    # Iterate through the unique list to create XML
    for alarm_values in alarm_list:
        item_creator_type_17_oid(items, host_name.upper(), triggers, alarm_values)

    SubElement(host_under_hosts, 'discovery_rules')
    macros = SubElement(host_under_hosts, 'macros')
    macro = SubElement(macros, 'macro')
    sub_macro = SubElement(macro, 'macro')
    value = SubElement(macro, 'value')
    sub_macro.text = '{$SNMP_COMMUNITY}'

    if 'GGSN' in host_name:
        value.text = 'Public'
    elif 'ITP1' in host_name:
        value.text = 'mobileumro'
    else:
        value.text = 'public'

    SubElement(host_under_hosts, 'inventory')

    return zabbix_export


def item_creator_type_17_oid(items, host_name, triggers, alarm_values):
    item = SubElement(items, 'item')
    name = SubElement(item, 'name')
    type = SubElement(item, 'type')
    SubElement(item, 'snmp_community')
    multiplier = SubElement(item, 'multiplier')
    SubElement(item, 'snmp_oid')
    key = SubElement(item, 'key')
    delay = SubElement(item, 'delay')
    history = SubElement(item, 'history')
    trends = SubElement(item, 'trends')
    status = SubElement(item, 'status')
    value_type = SubElement(item, 'value_type')
    SubElement(item, 'allowed_hosts')
    SubElement(item, 'units')
    delta = SubElement(item, 'delta')
    SubElement(item, 'snmpv3_contextname')
    SubElement(item, 'snmpv3_securityname')
    snmpv3_securitylevel = SubElement(item, 'snmpv3_securitylevel')
    snmpv3_authprotocol = SubElement(item, 'snmpv3_authprotocol')
    SubElement(item, 'snmpv3_authpassphrase')
    snmpv3_privprotocol = SubElement(item, 'snmpv3_privprotocol')
    SubElement(item, 'snmpv3_privpassphrase')
    formula = SubElement(item, 'formula')
    SubElement(item, 'delay_flex')
    SubElement(item, 'params')
    SubElement(item, 'ipmi_sensor')
    data_type = SubElement(item, 'data_type')
    authtype = SubElement(item, 'authtype')
    SubElement(item, 'username')
    SubElement(item, 'password')
    SubElement(item, 'publickey')
    SubElement(item, 'privatekey')
    SubElement(item, 'port')
    description = SubElement(item, 'description')
    inventory_link = SubElement(item, 'inventory_link')
    SubElement(item, 'valuemap')
    applications = SubElement(item, 'applications')
    application = SubElement(applications, 'application')
    application_name = SubElement(application, 'name')
    interface_ref = SubElement(item, 'interface_ref')

    #
    # Setting basic information for the item.
    #
    name.text = 'An Alarm Notification For : ' + alarm_values['name']
    type.text = '17'
    multiplier.text = '0'
    key.text = 'snmptrap["' + alarm_values['oid'] + '"]'
    delay.text = '0'
    history.text = '90'
    trends.text = '365'
    status.text = '0'
    value_type.text = '2'
    delta.text = '0'
    snmpv3_securitylevel.text = '0'
    snmpv3_authprotocol.text = '0'
    snmpv3_privprotocol.text = '0'
    formula.text = '1'
    data_type.text = '0'
    authtype.text = '0'
    inventory_link.text = '0'
    description.text = alarm_values['description']
    interface_ref.text = 'if1'

    application_name.text = 'Alarms'

    trigger = SubElement(triggers, 'trigger')
    trigger_expression = SubElement(trigger, 'expression')
    trigger_name = SubElement(trigger, 'name')
    SubElement(trigger, 'url')
    trigger_status = SubElement(trigger, 'status')
    trigger_priority = SubElement(trigger, 'priority')
    trigger_description = SubElement(trigger, 'description')
    trigger_type = SubElement(trigger, 'type')
    SubElement(trigger, 'dependencies')

    trigger_expression.text = '{' + host_name + ':' + key.text + '.str("' + alarm_values['oid'] + '")}=1'
    trigger_name.text = 'ATTENTION : On {HOST.NAME}, An Alarm : ' + alarm_values['name'] + ', From Module : ' + \
                        alarm_values['mib_module']
    trigger_status.text = '0'
    trigger_priority.text = '3'
    trigger_description.text = description.text
    trigger_type.text = '0'


def item_creator_type_17(items, host_name, triggers, alarm_values):
    item = SubElement(items, 'item')
    name = SubElement(item, 'name')
    type = SubElement(item, 'type')
    SubElement(item, 'snmp_community')
    multiplier = SubElement(item, 'multiplier')
    SubElement(item, 'snmp_oid')
    key = SubElement(item, 'key')
    delay = SubElement(item, 'delay')
    history = SubElement(item, 'history')
    trends = SubElement(item, 'trends')
    status = SubElement(item, 'status')
    value_type = SubElement(item, 'value_type')
    SubElement(item, 'allowed_hosts')
    SubElement(item, 'units')
    delta = SubElement(item, 'delta')
    SubElement(item, 'snmpv3_contextname')
    SubElement(item, 'snmpv3_securityname')
    snmpv3_securitylevel = SubElement(item, 'snmpv3_securitylevel')
    snmpv3_authprotocol = SubElement(item, 'snmpv3_authprotocol')
    SubElement(item, 'snmpv3_authpassphrase')
    snmpv3_privprotocol = SubElement(item, 'snmpv3_privprotocol')
    SubElement(item, 'snmpv3_privpassphrase')
    formula = SubElement(item, 'formula')
    SubElement(item, 'delay_flex')
    SubElement(item, 'params')
    SubElement(item, 'ipmi_sensor')
    data_type = SubElement(item, 'data_type')
    authtype = SubElement(item, 'authtype')
    SubElement(item, 'username')
    SubElement(item, 'password')
    SubElement(item, 'publickey')
    SubElement(item, 'privatekey')
    SubElement(item, 'port')
    description = SubElement(item, 'description')
    inventory_link = SubElement(item, 'inventory_link')
    SubElement(item, 'valuemap')
    applications = SubElement(item, 'applications')
    application = SubElement(applications, 'application')
    application_name = SubElement(application, 'name')
    interface_ref = SubElement(item, 'interface_ref')

    #
    # Setting basic information for the item.
    #
    name.text = 'An Alarm Notification For : ' + alarm_values['name']
    type.text = '17'
    multiplier.text = '0'
    key.text = 'snmptrap["(' + alarm_values['mib_module'] + '::' + alarm_values[
        'name'] + ')((.|[[:space:]])*)({#SNMPVALUE})"]'
    delay.text = '0'
    history.text = '90'
    trends.text = '365'
    status.text = '0'
    value_type.text = '2'
    delta.text = '0'
    snmpv3_securitylevel.text = '0'
    snmpv3_authprotocol.text = '0'
    snmpv3_privprotocol.text = '0'
    formula.text = '1'
    data_type.text = '0'
    authtype.text = '0'
    inventory_link.text = '0'
    description.text = alarm_values['description']
    interface_ref.text = 'if1'

    application_name.text = 'Alarms'

    trigger = SubElement(triggers, 'trigger')
    trigger_expression = SubElement(trigger, 'expression')
    trigger_name = SubElement(trigger, 'name')
    SubElement(trigger, 'url')
    trigger_status = SubElement(trigger, 'status')
    trigger_priority = SubElement(trigger, 'priority')
    trigger_description = SubElement(trigger, 'description')
    trigger_type = SubElement(trigger, 'type')
    SubElement(trigger, 'dependencies')

    trigger_expression.text = '{' + host_name + ':' + key.text + '.str(' + alarm_values['name'] + ')}=1'
    trigger_name.text = 'ATTENTION : On {HOST.NAME}, An Alarm : ' + alarm_values[
        'name'] + ' - {#SNMPVALUE}, From Module : ' + alarm_values['mib_module']
    trigger_status.text = '0'
    trigger_priority.text = '3'
    trigger_description.text = description.text
    trigger_type.text = '0'


def xml_pretty_me(file_name_for_prettify, string_to_prettify):
    #
    # Open a file and write to it and we are done.
    #
    logging.debug("Creating File %s", file_name_for_prettify)

    xml = minidom.parseString(string_to_prettify)
    pretty_xml_as_string = xml.toprettyxml()
    output_file = open(file_name_for_prettify, 'w')
    output_file.write(pretty_xml_as_string)
    logging.debug("Creation Complete")
    output_file.close()


def read_from_csv(csv_file_name):
    try:
        reader = csv.reader(open(csv_file_name, 'r'))
        return reader
    except exception:
        print("Something went wrong in reading file" + str(exception))
        exit()


# @param
def zabbix_snmp_trap_import_from_csv(file_name, host_name, host_group_name, host_interface_ip):
    csv_reader = read_from_csv(file_name)
    alarm_list = []
    for alarm_data in csv_reader:

        # Skipping First Line
        if alarm_data[0] == "Name":
            continue

        oid_dictionary = {'name': alarm_data[0], 'full_name': alarm_data[1]}

        oid_to_convert = str(alarm_data[2])[1:]
        smi_name = get_smi_number_to_name(oid_to_convert[:11])
        if smi_name != False:
            iana_name_from_oid = smi_name + oid_to_convert[11:]
            oid_dictionary['oid'] = iana_name_from_oid
        else:
            oid_dictionary['oid'] = alarm_data[2]

        oid_dictionary['type'] = alarm_data[3]
        oid_dictionary['access'] = alarm_data[4]
        oid_dictionary['indexes'] = alarm_data[5]
        oid_dictionary['mib_module'] = alarm_data[6]
        oid_dictionary['description'] = alarm_data[7].strip('"')
        logging.debug('oid_dictionary:' + str(oid_dictionary))

        alarm_list.append(oid_dictionary)

    xml_tree = generate_items_xml_file_complete(alarm_list, host_name, host_group_name, host_interface_ip)
    xml_tree_as_string = ElementTree.tostring(xml_tree)
    return xml_tree_as_string


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='''Select the Alarms from the iReasoning MIB browser and Export them as CSV.
                                                    This Script expect MIB information to be in CSV format.
                                                    Export from a iReasoning Browser will generate CSV as below.
                                                    "Name","Full Name","OID","Type","Access","Indexes","MIB Module","Description".
                                                    We use this information to create snmptrap items and corresponding Trigger in the XML.
                                                    Which can be imported directly.''')

    parser.add_argument('-e', '--export-csv', help='OID file, Gives all OIDs on the device', required=True)
    parser.add_argument('-n', '--host-name', help='Host name as given in Zabbix server.', required=True)
    parser.add_argument('-g', '--host-group', help='Host Group which the host belongs to, as in Zabbix server.',
                        required=True)
    parser.add_argument('-i', '--host-interface',
                        help='SNMP Interface configured on Zabbix server. (Assuming Single Interface in Configured)',
                        required=True)
    parser.add_argument('-d', '--debug', help='Running Debug mode - More Verbose', action="store_true")
    parser.add_argument('-v', '--verbose', help='Running Debug mode - More Verbose', action="store_true")
    args = parser.parse_args()

    csv_file_name = args.export_csv
    zabbix_host_name = args.host_name
    zabbix_host_group_name = args.host_group
    zabbix_host_interface_ip = args.host_interface

    if args.debug or args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    xml_tree_gen_as_string = zabbix_snmp_trap_import_from_csv(csv_file_name, zabbix_host_name, zabbix_host_group_name,
                                                              zabbix_host_interface_ip)
    xml_pretty_me(zabbix_host_name.lower() + '-item-trigger-import.xml', xml_tree_gen_as_string)

