## Zabbix Item Creation using OID and Name CSV files.

This script is to create a xml import file from a csv file.
We use 2 csv file for this.

1. **First is the OID csv file**. This OID file will contain all the range of OIDs which can be configured on the device. OID CSV will be similar to the CSV sample given below.
2. **Information (Name) configured in those OIDs above, with index**. This file contains all the configuration information done on the device. Will give the index of the configured variable.
 

### CSV format as below 

Below is the OID csv file. **(We will called it OID CSV File)** 

module_name|oid_name|oid|datatype|start|end|description
-----------|------|------|------|------|------|---------
voip_destination|status|1.3.6.1.2.1.2.2.18.0|string|0|1000|some description
voip_destination|flags|1.3.6.1.2.1.2.2.18.1|string|0|1000|some description
voip_destination|type|1.3.6.1.2.1.2.2.18.2|string|0|1000|some description

Here is the sample csv output for the above file.
 
    module_name,oid_name,oid,datatype,start,end,description
    voip_destination,status,1.3.6.1.2.1.2.2.18.0,string,0,1000,some description
    voip_destination,flags,1.3.6.1.2.1.2.2.18.1,string,0,1000,some description
    voip_destination,type,1.3.6.1.2.1.2.2.18.2,string,0,1000,some description


Below is name (configured) oid information, in the OIDs above. **(We will called it NAME CSV File)**.
We use the name_table.`module-name` below to join with the table above with oid_table.`module_name`.

module_name|index|name
-----------|------|---------
voip_destination|0|test_data_44test
linkset|1|test_data_44tes
ip|0|test_datatest

Here is the sample csv output for the above file.

    module_name,TEST_DATAdex,TEST_DATAmTEST
    Linkset,0,TEST_DATA_44TEST
    Linkset,1,TEST_DATA_44TEST
    IP,0,TEST_DATATEST
    IP,1,TEST_DATAlTEST
    IP,2,TEST_DATAteTEST



### USAGE


    usage: zabbix_items_from_csv.py [-h] -o CSV_OID -c CSV_NAME -n HOST_NAME -g
                                    HOST_GROUP -i HOST_INTERFACE -a
                                    HOST_APPLICATION [-y] [-f]
    
    This script is to Generate xml import file for Zabbix from CSV files.We need
    two CSV files.1. OID file, gives all the OIDs in the device.2. Name file,
    gives all names configured for the above OIDs in the Device. 
    
    Example : python -o oid_list_with_range_processed.csv -c oid_names_configured.csv -n
    GGSN-1-LONDON -g GGSN-GROUP -i 127.0.0.1 -a GGSN-APP-OIDS -y
    
    optional arguments:
      -h, --help            show this help message and exit
      -o CSV_OID, --csv-oid CSV_OID
                            OID file, Gives all OIDs on the device
      -c CSV_NAME, --csv-name CSV_NAME
                            Name file, gives all names configured for the above
                            OIDs in the Device.
      -n HOST_NAME, --host-name HOST_NAME
                            Host name as given in Zabbix server.
      -g HOST_GROUP, --host-group HOST_GROUP
                            Host Group which the host belongs to, as in Zabbix
                            server.
      -i HOST_INTERFACE, --host-interface HOST_INTERFACE
                            SNMP Interface configured on Zabbix server. (Assuming
                            Single Interface in Configured)
      -a HOST_APPLICATION, --host-application HOST_APPLICATION
                            Application Name in the Zabbix Server. (To organize
                            all items being imported)
      -y, --only-name       Create xml items which are present in the name file.
                            i.e create items which are configured in the device
                            already, Rest of the OIDs are Ignored. [Default :
                            False]
      -f, --include-first-line
                            Include First line (Header) in the CSV file input,
                            [Default : False]
                            
### Code Usage :

```python
import zabbix_items_from_csv

#-----------------------
# Limit reading to first 10 Lines.
#-----------------------
complete_list_dict_device_1 =  zabbix_items_from_csv.reader_csv_file('oid_list_with_range_processed.csv', 10)
complete_list_name_dict_device_1 = zabbix_items_from_csv.read_csv_name_module('oid_names.csv')
dict_device_1 = zabbix_items_from_csv.merge_csv_data(complete_list_dict_device_1, complete_list_name_dict_device_1, True)
xml_tree_string_device_1 = zabbix_items_from_csv.\
                            generate_items_xml_file_complete(dict_device_1,
                                                            'BLR-DEVICE_1', 'BLR-DEVICE_1',
                                                            '10.12.51.11', 'DEVICE_1')
zabbix_items_from_csv.xml_pretty_me('BLR-DEVICE_1.xml', xml_tree_string_device_1)
#-----------------------
xml_tree_string_device_1 = zabbix_items_from_csv.\
                            generate_items_xml_file_complete(dict_device_1,
                                                            'CHN-DEVICE_1', 'CHN-DEVICE_1',
                                                            '10.12.51.11', 'DEVICE_1')
zabbix_items_from_csv.xml_pretty_me('CHN-DEVICE_1.xml', xml_tree_string_device_1)


#-----------------------
# Read all the lines from the csv file.
#-----------------------
complete_list_dict_device_2 =  zabbix_items_from_csv.reader_csv_file('oid_list_with_range_processed.csv')
complete_list_name_dict_device_2 = zabbix_items_from_csv.read_csv_name_module('oid_names.csv')
dict_device_2 = zabbix_items_from_csv.merge_csv_data(complete_list_dict_device_2, complete_list_name_dict_device_2)
xml_tree_string_device_2 = zabbix_items_from_csv.\
                            generate_items_xml_file_complete(dict_device_2,
                                                             'BLR-DEVICE_2', 'BLR-DEVICE_2',
                                                             '12.12.54.66', 'DEVICE_2')
zabbix_items_from_csv.xml_pretty_me('BLR-DEVICE_2.xml', xml_tree_string_device_2)
#-----------------------
xml_tree_string_device_2 = zabbix_items_from_csv.\
                            generate_items_xml_file_complete(dict_device_2,
                                                             'CHN-DEVICE_2', 'CHN-DEVICE_2',
                                                             '12.12.52.74', 'DEVICE_2')
zabbix_items_from_csv.xml_pretty_me('CHN-DEVICE_2.xml', xml_tree_string_device_2)
```

### Code Location 
Code can be found here : <https://github.com/ahmedzbyr/zabbix_item_from_csv>

