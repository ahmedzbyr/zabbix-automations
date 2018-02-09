#!/usr/bin/python

__author__ = 'ahmed'


#
# Import required packages.
#
import xmltodict  # Need to install this
import logging
from dateutil import parser
from calendar import timegm
import sys
import os.path
import argparse
import textwrap

sys.path.insert(0, '../zbxsend/')  # Assuming zbxsend is in the same Hierarchy
import zbxsend  # This package can be installed from : https://github.com/ahmedzbyr/zbxsend

#
# Creating an Email Notification.
#
# NOTE :
# Will need to setup mailx for this setup.
#       HOWTO : Setup mailx can be found in link below.
#       http://whatizee.blogspot.in/2013/12/installing-and-config-heirloom-mailx.html
#
def email_body_header(about_info):
    bodyHeader = "echo -e \"Hi Team,\\n\\nBelow are the Details about " + about_info + " \\n"
    return bodyHeader


def email_body_footer(about_info):
    body_footer = "\\n\\nIMPORTANT : " + about_info.upper() + "." \
                                                              "\\n\\nBest Regards,\\nOperations Team\\n\\n--\\nPlease do not respond to this mail. " \
                                                              "For any queries Contact operations@me.com\\n\\n\""
    return body_footer


def email_body_message(body_message):
    return body_message


def email_subject_message(service_type):
    subject_and_mailing = "| mailx -v -A mail_me -s \"ERROR : " + service_type + " Service. Current Time : $(date +%H:%M)\" 'zubair.ahmed@me.com'"
    return subject_and_mailing


# Executing system command
def command_executor(command):
    # Executing generated shell script on the server.
    response = os.system(command)

    # If we get 0, then all is well.
    if response == 0:
        logging.info("Execution Successful")


# --------------------------------------------------------
# Loading XML as a dictionary.
# --------------------------------------------------------
def load_xml_as_dictionary(file_name):
    try:
        # Open a file in read-only mode
        document_file = open(file_name, "r")

        # read the file object
        original_document = document_file.read()

        # Parse the read document string
        dictionary_document = xmltodict.parse(original_document)
        return dictionary_document

    # Exit if there is an issue.
    except:
        logging.exception("Could not read XML file please check, Exiting Now.")
        exit()


# --------------------------------------------------------
# All KPI count
# --------------------------------------------------------
def generate_kpi_count(dictionary_xml_document_for_counters):
    # Logging Info
    logging.info("Generating KPI count Dictionary")

    dictionary_all_kpi_count = {}
    main_kpi_count = 0
    #
    # Traverse through the dictionary and get all the Main KPI and Sub KPI counts.
    #
    for item in dictionary_xml_document_for_counters["measCollecFile"]["measData"]["measInfo"]:
        sub_kpi_count = 0

        # Getting Sub KPI count
        for data in item['measType']:
            sub_kpi_count += 1

        # Store this information in Dictionary.
        dictionary_all_kpi_count[main_kpi_count] = sub_kpi_count
        main_kpi_count += 1

    # Logging for debugging
    logging.debug(dictionary_all_kpi_count)

    return dictionary_all_kpi_count


# --------------------------------------------------------
# KPI list generator
# --------------------------------------------------------
def generate_kpi_list(dictionary_xml_document_for_list, dictionary_all_kpi_index_count_for_list):
    # Logging Info
    logging.info("Starting to generate - KPI LIST")

    index = -1
    for item in dictionary_xml_document_for_list["measCollecFile"]["measData"]["measInfo"]:
        try:
            if isinstance(item['measValue']['r'], dict):
                # Increment and Pop the item from the Dictionary
                index += 1
                dictionary_all_kpi_index_count_for_list.pop(index)

                # Logging for debugging
                logging.debug("Index %s, DICTIONARY", index)

            else:
                # Increment, as this is the item we need so do nothing.
                index += 1

                # Logging for debugging
                logging.debug("Index: %s, NOT DICTIONARY", index)
        except:

            # Increment and Pop the item from the Dictionary
            index += 1
            dictionary_all_kpi_index_count_for_list.pop(index)

            # Logging for debugging
            logging.debug("Index: %s, EXCEPTION", index)
            continue

    # Logging for debugging
    logging.debug("Total KPI in XML File : %s", index + 1)
    logging.debug(dictionary_all_kpi_index_count_for_list)

    return dictionary_all_kpi_index_count_for_list, index


# --------------------------------------------------------
# Generating List of KPI from XML, used to send ALL KPI data to Server
# --------------------------------------------------------
def generate_properties_list(dictionary_kpi_data_gen_list, total_index_gen_list):
    # Logging Info
    logging.info("Starting properties list generation.")

    # Create a new list which we can use instead of Properties file.
    create_properties_list = []
    for data in dictionary_kpi_data_gen_list:
        # Sub List to keep data together. Add data to the list
        single_property_list = ["KEY_VALUE", total_index_gen_list + 1, data, dictionary_kpi_data_gen_list[data]]

        # Add list to a bigger list.
        create_properties_list.append(single_property_list)

    # Logging for debugging
    logging.debug(create_properties_list)

    return create_properties_list


# --------------------------------------------------------
# Generating properties file.
#   1. Use of properties file is the send specific data from
#       the file.
#   2. '#' is used as comment in the properties file.
#   3. if there are few KPI's which needs to be sent the we
#       comment the rest of the information.
# --------------------------------------------------------
def generate_properties_file(dictionary_kpi_data_for_file, total_index_for_file, xml_file_name_to_process):
    # Logging Info
    logging.info("Starting properties file generation. Filename : \'%s.properties\'", xml_file_name_to_process)

    # Create a file to write to.
    output_file = open(xml_file_name_to_process + '.properties', 'w')

    # Run through the dictionary
    for data in dictionary_kpi_data_for_file:
        # Logging for Debugging
        logging.debug("KEY_VALUE," + str(total_index_for_file + 1) + "," + str(data) + ',' + str(
            dictionary_kpi_data_for_file[data]))
        # Write to file.
        output_file.write("KEY_VALUE," + str(total_index_for_file + 1) + "," + str(data) + ',' + str(
            dictionary_kpi_data_for_file[data]) +
                          "\n")

    # We are done, do close file.
    output_file.close()


# --------------------------------------------------------
# Send data from XML directly to server (ALL) data.
# --------------------------------------------------------
def send_data_to_server_from_list(properties_list_to_process, host_name_for_list,
                                  zabbix_server_name_ip_for_list,
                                  zabbix_server_port_for_list=10051):
    SEND_EMAIL_ONCE = True
    for process_list_item in properties_list_to_process:

        sender_value = []
        #
        # Process file
        # which are direct key/values in the XML and the
        # Processing is ACTIVE to send the data to Server.
        #
        if process_list_item[0] == "KEY_VALUE":
            #
            for item_in in range(0, int(process_list_item[3])):
                key = dictionary_xml_document["measCollecFile"]["measData"]["measInfo"][int(process_list_item[2])][
                          '@measInfoId'] + '_' + \
                      dictionary_xml_document["measCollecFile"]["measData"]["measInfo"][int(process_list_item[2])][
                          "measType"][item_in]["#text"]
                value = dictionary_xml_document["measCollecFile"]["measData"]["measInfo"][int(process_list_item[2])][
                    "measValue"]["r"][item_in]["#text"]

                # Pick the datetime from the XML and convert to timestampe
                end_time = dictionary_xml_document["measCollecFile"]["measData"]["measInfo"][int(process_list_item[2])][
                    'granPeriod']['@endTime']
                date_info = parser.parse(end_time)
                clock = timegm(date_info.timetuple())
                logging.debug('Date' + str(end_time) + ' -> (Time Stamp)' + str(clock))

                # Appending all Metric data together.
                sender_value.append(zbxsend.Metric(host_name_for_list, str(key), float(value), float(clock)))

            logging.debug(sender_value)
            sent_to_zabbix = zbxsend.send_to_zabbix(sender_value, zabbix_server_name_ip_for_list,
                                                    zabbix_server_port_for_list)
            if sent_to_zabbix == False and SEND_EMAIL_ONCE == True:
                email_head = email_body_header("Python XML Processing")
                email_body = email_body_message("Communication To Zabbix Server has failed. Please check Connectivity.")
                email_footer = email_body_footer("Python XML Processing has Failed")
                email_subject_and_send = email_subject_message("Python XML Processing")
                command_executor(email_head + email_body + email_footer + email_subject_and_send)
                SEND_EMAIL_ONCE = False

        #
        # TODO : Processing SUB TREE in XML.
        #
        elif process_list_item[0] == "KEY_VALUE_TREE_APN":
            logging.debug("passing APN for now")

        #
        # TODO : Processing SUB TREE in XML.
        #
        elif process_list_item[0] == "KEY_VALUE_TREE_IP":
            logging.debug("passing IP for now")

    #
    # Skip if line is commented
    #
    else:
        logging.debug(process_list_item)


# --------------------------------------------------------
# Sending data from a properties file.
#   1. Use of properties file is the send specific data from
#       the file.
#   2. '#' is used as comment in the properties file.
#   3. if there are few KPI's which needs to be sent the we
#       comment the rest of the information.
# --------------------------------------------------------
def send_data_to_server_from_file(properties_filename, host_name_for_file,
                                  zabbix_server_name_ip_for_file,
                                  zabbix_server_port_for_file=10051):
    # Reading Property file for processing XML file.
    file_reader = open(properties_filename, "r")

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
            sender_value = []

            # Adding Debugging
            logging.debug(list_of_values)

            #
            # Process file
            # which are direct key/values in the XML and the
            # Processing is ACTIVE to send the data to Server.
            #
            if list_of_values[0] == "KEY_VALUE":
                #
                for item_in in range(0, int(list_of_values[3])):
                    key = dictionary_xml_document["measCollecFile"]["measData"]["measInfo"][int(list_of_values[2])]['@measInfoId'] +\
                          '_'+dictionary_xml_document["measCollecFile"]["measData"]["measInfo"][int(list_of_values[2])]["measType"][item_in]["#text"]
                    value = dictionary_xml_document["measCollecFile"]["measData"]["measInfo"][int(list_of_values[2])]["measValue"]["r"][item_in]["#text"]

                    # Pick the datetime from the XML and convert to timestampe
                    end_time = dictionary_xml_document["measCollecFile"]["measData"]["measInfo"][int(list_of_values[2])]['granPeriod']['@endTime']
                    date_info = parser.parse(end_time)
                    clock = timegm(date_info.timetuple())
                    logging.debug('Date' + str(end_time) + ' -> (Time Stamp)' + str(clock))

                    # Appending all Metric data together.
                    sender_value.append(zbxsend.Metric(host_name_for_file, str(key), float(value), float(clock)))

                logging.debug(sender_value)
                sent_to_zabbix = zbxsend.send_to_zabbix(sender_value, zabbix_server_name_ip_for_file,
                                                        int(zabbix_server_port_for_file))

                if sent_to_zabbix == False and SEND_EMAIL_ONCE == True:
                    email_head = email_body_header("Python XML Processing")
                    email_body = email_body_message(
                        "Communication To Zabbix Server has failed. Please check Connectivity.")
                    email_footer = email_body_footer("Python XML Processing has Failed")
                    email_subject_and_send = email_subject_message("Python XML Processing")
                    command_executor(email_head + email_body + email_footer + email_subject_and_send)
                    SEND_EMAIL_ONCE = False

                    # let Exit as we might get same timeout for other KPIs as well.
                    exit()

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

        #
        # Skip if line is commented
        #
        else:
            logging.debug(process_line)


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
    python zabbix_send_from_kpi_xml.py --kpi-xml <source_xml_file> --generate-properties
        example: python zabbix_send_from_kpi_xml.py --kpi-xml KPI_SOURCE_FILE.xml --generate-properties --debug

     2. Send all KPI from the xml to server.
     --------------------------------------------
    python zabbix_send_from_kpi_xml.py --kpi-xml <source_xml_file> --zabbix-server-ip <zabbix_server_ip> --zabbix-server-port <zabbix_server_port> --host-name <host_name> --all --debug
        example: python zabbix_send_from_kpi_xml.py --kpi-xml KPI_SOURCE_FILE.xml --zabbix-server-ip 127.0.0.1 --zabbix-server-port 10051 --host-name ams-ggsn --all --debug

     3. Send KPI from properties file.
     --------------------------------------------
    python zabbix_send_from_kpi_xml.py --kpi-xml <source_xml_file> --zabbix-server-ip <zabbix_server_ip> --zabbix-server-port <zabbix_server_port> --host-name <host_name> --properties-file <properties_file> --debug
        example:  python zabbix_send_from_kpi_xml.py --kpi-xml KPI_SOURCE_FILE.xml --zabbix-server-ip 127.0.0.1 --zabbix-server-port 10051 --host-name ams-ggsn --properties-file KPI_SOURCE_FILE.xml.properties --debug

     """)
    exit()


# --------------------------------------------------------
# Process XML and send data to Zabbix Server.
# --------------------------------------------------------
if __name__ == '__main__':

    command_line_opt = argparse.ArgumentParser("Send Zabbix metric by reading from a XML file. "
                                               "This needs package zbxsend from : https://github.com/ahmedzbyr/zbxsend"
                                               "Step 1 : Install zbxsend"
                                               "Step 2 : Install xmltodict")
    command_line_opt.add_argument('-x', '--kpi-xml', help='Is the XML KPI file for Device.', required=True)
    command_line_opt.add_argument('-i', '--zabbix-server-ip',
                                  help='IP address of the Zabbix Server to which this data needs to be sent.')
    command_line_opt.add_argument('-s', '--zabbix-server-port',
                                  help='Port which Zabbix server is listening (Default : 10051).', default=10051,
                                  type=int)
    command_line_opt.add_argument('-n', '--host-name', help='Host name as given in Zabbix server.')
    command_line_opt.add_argument('-p', '--properties-file',
                                  help='This is the file which is generated using option (1). \'#\' is comment in properties file.')
    command_line_opt.add_argument('-a', '--all',
                                  help='Application Name in the Zabbix Server. (To organize all items being imported)',
                                  action="store_true")
    command_line_opt.add_argument('-g', '--generate-properties',
                                  help='Include First line (Header) in the CSV file input, [Default : False]',
                                  action="store_true")
    command_line_opt.add_argument('-d', '--debug', help='Running Debug mode - More Verbose', action="store_true")
    command_line_opt.add_argument('-v', '--version', help="Show script version", action="version",
                                  version="kpi metric sender 0.1.0".upper())

    args = command_line_opt.parse_args()
    xml_file_name = args.kpi_xml

    if args.debug or args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    if not os.path.isfile(xml_file_name):
        logging.error("xml File Not Present")
        command_line_opt.print_help()

    # Loading XML as a Dictionary
    dictionary_xml_document = load_xml_as_dictionary(xml_file_name)
    # Create ALL kpi list
    dictionary_kpi_data = generate_kpi_count(dictionary_xml_document)

    # Create KPI list we need
    dictionary_kpi_data, total_index = generate_kpi_list(dictionary_xml_document, dictionary_kpi_data)

    if args.generate_properties and args.kpi_xml:
        # Logging for debugging
        logging.debug("GENERATE_PROPERTIES")

        # Create File
        generate_properties_file(dictionary_kpi_data, total_index, xml_file_name)

    elif args.kpi_xml and args.zabbix_server_ip and args.zabbix_server_port and args.host_name and args.all:
        # Logging for Debugging.
        logging.debug("Sending all KPI information from the XML file")

        # Setting Information to send data
        zabbix_server_name_ip = str(args.zabbix_server_ip)
        zabbix_server_port = int(args.zabbix_server_port)
        host_name = str(args.host_name)

        # Create Properties list.
        properties_list = generate_properties_list(dictionary_kpi_data, total_index)

        # Sending Data to Server.
        send_data_to_server_from_list(properties_list, host_name, zabbix_server_name_ip, zabbix_server_port)

    elif args.kpi_xml and args.zabbix_server_ip and args.zabbix_server_port and args.host_name and args.properties_file:
        # Logging for Debugging.
        logging.debug("Sending Data from Properties file")

        # Setting Information to send data
        zabbix_server_name_ip = str(args.zabbix_server_ip)
        zabbix_server_port = int(args.zabbix_server_port)
        host_name = str(args.host_name)

        # Properties files Name
        properties_file_name = str(args.properties_file)

        if not os.path.isfile(properties_file_name):
            logging.error("Properties File Not Present")
            command_line_opt.print_help()

        send_data_to_server_from_file(properties_file_name, host_name, zabbix_server_name_ip, zabbix_server_port)

    else:
        command_line_opt.print_help()
        help_menu()