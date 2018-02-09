#
# Import required packages.
#
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement
import logging
import re
import datetime
from xml.dom import minidom
import argparse

__author__ = 'ahmed'


def reader_csv_file(file_name, read_till=99999, skip_header=True, all_oid_range=False):
    # Reading Property file for processing XML file.
    file_reader = open(file_name, "r")

    # Skipping header line.
    if skip_header:
        file_reader.next()

    #
    # List to hold all the dictionary values.
    # Every row is a dictionary
    #
    file_list = []

    # line count to read till specific line.
    line_count = 0

    # Reading Lines now.
    for process_line in file_reader:

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

        # Check if we have a threshold to read line.
        if read_till < line_count:
            break

        # Create a temp dictionary to hold the line.
        line_dict = {}

        # Split line by ','
        list_proc_line_split = process_line.split(",")

        # Getting All data into the dictionary
        line_dict['module'] = list_proc_line_split[0].lower()  # Converting to lower case

        if '/' in str(list_proc_line_split[1]).lower():  # removing '=/' in field to 'per' and '_'
            line_dict['oid_name'] = re.sub('/', '_per_',
                                           list_proc_line_split[1].lower())  # zabbix does not like / in the key
        elif '=' in str(list_proc_line_split[1]).lower():  # Ex : mb/sec will be mb_per_sec
            line_dict['oid_name'] = re.sub('=', '_',
                                           list_proc_line_split[1].lower())  # Ex : user=phone will be user_phone
        else:
            # other possible special char is removed
            line_dict['oid_name'] = re.sub('[\[\]/=+*:,\'\"><]', '', list_proc_line_split[1].lower())

        line_dict['oid'] = list_proc_line_split[2]
        line_dict['datatype'] = list_proc_line_split[3].upper()  # making sure we have this as upper case
        line_dict['start'] = list_proc_line_split[4]
        line_dict['end'] = list_proc_line_split[5]
        line_dict['description'] = list_proc_line_split[6].strip()  # Strip string.
        oid_range_list = []

        if all_oid_range:
            oid_range_to_use = int(line_dict['end'])
        else:
            oid_range_to_use = 1

        #
        # Our file has OID range we are taking the range and putting them into a list.
        # Currently we need just the first OID (.0).
        # TODO : Need to change this if we need more than just the firat Element from the file.
        #
        for oid_range in range(int(line_dict['start']), oid_range_to_use):
            oid_range_created = line_dict['oid'] + '.' + str(oid_range)
            oid_range_list.append(oid_range_created)

        line_dict['oid_list'] = oid_range_list  # Adding the list to dictionary

        # Our row is ready to be added to the list.
        file_list.append(line_dict)
        line_count += 1

    return file_list


def read_csv_name_module(file_name, skip_header=True):
    # Reading Property file for processing XML file.
    file_reader = open(file_name, "r")

    # Skipping header line.
    if skip_header:
        file_reader.next()

    module_name_index = {}

    for line in file_reader:
        # Skip Empty Lines from property file.
        if line in ['\n', '\r\n']:
            continue

        line = line.strip()

        #
        # Checking for property file comments
        # Currently property file comments are '#'
        #
        if line[0] != "#":

            line = line.split(",")
            # Create a {} to store.
            data_dict = {'module': line[0].strip().lower(), 'index': line[1].strip()}

            # adding to {}

            # Checking for sp char to be removed.
            if '+' in line[2].strip():
                data_dict['name'] = re.sub('[+]', 'plus', line[2].strip())
            elif '#' in line[2].strip():
                data_dict['name'] = re.sub('#', '', line[2].strip())
            else:
                data_dict['name'] = re.sub('#[\[\]/=*:,\'\"><]', '', line[2].strip())

            # If we have the data already then append the {}
            if data_dict['module'] in module_name_index:
                module_name_index[data_dict['module']].append(data_dict)
            else:
                module_name_index[data_dict['module']] = [data_dict]

    # Ready to return.
    return module_name_index


#
# Merging CSV files. [{}]
#
def merge_csv_data(list_from_oid, dict_from_names, only_name_items=False):
    # Creating a list to store new data
    merge_list_with_config_data = []

    # Traversing the exsisting list.
    for items_row_dict in list_from_oid:
        # If we have the module in the dictionary then we append.
        if items_row_dict['module'] in dict_from_names:
            items_row_dict['module_details'] = dict_from_names[items_row_dict['module']]
            merge_list_with_config_data.append(items_row_dict)

        # Else we create a dummy oid {}
        else:
            # Lets create a dummy dictionary so that we can use it later.
            place_holder_dict = {'module': items_row_dict['module'], 'index': '0', 'name': items_row_dict['oid']}

            # Check if we only want items which have been configured.
            if only_name_items:
                items_row_dict['module_details'] = []

            # Else we add the dummy {}
            else:
                items_row_dict['module_details'] = [place_holder_dict]

            # Create some data
            merge_list_with_config_data.append(items_row_dict)

    # ready to return.
    return merge_list_with_config_data


# --------------------------------------------------------
# Generate Complete Export/Import XML File
# --------------------------------------------------------
def generate_items_xml_file_complete(
        list_from_file,
        host_name_in_gen_item,
        host_group_name_in_gen_item,
        host_interface_in_gen_item,
        item_application_name=None):

    # Date format for the new file created.
    fmt = '%Y-%m-%dT%H:%M:%SZ'

    # Creating the main element.
    zabbix_export = Element('zabbix_export')

    # Sub Element which fall under zabbix_export
    version = SubElement(zabbix_export, 'version')
    date = SubElement(zabbix_export, 'date')

    # Groups
    groups = SubElement(zabbix_export, 'groups')
    group_under_groups = SubElement(groups, 'group')
    name_under_group = SubElement(group_under_groups, 'name')

    # triggers
    triggers = SubElement(zabbix_export, 'triggers')

    # hosts
    hosts = SubElement(zabbix_export, 'hosts')
    host_under_hosts = SubElement(hosts, 'host')
    host_under_host = SubElement(host_under_hosts, 'host')
    name_under_host = SubElement(host_under_hosts, 'name')

    SubElement(host_under_hosts, 'proxy')

    # status and its sub elements
    status_under_host = SubElement(host_under_hosts, 'status')
    ipmi_authtype_under_host = SubElement(host_under_hosts, 'ipmi_authtype')
    ipmi_privilege_under_host = SubElement(host_under_hosts, 'ipmi_privilege')

    # elements under hosts
    SubElement(host_under_hosts, 'ipmi_username')
    SubElement(host_under_hosts, 'ipmi_password')
    SubElement(host_under_hosts, 'templates')

    # Groups under a hosts
    groups_under_hosts = SubElement(host_under_hosts, 'groups')
    group_under_groups_host = SubElement(groups_under_hosts, 'group')
    name_group_under_groups_host = SubElement(group_under_groups_host, 'name')

    # Interfaces
    interfaces_under_host = SubElement(host_under_hosts, 'interfaces')
    interface_under_interfaces_host = SubElement(interfaces_under_host, 'interface')
    default_under_interface = SubElement(interface_under_interfaces_host, 'default')
    type_under_interface = SubElement(interface_under_interfaces_host, 'type')
    useip_under_interface = SubElement(interface_under_interfaces_host, 'useip')
    ip_under_interface = SubElement(interface_under_interfaces_host, 'ip')
    SubElement(interface_under_interfaces_host, 'dns')
    port_under_interface = SubElement(interface_under_interfaces_host, 'port')
    interface_ref_under_interface = SubElement(interface_under_interfaces_host, 'interface_ref')

    # elements under hosts
    SubElement(host_under_hosts, 'applications')
    items = SubElement(host_under_hosts, 'items')
    SubElement(host_under_hosts, 'discovery_rules')

    # macro sub element
    macros = SubElement(host_under_hosts, 'macros')
    macro = SubElement(macros, 'macro')
    sub_macro = SubElement(macro, 'macro')
    value = SubElement(macro, 'value')
    SubElement(host_under_hosts, 'inventory')

    # This information will be from the user.
    date.text = datetime.datetime.now().strftime(fmt)
    host_under_host.text = host_name_in_gen_item.upper()
    name_under_host.text = host_name_in_gen_item.upper()
    name_under_group.text = host_group_name_in_gen_item.upper()
    ip_under_interface.text = host_interface_in_gen_item
    name_group_under_groups_host.text = host_group_name_in_gen_item.upper()

    # Standard values
    version.text = '2.0'
    status_under_host.text = '0'
    ipmi_authtype_under_host.text = '-1'
    ipmi_privilege_under_host.text = '2'
    default_under_interface.text = '1'
    type_under_interface.text = '2'
    useip_under_interface.text = '1'
    port_under_interface.text = '161'
    interface_ref_under_interface.text = 'if1'
    sub_macro.text = '{$SNMP_COMMUNITY}'
    value.text = 'public'


    #
    # Processing through the list of OID from the list in the dictionary
    # This actually a range as in the csv file
    # If we have set 'all_oid_range' as true, then we will process all the OID range for each OID
    # Warning : There will be too many Items in the import file.
    # BE CAREFUL WITH THE RANGE.
    #
    for row_dict_from_file in list_from_file:

        # if row_dict_from_file['module_details'] == []:
        # item_creator(row_dict_from_file, items, host_name.upper(), triggers, row_dict_from_file['oid'], item_application_name)

        # For each OID in the list - check function 'reader_csv_file' for more details.
        for oid_list_item in row_dict_from_file['module_details']:
            item_creator(row_dict_from_file, items, host_name_in_gen_item.upper(), triggers, oid_list_item,
                         item_application_name)

    return ElementTree.tostring(zabbix_export)


def item_creator(dictionary, items, host_name, triggers, module_detail_dict_item_from_dictionary,
                 item_application_name):
    #
    # Creating an initial XML Template
    #
    item = SubElement(items, 'item')
    name = SubElement(item, 'name')
    type = SubElement(item, 'type')
    snmp_community = SubElement(item, 'snmp_community')
    multiplier = SubElement(item, 'multiplier')
    snmp_oid = SubElement(item, 'snmp_oid')
    key = SubElement(item, 'key')
    delay = SubElement(item, 'delay')
    history = SubElement(item, 'history')
    trends = SubElement(item, 'trends')
    status = SubElement(item, 'status')
    value_type = SubElement(item, 'value_type')
    SubElement(item, 'allowed_hosts')                                   # If we are not using an element
                                                                        # then do not assign it
    SubElement(item, 'units')                                           #
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
    # Setting basic information for the item. Setting Values now.
    #
    name.text = 'From Module : (' + str(dictionary['module']).upper() + '), Sub Category : (' \
                + str(dictionary['oid_name']).upper() + '), Item For : ' + module_detail_dict_item_from_dictionary[
                    'name'] + \
                ', (' + str(dictionary['module']).upper() + '-INDEX-' + \
                str(module_detail_dict_item_from_dictionary['index']) + ')'

    # This has to be unique
    key.text = dictionary['module'] + '_' + dictionary['oid_name'] + '_' + module_detail_dict_item_from_dictionary[
        'name']

    # For Verbose Mode
    logging.debug('Key Generated as : ' + str(key.text))

    # Setting the OID here.
    snmp_oid.text = dictionary['oid'] + '.' + str(module_detail_dict_item_from_dictionary['index'])

    #
    # Setting value type to get information in int to string.
    # Based on the input file.
    # TODO : Add more datatype based on the return information.
    #
    if dictionary['datatype'] == 'STRING':
        value_type.text = '1'
    elif dictionary['datatype'] == 'INTEGER':
        value_type.text = '3'
    else:
        value_type.text = '1'


    #
    # Setting SNMP v1, This will change as per requirement.
    # TODO : Put a condition here so that we can change this on the fly.
    #
    type.text = '1'

    #
    # Creating Item with default values. No change here.
    # TODO : Need to add more information here based on requirement.
    #
    delta.text = '0'
    snmpv3_securitylevel.text = '0'
    snmpv3_authprotocol.text = '0'
    snmpv3_privprotocol.text = '0'
    formula.text = '1'
    data_type.text = '0'
    authtype.text = '0'
    inventory_link.text = '0'
    interface_ref.text = 'if1'
    if str(dictionary['oid_name']).upper() == "STATUS":
        delay.text = '60'
        history.text = '90'
    else:
        delay.text = '3600'
        history.text = '9000'
    trends.text = '365'
    status.text = '0'
    snmp_community.text = '{$SNMP_COMMUNITY}'
    multiplier.text = '0'

    # Adding Description as in the CSV file.
    description.text = dictionary['description']

    # Creating all the items in a specific Application on Zabbix
    application_name.text = item_application_name

    #
    # Currently we are creating Trigger for status OIDs as we know the return information
    # Assuming INS (In Service) and nis (Not in Service)
    # If currently used OID status changes from anything other then INS we trigger an alarm.
    #
    # TODO : Add more conditions to create different Triggers for different scenario.
    #
    if dictionary['datatype'] == 'STRING' and dictionary['oid_name'] == 'status':
        #
        # Creating a template
        #
        trigger = SubElement(triggers, 'trigger')
        trigger_expression = SubElement(trigger, 'expression')
        trigger_name = SubElement(trigger, 'name')
        SubElement(trigger, 'url')
        trigger_status = SubElement(trigger, 'status')
        trigger_priority = SubElement(trigger, 'priority')
        trigger_description = SubElement(trigger, 'description')
        trigger_type = SubElement(trigger, 'type')
        SubElement(trigger, 'dependencies')

        # Creating a expression - important stuff here.
        # TODO : This might change as per requirement.
        trigger_expression.text = '{' + host_name + ':' + key.text + '.str("INS")}=0'
        trigger_name.text = 'ATTENTION : On {HOST.NAME}, An Alarm From Module : (' + str(dictionary['module']).upper() \
                            + '), Sub Category : (' + str(dictionary['oid_name']).upper() \
                            + '), For : ' + module_detail_dict_item_from_dictionary['name'] + \
                            ', (' + str(dictionary['module']).upper() + \
                            '-INDEX-' + str(module_detail_dict_item_from_dictionary['index']) + ')'

        #
        # Setting default values here.
        # And same description as in the CSV file.
        trigger_status.text = '0'
        trigger_priority.text = '1'
        trigger_description.text = description.text
        trigger_type.text = '0'


def xml_pretty_me(file_name_for_prettify, string_to_prettify):
    #
    # Open a file and write to it and we are done.
    #
    logging.debug("Creating File pretty_%s", file_name_for_prettify)

    # Creating an XML and prettify xml.
    xml = minidom.parseString(string_to_prettify)
    pretty_xml_as_string = xml.toprettyxml()

    # Creating a file to write this information.
    output_file = open(file_name_for_prettify, 'w')
    output_file.write(pretty_xml_as_string)

    # Done.
    logging.debug("Creation Complete")
    output_file.close()


# --------------------------------------------------------
# Process CSV to create zabbix items from OID and range.
# --------------------------------------------------------
if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='This script is to Generate xml import file for Zabbix from CSV files.'
                                                 'We need two CSV files.'
                                                 '1. OID file, gives all the OIDs in the device.'
                                                 '2. Name file, gives all names configured for the above OIDs in the Device.'
                                                 ' Example : python -o oid_list_with_range_processed.csv -c oid_names_configured.csv -n GGSN-1-LONDON -g GGSN-GROUP -i 127.0.0.1 -a GGSN-APP-OIDS -y ')
    parser.add_argument('-o', '--csv-oid', help='OID file, Gives all OIDs on the device', required=True)
    parser.add_argument('-c', '--csv-name',
                        help='Name file, gives all names configured for the above OIDs in the Device.', required=True)
    parser.add_argument('-n', '--host-name', help='Host name as given in Zabbix server.', required=True)
    parser.add_argument('-g', '--host-group', help='Host Group which the host belongs to, as in Zabbix server.',
                        required=True)
    parser.add_argument('-i', '--host-interface',
                        help='SNMP Interface configured on Zabbix server. (Assuming Single Interface in Configured)',
                        required=True)
    parser.add_argument('-a', '--host-application',
                        help='Application Name in the Zabbix Server. (To organize all items being imported)',
                        required=True)
    parser.add_argument('-y', '--only-name',
                        help='Create xml items which are present in the name file. i.e create items which are configured in the device already, Rest of the OIDs are Ignored. [Default : False]',
                        action="store_true")
    parser.add_argument('-f', '--include-first-line',
                        help='Include First line (Header) in the CSV file input, [Default : False]',
                        action="store_true")
    parser.add_argument('-d', '--debug', help='Running Debug mode - More Verbose', action="store_true")
    parser.add_argument('-v', '--verbose', help='Running Debug mode - More Verbose', action="store_true")
    parser.add_argument('--version', action='version', version='%(prog)s 0.1.0')

    args = parser.parse_args()


    # Assigning Arguments
    csv_file_to_process = args.csv_oid
    csv_names_files = args.csv_name
    host_name = args.host_name
    host_group_name = args.host_group
    host_interface = args.host_interface
    host_application_items = args.host_application

    skip_header_state = True
    if args.include_first_line:
        skip_header_state = False

    only_oid_in_name = False
    if args.only_name:
        only_oid_in_name = True

    if args.debug or args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    # Creating a list of dictionaries [{},{},{}, ...]
    complete_csv_list_dict = reader_csv_file(csv_file_to_process, skip_header=skip_header_state)

    # Creating names dictionary {[{}{}{}][{}{}{}][{}...]...}
    complete_csv_names = read_csv_name_module(csv_names_files, skip_header=skip_header_state)

    # Merge above CSV files.
    list_for_processing = merge_csv_data(complete_csv_list_dict, complete_csv_names, only_name_items=only_oid_in_name)

    # xml string returned.
    xml_tree_for_device = generate_items_xml_file_complete(list_for_processing, host_name,
                                                           host_group_name, host_interface,
                                                           host_application_items)
    # Write it to file as a pretty xml.
    xml_pretty_me(str(host_name).lower() + '_' + str(host_interface).lower() + '.xml', xml_tree_for_device)
