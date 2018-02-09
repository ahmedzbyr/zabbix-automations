import zabbix_snmp_trap_import_from_csv

# Creating XML tree as a String from CSV file.
xml_tree_gen_as_string = zabbix_snmp_trap_import_from_csv.zabbix_snmp_trap_import_from_csv(
    'export_csv_from_ireasoning_mib_browser.csv', 'GGSN', 'GGSN-GROUP', '127.0.0.1')

# Creating an XML file from xml_tree.
zabbix_snmp_trap_import_from_csv.xml_pretty_me('zabbix_import_file.xml', xml_tree_gen_as_string)