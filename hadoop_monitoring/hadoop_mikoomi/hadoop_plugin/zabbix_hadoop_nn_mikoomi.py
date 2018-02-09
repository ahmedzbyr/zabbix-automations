__author__ = 'ahmed'

import json
import urllib
import logging
import sys


# ---------------------------------
# Temp JSON loader function
# returns - json_data for processing
# ---------------------------------
def temp_json_loading():
    """
    This is a temp json loader for testing.
    :return: json data
    """
    file_desc = open('NAMENODE.json', 'r+')
    data = json.load(file_desc)
    return data

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


def json_processing(json_dict):

    TB = 1024 * 1024 * 1024 * 1024
    GB = 1024 * 1024 * 1024
    MB = 1024 * 1024
    KB = 1024

    namenode_dict = {}
    namenode_dict['start_time'] = int(str(json_dict['beans'][18]['StartTime'])[:10])
    namenode_dict['hadoop_version'] = str(json_dict['beans'][27]['Version']).split(',')[0]
    namenode_dict['file_and_directory_count'] = json_dict['beans'][27]['TotalFiles']
    namenode_dict['dfs_blocks'] = json_dict['beans'][27]['TotalBlocks']
    namenode_dict['namenode_process_heap_size'] = json_dict['beans'][15]['MemHeapUsedM']
    namenode_dict['max_heap_size'] = json_dict['beans'][15]['MemMaxM'] / 1024
    namenode_dict['storage_unit'] = 'TB'
    namenode_dict['configured_cluster_storage'] = min_value_display(float(json_dict['beans'][27]['Total']) / TB)
    namenode_dict['dfs_use_storage'] = min_value_display(float(json_dict['beans'][27]['Used']) / TB)
    namenode_dict['non_dfs_use_storage'] = min_value_display(float(json_dict['beans'][27]['NonDfsUsedSpace']) / TB)
    namenode_dict['available_dfs_storage'] = min_value_display(float(json_dict['beans'][27]['Free']) / TB)
    namenode_dict['used_storage_pct'] = min_value_display(float(json_dict['beans'][27]['PercentUsed']))
    namenode_dict['available_storage_pct'] = json_dict['beans'][27]['PercentRemaining']
    namenode_dict['live_nodes'] = json_dict['beans'][16]['NumLiveDataNodes']
    namenode_dict['dead_nodes'] = json_dict['beans'][16]['NumDeadDataNodes']
    namenode_dict['decommissioned_nodes'] = json_dict['beans'][16]['NumStaleDataNodes']
    namenode_dict['under_repllicated_nodes'] = json_dict['beans'][16]['UnderReplicatedBlocks']

    live_node =  json.loads(json_dict['beans'][27]['LiveNodes'])

    HIGH_CONST = 99999
    LOW_CONST = -99999

    max_capacity = LOW_CONST
    min_capacity = HIGH_CONST

    max_used_space = LOW_CONST
    min_used_space = HIGH_CONST

    max_non_dfs_used_space = LOW_CONST
    min_non_dfs_used_space = HIGH_CONST

    max_free_storage = LOW_CONST
    min_free_storage = HIGH_CONST

    max_used_storage_pct = LOW_CONST
    min_used_storage_pct = HIGH_CONST

    max_free_storage_pct = LOW_CONST
    min_free_storage_pct = HIGH_CONST

    for live_node_in_list in live_node:

        live_node_name = live_node_in_list
        capacity = float(live_node[live_node_in_list]['capacity']) / TB
        used_space = float(min_value_display(float(live_node[live_node_in_list]['usedSpace']) / TB))
        non_dfs_used_space = float(live_node[live_node_in_list]['nonDfsUsedSpace']) / TB

        free_capacity = capacity - used_space - non_dfs_used_space
        free_capacity_pct = free_capacity / capacity * 100
        used_space_pct = ((capacity - free_capacity) / capacity) * 100

        logging.debug("------------------------")
        logging.debug("live_node_name : " + str(live_node_name))
        logging.debug("capacity : " + str(capacity))
        logging.debug("used_space : " + str(used_space))
        logging.debug("non_dfs_used_space : " + str(non_dfs_used_space))
        logging.debug("free_capacity : " + str(free_capacity))
        logging.debug("free_capacity_pct : " + str(free_capacity_pct))
        logging.debug("used_space_pct : " + str(used_space_pct))
        logging.debug("------------------------")

        if capacity > max_capacity:
            max_capacity = capacity
            namenode_dict['max_configured_storage'] = max_capacity
            namenode_dict['max_configured_storage_node_name'] = live_node_name

        if capacity < min_capacity:
            min_capacity = capacity
            namenode_dict['min_configured_storage'] = min_value_display(min_capacity)
            namenode_dict['min_configured_storage_node_name'] = live_node_name

        if used_space > max_used_space:
            max_used_space = used_space
            namenode_dict['max_used_storage'] = min_value_display(max_used_space)
            namenode_dict['max_used_storage_node_name'] = live_node_name

        if used_space < min_used_space:
            min_used_space = used_space
            namenode_dict['min_used_storage'] = min_value_display(min_used_space)
            namenode_dict['min_used_storage_node_name'] = live_node_name

        if non_dfs_used_space > max_non_dfs_used_space:
            max_non_dfs_used_space = non_dfs_used_space
            namenode_dict['max_non_dfs_used_storage'] = min_value_display(max_non_dfs_used_space)
            namenode_dict['max_non_dfs_used_storage_node_name'] = live_node_name

        if non_dfs_used_space < min_non_dfs_used_space:
            min_non_dfs_used_space = non_dfs_used_space
            namenode_dict['min_non_dfs_used_storage'] = min_value_display(min_non_dfs_used_space)
            namenode_dict['min_non_dfs_used_storage_node_name'] = live_node_name

        if free_capacity > max_free_storage:
            max_free_storage = free_capacity
            namenode_dict['max_free_storage'] = max_free_storage
            namenode_dict['max_free_storage_node_name'] = live_node_name

        if free_capacity < min_free_storage:
            min_free_storage = free_capacity
            namenode_dict['min_free_storage'] = min_value_display(min_free_storage)
            namenode_dict['min_free_storage_node_name'] = live_node_name


        if used_space_pct > max_used_storage_pct:
            max_used_storage_pct = free_capacity_pct
            namenode_dict['max_used_storage_pct'] = max_used_storage_pct
            namenode_dict['max_used_storage_pct_node_name'] = live_node_name

        if used_space_pct < min_used_storage_pct:
            min_used_storage_pct = free_capacity_pct
            namenode_dict['min_used_storage_pct'] = min_value_display(min_used_storage_pct)
            namenode_dict['min_used_storage_pct_node_name'] = live_node_name

        if free_capacity_pct > max_free_storage_pct:
            max_free_storage_pct = free_capacity_pct
            namenode_dict['max_free_storage_pct'] = max_free_storage_pct
            namenode_dict['max_free_storage_pct_node_name'] = live_node_name

        if free_capacity_pct < min_free_storage_pct:
            min_free_storage_pct = free_capacity_pct
            namenode_dict['min_free_storage_pct'] = min_value_display(min_free_storage_pct)
            namenode_dict['min_free_storage_pct_node_name'] = live_node_name


    logging.debug(namenode_dict['max_configured_storage'])
    logging.debug(namenode_dict['max_configured_storage_node_name'])
    logging.debug(namenode_dict['min_configured_storage'])
    logging.debug(namenode_dict['min_configured_storage_node_name'])
    logging.debug(namenode_dict['max_used_storage'])
    logging.debug(namenode_dict['max_used_storage_node_name'])
    logging.debug(namenode_dict['min_used_storage'])
    logging.debug(namenode_dict['min_used_storage_node_name'])
    logging.debug(namenode_dict['max_non_dfs_used_storage'])
    logging.debug(namenode_dict['max_non_dfs_used_storage_node_name'])
    logging.debug(namenode_dict['min_non_dfs_used_storage'])
    logging.debug(namenode_dict['min_non_dfs_used_storage_node_name'])
    logging.debug(namenode_dict['max_free_storage'])
    logging.debug(namenode_dict['max_free_storage_node_name'])
    logging.debug(namenode_dict['min_free_storage'])
    logging.debug(namenode_dict['min_free_storage_node_name'])
    logging.debug(namenode_dict['max_used_storage_pct'])
    logging.debug(namenode_dict['max_used_storage_pct_node_name'])
    logging.debug(namenode_dict['min_used_storage_pct'])
    logging.debug(namenode_dict['min_used_storage_pct_node_name'])
    logging.debug(namenode_dict['max_free_storage_pct'])
    logging.debug(namenode_dict['max_free_storage_pct_node_name'])
    logging.debug(namenode_dict['min_free_storage_pct'])
    logging.debug(namenode_dict['min_free_storage_pct_node_name'])

    return namenode_dict

def write_data_to_file(json, file_path, hadoop_name_in_zabbix):
    txt_file = open(file_path, 'w+')
    for keys in json:
        txt_file.writelines(hadoop_name_in_zabbix +' '+ str(keys) +' '+ str(json[keys]) + '\n')


def usage():
    print '''
            Usage: $SCRIPT_NAME <hadoop_host> <hadoop_port> <file_path> <zabbix_server_name>
    '''

def min_value_display(x):
    return '{0:.5f}'.format(x)


if __name__ == '__main__':

    logging.basicConfig(level=logging.INFO)
    if len(sys.argv) == 5:

        namenode_name = sys.argv[1]
        namenode_listen_port = sys.argv[2]
        file_path = sys.argv[3]
        nodename_in_zabbix = sys.argv[4]

        url = get_url(namenode_name, namenode_listen_port)
        json_as_dictionary = load_url_as_dictionary(url)
        json_processed = json_processing(json_as_dictionary)
        write_data_to_file(json_processed, file_path, nodename_in_zabbix)

    else:
        usage()

