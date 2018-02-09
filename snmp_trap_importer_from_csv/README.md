## Zabbix Import File from iReasoning Export CSV.
Module used to generate Zabbix import xml for snmp traps
Below are steps to create a Zabbix Import for Traps. 
These traps are captured from the `snmptrap` function in Zabbix.


###Step 1:
Select the Alarms from the iReasoning MIB browser and Export them as CSV. 
This Script expect MIB information to be in CSV format.
Export from a iReasoning Browser will generate CSV as below.

    "Name","Full Name","OID","Type","Access","Indexes","MIB Module","Description"

We use this information to create snmptrap items and corresponding Trigger in the XML.
Which can be imported directly.


###Step 2: 
Below are the details to create the xml file from the CSV create above.

    python zabbix_snmp_trap_import_from_csv.py <export_csv> <host_name> <host_group_name> <host_interface_name>
    
    example: python zabbix_snmp_trap_import_from_csv.py \
                -e export_csv_from_ireasoning_mib_browser.csv \ 
                -n GGSN-1-LONDON -g GGSN-GROUP -i 127.0.0.1
    
    usage: zabbix_snmp_trap_import_from_csv.py [-h] -e EXPORT_CSV -n HOST_NAME -g HOST_GROUP -i HOST_INTERFACE
    
Select the Alarms from the iReasoning MIB browser and Export them as CSV. This
Script expect MIB information to be in CSV format. Export from a iReasoning
Browser will generate CSV as below.     

    "Name","Full Name","OID","Type","Access","Indexes","MIB Module","Description".

We use this information to create snmptrap items and corresponding Trigger in the XML.
Which can be imported directly.
    
    optional arguments:
      -h, --help            show this help message and exit
      -e EXPORT_CSV, --export-csv EXPORT_CSV
                            OID file, Gives all OIDs on the device
      -n HOST_NAME, --host-name HOST_NAME
                            Host name as given in Zabbix server.
      -g HOST_GROUP, --host-group HOST_GROUP
                            Host Group which the host belongs to, as in Zabbix
                            server.
      -i HOST_INTERFACE, --host-interface HOST_INTERFACE
                            SNMP Interface configured on Zabbix server. (Assuming
                            Single Interface in Configured)


### Code location 
Location can be found here : <https://github.com/ahmedzbyr/zabbix_snmp_trap_import_from_csv>
