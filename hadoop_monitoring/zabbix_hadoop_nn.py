__author__ = 'ahmed'

import json
import ast
import textwrap
import urllib
import logging

import time
import datetime

from xml.dom import minidom
from xml.etree import ElementTree
from xml.etree.ElementTree import Element
from xml.etree.ElementTree import SubElement

import argparse
import re

import zbxsend  # This package can be installed from : https://github.com/ahmedzbyr/zbxsend


# ---------------------------------
# Temp JSON loader function
# returns - json_data for processing
# ---------------------------------
def temp_json_loading():
    """
    This is a temp json loader for testing.
    :return: json data
    """
    file_desc = open('resources/namenode_jmx.json', 'r+')
    data = json.load(file_desc)
    return data


# ---------------------------------
# Generate Module Dictionary from Category List.
# returns - key/value module info
# ---------------------------------
def generate_module_dictionary(category_to_process, data):
    """
        This Function generates module dictionary from the JSON.
        We select specific modules we need to process, and use them.

        Module indices are mention in the list 'category_to_process'
        'data' is the json, which we use to extract these parameters.

        Returns key/value pair information
        key : ModuleName
        Value :

    :param category_to_process:
    :param data:
    :return:
    """
    module_name = dict()
    for item in category_to_process:
        for key in data['beans'][item]:
            if key == 'name':
                try:
                    if 'type' in str(data['beans'][item][key]):
                        module_name[item] = str(data['beans'][item][key]).split('=')[1]
                    elif 'name' in str(data['beans'][item][key]):
                        module_name[item] = str(data['beans'][item][key]).split('name=')[1]
                except:
                    print("Some Error Occurred in module_gen - But will continue for other modules")
                    continue

    return module_name


# ---------------------------------
# Generate URL
# ---------------------------------
# This function converts the servername to URL which we need to query.
def get_url(server_name, listen_port):
    """
        Generating URL to get the information
        from namenode/namenode

    :param server_name:
    :param listen_port:
    :return:
    """

    if listen_port < 0:
        print ("Invalid Port")
        exit()

    if not server_name:
        print("Pass valid Hostname")
        exit()

    URL = "http://"+server_name+":"+str(listen_port)+"/jmx"
    return URL


# ---------------------------------
# Load URL
# ---------------------------------
def load_url_as_dictionary(url):
    """
        Loading JSON URL which we recieved from
        namenode/namenode

    :param url:
    :return:
    """
    # Server URL to get JSON information
    return json.load(urllib.urlopen(url))


# ---------------------------------
# Check value type - int/float/str
# ---------------------------------
def check_value_type(value):
    """
        Check value type so that we can process
        them differently

    :param value:
    :return:
    """
    if isinstance(value, int):
        return int(value)
    elif isinstance(value, float):
        return float(value)
    else:
        return str(value).strip()


# ---------------------------------
# Processing JSON data to get key/value data
# ---------------------------------
def processing_json(category, json_data, module_name):
    """
        Processing JSON data to get key/value data.
        Key will contain the zabbix item-name
        value JSON reponse value.

        This k/v will be further processed to
        generate XML or send data to Zabbix server.

    :param category:
    :param json_data:
    :param module_name:
    :return:
    """

    send_value = dict()
    for item in category:
        for key in json_data['beans'][item]:

            # Skip Name - as this is the Category information,
            # which we have already processed.
            if key == 'name':
                continue

            # All data which are not dict/list.
            elif not isinstance(json_data['beans'][item][key], dict) and \
                    not isinstance(json_data['beans'][item][key], list):
                zbx_key = re.sub('[\[\]/=*:\.,\'\"><]', '', str(module_name[item] + '_' + key).strip())
                zbx_value = json_data['beans'][item][key]
                send_value[zbx_key] = zbx_value
                logging.debug("Adding Key/Value to Dictionary, Key : " + str(zbx_key) + " / Value : " + str(zbx_value))


            # If we have dictinary then we create key/value of that dictionary.
            elif isinstance(json_data['beans'][item][key], dict):
                for value_in_sub in json_data['beans'][item][key]:
                    zbx_key = re.sub('[\[\]/=*:\.,\'\"><]', '', str(module_name[item] + '_' +
                                        key + '_' + value_in_sub).strip())
                    zbx_value = json_data['beans'][item][key][value_in_sub]
                    send_value[zbx_key] = zbx_value
                    logging.debug("Adding Key/Value to Dictionary, Key : " +
                                        str(zbx_key) + " / Value : " + str(zbx_value))

            # This is specific processing for LiveNodes
            if key == "LiveNodes" or key == "VolumeInfo":
                dict_v = ast.literal_eval(json_data['beans'][item][key])
                for key_live in dict_v:
                    for item_live in dict_v[key_live]:
                        zbx_key = re.sub('[\[\]/=*:\.,\'\"><]', '', str(module_name[item] + '_' +
                                            key + '_' + key_live + '_' + item_live).strip())
                        zbx_value = dict_v[key_live][item_live]
                        send_value[zbx_key] = zbx_value
                        logging.debug("Adding Key/Value to Dictionary, Key : " +
                                            str(zbx_key) + " / Value : " + str(zbx_value))
    return send_value


# ---------------------------------
# Sending Data to Zabbix Server
# ---------------------------------
def send_data_to_zabbix(send_data_from_dict, host_name, zbx_server_ip, zbx_server_port):
    """
        Once we have the processed data as Key/Value pair.
        Now we create a Metric JSON which is similar to below.
        Using Zabbix Metric

        {
            "request":"sender data",
            "data":[
                    {
                        "host":"Host name 1",
                        "key":"item_key",
                        "value":"33",
                        "clock":"123123123123"
                    },
                    {
                        "host":"Host name 2",
                        "key":"item_key",
                        "value":"55",
                        "clock":"23423423423"
                    }
                ]
            }

        'Clock' is taken as the current system time when the JSON was picked up.

    :param send_data_from_dict:
    :param host_name:
    :param zbx_server_ip:
    :param zbx_server_port:
    :return:
    """
    clock = time.time()
    send_data_list = []

    # Creating JSON
    for keys in send_data_from_dict:
        send_data_list.append(zbxsend.Metric(host_name, keys, send_data_from_dict[keys], clock))

    logging.info("Sending Data to Zabbix Server, for Host : " + str(host_name))
    logging.info("Zabbix IP : " + str(zabbix_server_ip))
    logging.info("Zabbix Port : " + str(zbx_server_port))

    # Sending JSON to Zabbix Server.
    zbxsend.send_to_zabbix(send_data_list, zabbix_host=zbx_server_ip, zabbix_port=zbx_server_port)



# ---------------------------------
# Generate Zabbix Items
# ---------------------------------
def generate_items_xml_file_complete(
                                    dict_from_json_processing,
                                    host_name,
                                    host_group_name,
                                    host_interface,
                                    host_application_name=None):

    """
        Create Zabbix XML Import file, to create Items in the Zabbix server.
        This is again done using the key/value pair which we generated in the process JSON phase.

    :param dict_from_json_processing:
    :param host_name:
    :param host_group_name:
    :param host_interface:
    :param host_application_name:
    :return:
    """


    # Date format for the new file created.
    fmt = '%Y-%m-%dT%H:%M:%SZ'

    # Creating the main element.
    zabbix_export = Element('zabbix_export')

    # Sub Element which fall under zabbix_export
    version = SubElement(zabbix_export, 'version')
    date =  SubElement(zabbix_export, 'date')

    # Groups
    groups = SubElement(zabbix_export, 'groups')
    group_under_groups = SubElement(groups, 'group')
    name_under_group = SubElement(group_under_groups, 'name')

    # triggers
    SubElement(zabbix_export, 'triggers')

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
    applications = SubElement(host_under_hosts, 'applications')
    application = SubElement(applications, 'application')
    application_name = SubElement(application, 'name')
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
    host_under_host.text = host_name
    name_under_host.text = host_name
    name_under_group.text = host_group_name
    ip_under_interface.text = host_interface
    name_group_under_groups_host.text = host_group_name

    # Standard values
    version.text = '2.0'
    status_under_host.text = '0'
    ipmi_authtype_under_host.text = '-1'
    ipmi_privilege_under_host.text = '2'
    default_under_interface.text = '1'
    type_under_interface.text = '1'
    useip_under_interface.text = '1'
    port_under_interface.text = '10050'
    interface_ref_under_interface.text = 'if1'
    sub_macro.text = '{$SNMP_COMMUNITY}'
    value.text = 'public'
    application_name.text = host_application_name

    #
    # Processing through the list of OID from the list in the dictionary
    # This actually a range as in the csv file
    #   If we have set 'all_oid_range' as true, then we will process all the OID range for each OID
    #   Warning : There will be too many Items in the import file.
    #             BE CAREFUL WITH THE RANGE.
    #
    for key_from_dict in dict_from_json_processing:
        logging.info("Creating Item for : " + str(key_from_dict))
        item_creator(items, key_from_dict, dict_from_json_processing[key_from_dict])

    return ElementTree.tostring(zabbix_export)


# ---------------------------------
# Creating Individual Items from the Dictionary
# ---------------------------------
def item_creator(items, module_detail_dict_item_from_dictionary, value_data):
    """
        Creating items from the Dictionary.

    :param items:
    :param module_detail_dict_item_from_dictionary:
    :param value_data:
    :return:
    """
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
    name.text = module_detail_dict_item_from_dictionary

    # This has to be unique
    key.text = module_detail_dict_item_from_dictionary

    # For Verbose Mode
    logging.debug('Key Generated as : ' + str(key.text))

    #
    # Setting value type to get information in int to string.
    # Based on the input file.
    # TODO : Add more datatype based on the return information.
    #
    if isinstance(value_data, str):
        value_type.text = '4'
    elif isinstance(value_data, int):
        value_type.text = '2'
    elif isinstance(value_data, float):
        value_type.text = '0'
    else:
        value_type.text = '4'


    #
    # Setting SNMP v1, This will change as per requirement.
    # TODO : Put a condition here so that we can change this on the fly.
    #
    type.text = '2'

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
    delay.text = '30'
    history.text = '90'
    trends.text = '365'
    status.text = '0'
    multiplier.text = '0'

    # Adding Description as in the CSV file.
    description.text = 'Description For : ' + str(module_detail_dict_item_from_dictionary) + 'goes here.'

    # Creating all the items in a specific Application on Zabbix
    application_name.text = str(module_detail_dict_item_from_dictionary).split('_')[0]



# ---------------------------------
# XML pretty me.
# ---------------------------------
def xml_pretty_me(file_name_for_prettify, string_to_prettify):
    """
        Creating a preety XML tab seperated.

    :param file_name_for_prettify:
    :param string_to_prettify:
    :return:
    """
    #
    # Open a file and write to it and we are done.
    #
    logging.debug("Creating File pretty_%s", file_name_for_prettify)

    # Creating an XML and prettify xml.
    xml = minidom.parseString(string_to_prettify)
    pretty_xml_as_string = xml.toprettyxml()

    # Creating a file to write this information.
    output_file = open(file_name_for_prettify, 'w' )
    output_file.write(pretty_xml_as_string)

    # Done.
    logging.debug("Creation Complete")
    output_file.close()


# ---------------------------------
# Read Properties file to generate Catagory List.
# ---------------------------------
def read_properties_file(file_name):
    """
        This function is used to create the category list.
        Check properties files for more information.

        These categories are modules in the JSON we get from Namenode/Datanode.

    :param file_name:
    :return:
    """
    file_reader = open(file_name, 'r+')
    catagory_list = []

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

            line_split = line.split(":")
            # Create a {} to store.
            catagory_list.append(int(line_split[0]))

    return catagory_list


# ---------------------------------
# Generate Key Value pair
# ---------------------------------
def get_json_data_as_kv(hp_host_name, hp_host_port, properties_file):
    """
        Generating JSON Key value pair based on the category indices.

    :param hp_host_name:
    :param hp_host_port:
    :return:
    """
    category_to_process = read_properties_file(properties_file)
    # url_to_query = get_url(hp_host_name, hp_host_port)
    # logging.debug('URL to Query : ' + url_to_query)
    #
    # json_data = load_url_as_dictionary(url_to_query)

    json_data = temp_json_loading()
    create_modules = generate_module_dictionary(category_to_process, json_data)
    ready_dictionary = processing_json(category_to_process, json_data, create_modules)

    return ready_dictionary


# ---------------------------------
# Main Function
# ---------------------------------
if __name__ == "__main__":

    # Setting Log Level
    logging.basicConfig(level=logging.DEBUG)

    # create the top-level parser
    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
                                     description=textwrap.dedent('''

    Namenode Zabbix Monitoring
    ----------------------

    This script can be used to monitor Namenode Parameters.
    This script can be used to

    1. Generate Zabbix Import XML.
    2. Send monitoring data to Zabbix server.

    Parameter which are monitored are in the indexes of the JSON and are as below.
    category_to_process = Taken from the properties file namenode/namenode.properties

    ----------------------'''))

    parser.add_argument('-hh', '--hadoop-host-name',
                                help='Hadoop Hostname/IP to connect to get JSON file.', required=True)
    parser.add_argument('-hp', '--hadoop-host-port', default=50070,
                                help='Hadoop Hostname/IP Port to connect to. (default=50070)', required=True)
    parser.add_argument('-zh', '--zabbix-host-name', help='Hostname as in the Zabbix server.', required=True)
    parser.add_argument('-p', '--properties-file',
                                help='Select properties file to process, Namenode or Datanode', required=True)

    subparsers = parser.add_subparsers(help='sub-command help')

    # create the parser for the "xml-generator" command
    parser_xml_gen = subparsers.add_parser('xml-gen', help='\'xml-gen --help\' for more options')
    parser_xml_gen.add_argument('-zp', '--zabbix-host-port',
                                help='Host port as as in the Zabbix server. (Monitoring host)', required=True)
    parser_xml_gen.add_argument('-zi', '--zabbix-host-interface',
                                help='Host Interface as as in the Zabbix server.. (Monitoring host)', required=True)
    parser_xml_gen.add_argument('-zg', '--zabbix-host-group',
                                help='Host Group as in the Zabbix server. (Monitoring host)', required=True)
    parser_xml_gen.add_argument('-za', '--zabbix-host-application',
                                help='Host Application as in the Zabbix server. (Monitoring host)', required=True)


    # create the parser for the "send-data" command
    parser_send_data = subparsers.add_parser('send-data', help='\'send-data --help\' for more options')
    parser_send_data.add_argument('-zp', '--zabbix-port', default=10051, help='Zabbix port for sending data, default=10051')
    parser_send_data.add_argument('-zi', '--zabbix-server-ip', help='Zabbix server IP to send the Data to.', required=True)

    # For Testing
    str_cmd = '-hh hmhdmaster1 -hp 50070 -zh hmhdmaster1 ' \
              '-p resources/namenode.properties send-data -zp 10051 -zi 10.231.67.201'.split()
    str_cmd2 = '-hh hmhdmaster1 -hp 50070 -zh hmhdmaster1 -p resources/namenode.properties xml-gen -zp 10050 ' \
               '-zi 10.20.6.31 -zg Linux_Server -za hadoop'.split()
    str_help_xml = '-hh hmhdmaster1 -zh hmhdmaster1 xml-gen --help'.split()
    str_help_send = '-hh hmhdmaster1 -zh hmhdmaster1 send-data --help'.split()


    args = parser.parse_args(str_cmd)

    #
    # TODO : Dirty code to check 'SEND' or 'Create XML'.
    #
    type_proc = ''
    try:
        if args.zabbix_server_ip:
            type_proc = 'SEND'
    except:
        if args.zabbix_host_port:
            type_proc = 'XML'

    # Send Data to Zabbix
    if type_proc == 'SEND':
        # Common Parameters
        hadoop_host_name = args.hadoop_host_name
        hadoop_host_port = args.hadoop_host_port
        zabbix_host_name = args.zabbix_host_name
        node_properties = args.properties_file

        # Paramete to send the data to.
        zabbix_port = args.zabbix_port
        zabbix_server_ip = args.zabbix_server_ip

        # Generating k/v pairs
        key_value_pairs = get_json_data_as_kv(hadoop_host_name, hadoop_host_port, node_properties)

        # Send data
        send_data_to_zabbix(key_value_pairs, str(zabbix_host_name), str(zabbix_server_ip), int(zabbix_port))

    # Create Item for Zabbix (Export.xml)
    elif type_proc == 'XML':

        # Common Parameters
        hadoop_host_name = args.hadoop_host_name
        hadoop_host_port = args.hadoop_host_port
        zabbix_host_name = args.zabbix_host_name
        node_properties = args.properties_file

        # XML specific Parameters
        zabbix_host_port = args.zabbix_host_port
        zabbix_host_interface = args.zabbix_host_interface
        zabbix_host_group = args.zabbix_host_group
        zabbix_host_application = args.zabbix_host_application

        # Create k/v pairs
        key_value_pairs = get_json_data_as_kv(hadoop_host_name, hadoop_host_port, node_properties)

        # Generate XML file.
        xml_string = generate_items_xml_file_complete(key_value_pairs, zabbix_host_name,
                                                      zabbix_host_group, zabbix_host_interface,
                                                      zabbix_host_application)
        xml_pretty_me(str(zabbix_host_name).lower() + '_' + zabbix_host_interface + '_export.xml', xml_string)

    # Should not reach here.
    else:
        parser.print_help()
