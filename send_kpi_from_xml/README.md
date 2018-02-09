# Send KPI Data to Zabbix from XML KPI File

Send Zabbix metric by reading from a XML file. 
This needs package zbxsend from : https://github.com/ahmedzbyr/zbxsend

1. Install zbxsend
2. Install xmltodict
3. Create items in zabbix using `auto_zabbix_export_generator.py` script.
4. Import items to zabbix.
5. Running the script `zabbix_send_from_kpi_xml.py` to send the data to zabbix server.

## Zabbix Item Creation 
Before we send the Data to Zabbix. We need to create Keys (Items) in Zabbix.
Use the script called `auto_zabbix_export_generator.py`. Script can be found the same location as the sender script.
This script will create a xml file, which can be imported into the zabbix directly.
Below are the usage for the zabbix item xml import generator.

#### To Generate XML Export file for Zabbix from a Properties file.
This properties file can be generated from the sender script `zabbix_send_from_kpi_xml.py` as in the option (1) below.
Once created then we can use this file to create specific KPI `items` import file, for the zabbix server which we want to monitor.

     python ggsn_auto_zabbix_export_generator.py <source_xml_file> [ALL] <host_name> <host_group_name>
     	example: python ggsn_auto_zabbix_export_generator.py KPI_SOURCE_FILE.xml ALL ZABBIX-TMP DEVICE_X1_2

#### Create All KPI Key values from the Zabbix server.
This option is used to create import xml for all KPIs `items` which are present in the kpi xml. 
Which we use to create `items` in the zabbix server. 

     python ggsn_auto_zabbix_export_generator.py <source_xml_file> [FILE] <properties_file_name> <host_name> <host_group_name>
     	example:  python ggsn_auto_zabbix_export_generator.py KPI_SOURCE_FILE.xml FILE KPI_SOURCE_FILE.xml.properties ZABBIX-TMP DEVICE_X1_2
 
**NOTE: `items` key is created based on the `Module`_`SubCategory` from the kpi xml file.**

#### Parameter Information:

     <source_xml_file>      : Is the XML KPI file for Device.
     <properties_file_name> : This is the file which is generated using option (1). '#' is comment in properties file.
     <host_name>            : Host name which needs to be created on zabbix.
     <host_group_name>      : Group name to which host needs to be assigned.
     [ALL]                  : Static value. Use as-is.
     [FILE]                 : Static Value. Use as-is.


## Below is the Usage for Zabbix KPI Sender.

#### 1. To Generate Properties file.
This is to generate a properties file, which can be used to send specific KPIs.
Instead of sending all KPI values. Putting a `#` before the line to comment the line.

    python zabbix_send_from_kpi_xml.py --kpi-xml <source_xml_file> --generate-properties
        example: python zabbix_send_from_kpi_xml.py --kpi-xml KPI_SOURCE_FILE.xml --generate-properties --debug


#### 2. Send all KPI from the xml to server.
Using this option will send all the KPI values from the XML. Most of the time this is better.

    python zabbix_send_from_kpi_xml.py --kpi-xml <source_xml_file> --zabbix-server-ip <zabbix_server_ip> --zabbix-server-port <zabbix_server_port> --host-name <host_name> --all --debug
        example: python zabbix_send_from_kpi_xml.py --kpi-xml KPI_SOURCE_FILE.xml --zabbix-server-ip 127.0.0.1 --zabbix-server-port 10051 --host-name ams-ggsn --all --debug


#### 3. Send KPI from properties file.
Using this option script expects the properties file to be provided, which was create in option (1).

    python zabbix_send_from_kpi_xml.py --kpi-xml <source_xml_file> --zabbix-server-ip <zabbix_server_ip> --zabbix-server-port <zabbix_server_port> --host-name <host_name> --properties-file <properties_file> --debug
        example:  python zabbix_send_from_kpi_xml.py --kpi-xml KPI_SOURCE_FILE.xml --zabbix-server-ip 127.0.0.1 --zabbix-server-port 10051 --host-name ams-ggsn --properties-file KPI_SOURCE_FILE.xml.properties --debug


### Parameter Information

Send Zabbix metric by reading from a XML file. This needs package `zbxsend` from : `https://github.com/ahmedzbyr/zbxsend`.
Install Packages - `pip install zbxsend` and `pip install xmltodict`        
       
    python zabbix_send_from_kpi_xml.py        
       [-h] -x KPI_XML [-i ZABBIX_SERVER_IP] [-s ZABBIX_SERVER_PORT]
       [-n HOST_NAME] [-p PROPERTIES_FILE] [-a] [-g] [-d] [-v]
    
    optional arguments:
      -h, --help            show this help message and exit
      -x KPI_XML, --kpi-xml KPI_XML
                            Is the XML KPI file for Device.
      -i ZABBIX_SERVER_IP, --zabbix-server-ip ZABBIX_SERVER_IP
                            IP address of the Zabbix Server to which this data
                            needs to be sent.
      -s ZABBIX_SERVER_PORT, --zabbix-server-port ZABBIX_SERVER_PORT
                            Port which Zabbix server is listening (Default :
                            10051).
      -n HOST_NAME, --host-name HOST_NAME
                            Host name as given in Zabbix server.
      -p PROPERTIES_FILE, --properties-file PROPERTIES_FILE
                            This is the file which is generated using option (1).
                            '#' is comment in properties file.
      -a, --all             Application Name in the Zabbix Server. (To organize
                            all items being imported)
      -g, --generate-properties
                            Include First line (Header) in the CSV file input,
                            [Default : False]
      -d, --debug           Running Debug mode - More Verbose

### Code location 
Location can be found here : <https://github.com/ahmedzbyr/zabbix-automations/blob/master/send_kpi_from_xml>
