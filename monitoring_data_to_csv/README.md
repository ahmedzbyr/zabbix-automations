## Fetch Monitoring Data from Item to CSV file.

NOTE : Initial script was taken from <http://doc.bonfire-project.eu/R2/monitoring/bonfire_monitoring_data_to_csv.html> 
Location for the Original File : <http://doc.bonfire-project.eu/R2/_static/scripts/fetch_items_to_csv.py>
Have done some minor changes as per my need.

    The research leading to these results has received funding from the
    European Commission's Seventh Framework Programme (FP7/2007-13)
    under grant agreement no 257386.
    
        http://www.bonfire-project.eu/
    Copyright 2012 Yahya Al-Hazmi, TU Berlin
    
    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at
    
        http://www.apache.org/licenses/LICENSE-2.0 
    
    Unless required by applicable law or agreed to in writing, software 
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License this script fetches resource monitoring information from Zabbix-Server
    through Zabbix-API
    
    To run this script you need to install python-argparse "apt-get install python-argparse"

This script gets monitoring data from Items from Zabbix server and creates a CSV file.

For a range of time given. Time range is given in 'yyyy-mm-dd hh:mm:ss' format.
For the range we give start datetime and end datetime, 
if only start datetime is specified then time period will be start datetime to now()

Script can do 2 things:

1. Single key data into csv
2. Multiple keys read from a file and create csv file for each key.


### Single key data into csv
This option will connect to Zabbix and collection a single key monitoring data.
CSV file is created with the key_name.csv format.

    python -s 127.0.0.1 -n host-in-zabbix -u admin -p zabbix -k key-in-zabbix -t1 "2014-10-16 12:00:00" -v 1 

### Multiple keys read from a file.
This option will connect to Zabbix and collection a multiple key monitoring data.
Each key will have its own CSV file. CSV file is created with the key_name.csv format.

    python fetch_monitoring_data_to_csv.py -s 127.0.0.1 -n host-in-zabbix -u admin -p zabbix -f sample_key_file.txt -t1 "2014-10-16 12:00:00" -v 1 
    python fetch_monitoring_data_to_csv.py -s 127.0.0.1 -n host-in-zabbix -u admin -p zabbix -f sample_zabbix_export_file.xml -t1 "2014-10-16 12:00:00" -v 1

### Sample Output CSV File.
CSV file created is in below format.

key|timestamp|value
------|------|------
TestKeyFromZabbix_VS.dlBytes|2014-10-14 12:00:00|0
TestKeyFromZabbix_VS.dlBytes|2014-10-14 12:05:00|0
TestKeyFromZabbix_VS.dlBytes|2014-10-14 12:10:00|0
TestKeyFromZabbix_VS.dlBytes|2014-10-14 12:15:00|3517

Here is a raw output. Rather a semicolon separated values (SSV).

    key;timestamp;value
    TestKeyFromZabbix_VS.dlBytes;2014-10-14 12:00:00;0
    TestKeyFromZabbix_VS.dlBytes;2014-10-14 12:05:00;0
    TestKeyFromZabbix_VS.dlBytes;2014-10-14 12:10:00;0
    TestKeyFromZabbix_VS.dlBytes;2014-10-14 12:15:00;3517
 
 
### Usage 

    usage: fetch_monitoring_data_to_csv.py [-h] -s SERVER_IP -n HOSTNAME
                                           (-k KEY | -f FILE) -u USERNAME -p
                                           PASSWORD [-o OUTPUT] -t1 DATETIME_START
                                           [-t2 DATETIME_END] [-v DEBUG_LEVEL]
    
    Fetch history from aggregator and save it into CSV file
    
    optional arguments:
      -h, --help            show this help message and exit
      -s SERVER_IP, --server-ip SERVER_IP
                            Server IP address
      -n HOSTNAME, --hostname HOSTNAME
                            Hostname of the VM
      -k KEY, --key KEY     Zabbix Item key
      -f FILE, --file FILE  Zabbix Item key File. XML export file from Zabbix.
                            Text file with key in each line.Each Key will create
                            its own csv file.
      -u USERNAME, --username USERNAME
                            Zabbix username
      -p PASSWORD, --password PASSWORD
                            Zabbix password
      -o OUTPUT, --output OUTPUT
                            Output file name, default key_hostname.csv (will
                            remove all special chars).This Option currently works
                            with -k/--key option.
      -t1 DATETIME_START, --datetime-start DATETIME_START
                            Start datetime, 'yyyy-mm-dd HH:MM:SS' use this pattern
                            '2014-10-15 19:12:00" if only t1 specified then time
                            period will be t1 to now()
      -t2 DATETIME_END, --datetime-end DATETIME_END
                            end datetime, "yyyy-mm-dd HH:MM:SS" use this pattern
                            '2014-10-15 19:12:00'
      -v DEBUG_LEVEL, --debug-level DEBUG_LEVEL
                            log level, default 0
    

### Code Usage

#### Multiple keys read from a file.

    from fetch_monitoring_data_to_csv import fetch_multi_key_monitoring_data_to_csv
    
    fetch_multi_key_monitoring_data_to_csv('admin','zabbix', "http://127.0.0.1/zabbix", 'BLR-IN-DEVICE',
                                 'file.txt', '', '2014-10-14 12:00:00', '', 1)
           
                               
### Code Location
Code can be found here : <https://github.com/ahmedzbyr/fetch_monitoring_data_to_csv>
