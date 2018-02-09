from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
import logging
import zabbix_send_from_kpi_xml
import sys
import os.path
import datetime


# --------------------------------------------------------
# Help Menu
# --------------------------------------------------------
def help_menu():
    logging.error(" Wrong Arguments - Please see below for more information")
    logging.error("""\n
     --------------------------------------------
                        USAGE
     --------------------------------------------

     1. To Generate Properties file.
     --------------------------------------------
     python ggsn_auto_zabbix_export_generator.py <source_xml_file> [ALL] <host_name> <host_group_name>
     \texample: python ggsn_auto_zabbix_export_generator.py KPI_SOURCE_FILE.xml ALL ZABBIX-TMP DEVICE_X1_2

     3. Send KPI from properties file.
     --------------------------------------------
     python ggsn_auto_zabbix_export_generator.py <source_xml_file> [FILE] <properties_file_name> <host_name> <host_group_name>
     \texample:  python ggsn_auto_zabbix_export_generator.py KPI_SOURCE_FILE.xml FILE KPI_SOURCE_FILE.xml.properties ZABBIX-TMP DEVICE_X1_2

     Parameter Information
     --------------------------------------------
     <source_xml_file>      : Is the XML KPI file for Device.
     <properties_file_name> : This is the file which is generated using option (1). '#' is comment in properties file.
     <host_name>            : Host name which needs to be created on Zabbix.
     <host_group_name>      : Group name to which host needs to be assigned.
     [ALL]                  : Static value. Use as-is.
     [FILE]                 : Static Value. Use as-is.
     --------------------------------------------
     """)
    exit()


# --------------------------------------------------------
# Generate unique keys
# --------------------------------------------------------
def generate_unique_key(properties_list_key, dictionary_xml_document_key):

    # Creating a bucket
    unique_key_list_data = []

    # Traverse through the list of lists.
    for list_value_properties in properties_list_key:
        #
        # Process file
        # which are direct key/values in the XML and the
        # Processing is ACTIVE to send the data to Server.
        #
        if list_value_properties[0] == "KEY_VALUE":

            for item_in in range(0, int(list_value_properties[3])):
                key_data_from_xml = dictionary_xml_document_key["measCollecFile"]["measData"]["measInfo"][int(list_value_properties[2])]['@measInfoId'] +'_'+ dictionary_xml_document_key["measCollecFile"]["measData"]["measInfo"][int(list_value_properties[2])]["measType"][item_in]["#text"]
                logging.debug("Key:"+key_data_from_xml)

                # Making sure all the key Generated are Unique.
                if key_data_from_xml not in unique_key_list_data:
                    logging.debug("Key Added:"+key_data_from_xml)
                    unique_key_list_data.append(key_data_from_xml)

        #
        # TODO : Processing SUB TREE in XML.
        #
        elif list_value_properties[0] == "KEY_VALUE_TREE_APN":
            logging.debug("passing APN for now")

        #
        # TODO : Processing SUB TREE in XML.
        #
        elif list_value_properties[0] == "KEY_VALUE_TREE_IP":
            logging.debug("passing IP for now")

    # Debugging
    logging.debug(unique_key_list_data)

    # Return the unique list
    return unique_key_list_data


# --------------------------------------------------------
# Unique keys from file.
# --------------------------------------------------------
def generate_unique_key_from_file(properties_file_name_in_file, dictionary_xml_document_file):

    # Bucket
    unique_key_list = []

    # Reading Property file for processing XML file.
    file_reader = open(properties_file_name_in_file, "r")

    for process_line in file_reader.readlines():

        # Skip Empty Lines from property file.
        if process_line in ['\n', '\r\n']:
            continue

        process_line = process_line.strip()

        #
        # Checking for property file comments
        # Currently property file comments are '#'
        #
        if process_line[0] != "#":
            list_of_values = process_line.split(",")

            # Adding Debugging
            logging.debug(list_of_values)

            #
            # Process file
            # which are direct key/values in the XML and the
            # Processing is ACTIVE to send the data to Server.
            #

        if list_of_values[0] == 'KEY_VALUE':
            for item_in in range(0, int(list_of_values[3])):
                key_data_from_xml = dictionary_xml_document_file["measCollecFile"]["measData"]["measInfo"][int(list_of_values[2])]['@measInfoId'] +\
                                    '_'+ dictionary_xml_document_file["measCollecFile"]["measData"]["measInfo"][int(list_of_values[2])]["measType"][item_in]["#text"]

                logging.debug("Key:" + key_data_from_xml)

                # Making sure all the key Generated are Unique.
                if key_data_from_xml not in unique_key_list:
                    unique_key_list.append(key_data_from_xml)

        #
        # TODO : Processing SUB TREE in XML.
        #
        elif list_of_values[0] == "KEY_VALUE_TREE_APN":
            logging.debug("passing APN for now")

        #
        # TODO : Processing SUB TREE in XML.
        #
        elif list_of_values[0] == "KEY_VALUE_TREE_IP":
            logging.debug("passing IP for now")

    # Debugging
    logging.debug(unique_key_list)

    return unique_key_list


# --------------------------------------------------------
# Generate Complete Export/Import XML File
# --------------------------------------------------------
def generate_items_xml_file_complete(unique_key_list_for_file, host_name_for_import, host_group_name_for_import):

    zabbix_export = Element('zabbix_export')
    version = SubElement(zabbix_export, 'version')
    version.text = '2.0'

    fmt = '%Y-%m-%dT%H:%M:%SZ'
    date =  SubElement(zabbix_export, 'date')
    date.text = datetime.datetime.now().strftime(fmt)

    groups = SubElement(zabbix_export, 'groups')
    group_under_groups = SubElement(groups, 'group')
    name_under_group = SubElement(group_under_groups, 'name')
    name_under_group.text = host_group_name_for_import.upper()

    hosts = SubElement(zabbix_export, 'hosts')
    host_under_hosts = SubElement(hosts, 'host')
    host_under_host = SubElement(host_under_hosts, 'host')
    host_under_host.text = host_name_for_import.upper()

    name_under_host = SubElement(host_under_hosts,'name')
    name_under_host.text = host_name_for_import.upper()
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
    name_group_under_groups_host.text = host_group_name_for_import.upper()

    SubElement(host_under_hosts, 'interfaces')
    # interfaces_under_host = SubElement(host_under_hosts, 'interfaces')
    # interface_under_interfaces_host = SubElement(interfaces_under_host, 'interface')
    # default_under_interface = SubElement(interface_under_interfaces_host, 'default')
    # default_under_interface.text = '1'
    #
    # type_under_interface = SubElement(interface_under_interfaces_host, 'type')
    # type_under_interface.text = '1'
    #
    # useip_under_interface = SubElement(interface_under_interfaces_host, 'useip')
    # useip_under_interface.text = '1'
    #
    # ip_under_interface = SubElement(interface_under_interfaces_host, 'ip')
    # ip_under_interface.text = '127.0.0.1'
    #
    # SubElement(interface_under_interfaces_host, 'dns')
    # port_under_interface = SubElement(interface_under_interfaces_host, 'port')
    # port_under_interface.text = '10050'
    #
    # interface_ref_under_interface = SubElement(interface_under_interfaces_host, 'interface_ref')
    # interface_ref_under_interface.text = 'if1'


    SubElement(host_under_hosts, 'applications')
    items = SubElement(host_under_hosts, 'items')

    # Iterate through the unique list to create XML
    for unique_key_data_from_xml in unique_key_list_for_file:
        item = SubElement(items, 'item')
        name = SubElement(item, 'name')
        type = SubElement(item, 'type')
        snmp_community = SubElement(item, 'snmp_community')
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
        SubElement(item, 'description')
        inventory_link = SubElement(item, 'inventory_link')
        SubElement(item, 'valuemap')

        #
        # Setting basic information for the item.
        #
        name.text = unique_key_data_from_xml
        type.text = '2'
        multiplier.text = '0'
        key.text = unique_key_data_from_xml
        delay.text = '0'
        history.text = '90'
        trends.text = '365'
        status.text = '0'
        value_type.text = '3'
        delta.text = '0'
        snmpv3_securitylevel.text = '0'
        snmpv3_authprotocol.text = '0'
        snmpv3_privprotocol.text = '0'
        formula.text = '1'
        data_type.text = '0'
        authtype.text = '0'
        inventory_link.text = '0'

    SubElement(host_under_hosts, 'discovery_rules')

    macros = SubElement(host_under_hosts, 'macros')
    macro = SubElement(macros, 'macro')
    sub_macro = SubElement(macro,'macro')
    value = SubElement(macro, 'value')
    sub_macro.text = '{$SNMP_COMMUNITY}'
    value.text = 'Public'

    SubElement(host_under_hosts, 'inventory')

    return  zabbix_export


# --------------------------------------------------------
# Generate XML items
# --------------------------------------------------------
def generate_items_xml_file(unique_key_list_for_file):
    #
    # Creating item XML here.
    #
    items = Element('items')

    # Iterate through the unique list to create XML
    for unique_key_data_from_xml in unique_key_list_for_file:
        item = SubElement(items, 'item')
        name = SubElement(item, 'name')
        type = SubElement(item, 'type')
        snmp_community = SubElement(item, 'snmp_community')
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
        SubElement(item, 'description')
        inventory_link = SubElement(item, 'inventory_link')
        SubElement(item, 'valuemap')

        #
        # Setting basic information for the item.
        #
        name.text = 'KPI_KEY_NAME_' + unique_key_data_from_xml
        type.text = '2'
        multiplier.text = '0'
        key.text = unique_key_data_from_xml
        delay.text = '0'
        history.text = '90'
        trends.text = '365'
        status.text = '0'
        value_type.text = '3'
        delta.text = '0'
        snmpv3_securitylevel.text = '0'
        snmpv3_authprotocol.text = '0'
        snmpv3_privprotocol.text = '0'
        formula.text = '1'
        data_type.text = '0'
        authtype.text = '0'
        inventory_link.text = '0'

    # Debugging
    logging.debug(ElementTree.tostring(items))

    return items


# --------------------------------------------------------
# Writing to File.
# --------------------------------------------------------
def write_xml_to_file(items, xml_file_name_to_write):
    #
    # Open a file and write to it and we are done.
    #
    logging.info("Creating File items_%s", xml_file_name_to_write)
    output_file = open('items_'+xml_file_name_to_write, 'w' )
    output_file.write('<?xml version="1.0" encoding="UTF-8"?>'
                       '<?xml-stylesheet type="text/xsl"?>')
    output_file.write(ElementTree.tostring(items))
    logging.info("Creation Complete")
    output_file.close()

def xml_pretty_me(file_name_for_prettify, string_to_prettify):
    #
    # Open a file and write to it and we are done.
    #
    logging.info("Creating File pretty_%s", file_name_for_prettify)
    import xml.dom.minidom
    xml = xml.dom.minidom.parseString(string_to_prettify)
    pretty_xml_as_string = xml.toprettyxml()
    output_file = open(file_name_for_prettify, 'w' )
    output_file.write(pretty_xml_as_string)
    logging.info("Creation Complete")
    output_file.close()

# --------------------------------------------------------
# Process XML for items (Zabbix Server).
# --------------------------------------------------------
if __name__ == '__main__':

    # System Arguments check
    if len(sys.argv) == 1 and len(sys.argv) != 5 and len(sys.argv) != 6:
        help_menu()

    logging.basicConfig(level=logging.DEBUG)

    # Loading XML as a Dictionary
    logging.info("Starting XML parsing process to Dictionary")

    xml_file_name = sys.argv[1]

    if not os.path.isfile(xml_file_name):
        logging.error("xml File Not Present")
        help_menu()

    # Loading XML as a Dictionary and Generate ALL KPIs
    dictionary_xml_document = zabbix_send_from_kpi_xml.load_xml_as_dictionary(xml_file_name)
    dictionary_kpi_data = zabbix_send_from_kpi_xml.generate_kpi_count(dictionary_xml_document)
    dictionary_kpi_data, total_index = zabbix_send_from_kpi_xml.generate_kpi_list(dictionary_xml_document, dictionary_kpi_data)

    if len(sys.argv) == 5 and sys.argv[2] == "ALL":

        host_name_to_create = sys.argv[3]
        host_group_name = sys.argv[4]

        # Create Properties list.
        properties_list = zabbix_send_from_kpi_xml.generate_properties_list(dictionary_kpi_data, total_index)
        unique_key_list = generate_unique_key(properties_list, dictionary_xml_document)
        zabbix_export_string = generate_items_xml_file_complete(unique_key_list, host_name_to_create, host_group_name)

        # Generate a New File.
        xml_pretty_me('ZABBIX_EXPORT_FILE_'+ host_name_to_create.upper() + '.xml', ElementTree.tostring(zabbix_export_string))

    elif len(sys.argv) == 6 and sys.argv[2] == "FILE":
        # Properties files Name
        properties_file_name = str(sys.argv[3])
        host_name_to_create = sys.argv[4]
        host_group_name = sys.argv[5]

        if not os.path.isfile(properties_file_name):
            logging.error("Properties File Not Present")
            help_menu()

        unique_key_list = generate_unique_key_from_file(properties_file_name, dictionary_xml_document)
        zabbix_export_string = generate_items_xml_file_complete(unique_key_list, host_name_to_create, host_group_name)

        # Generate a New File.
        xml_pretty_me('ZABBIX_EXPORT_FILE_'+ host_name_to_create.upper() + '.xml', ElementTree.tostring(zabbix_export_string))
