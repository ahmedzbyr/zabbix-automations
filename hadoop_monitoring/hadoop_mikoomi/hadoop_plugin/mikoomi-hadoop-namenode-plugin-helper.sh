#!/usr/bin/sh

#--------------------------------------------------------------------------------------------
# Expecting the following arguments in order -
# <ignore_value> = this is a parameter that is inserted by Zabbix
#                  It represents hostname/ip address entered in the host configuration.
# host = hostname/ip-address of Hadoop cluster NameNode server.
#        This is made available as a macro in host configuration.
# port = Port # on which the NameNode metrics are available (default = 50070)
#        This is made available as a macro in host configuration.
# zabbix_name = Name by which the Hadoop NameNode is configured in Zabbix.
#        This is made available as a macro in host configuration.
#--------------------------------------------------------------------------------------------

COMMAND_LINE="$0 $*" 
export SCRIPT_NAME="$0"

#--------------------------------------------------------------------------------------------
# Ignore the first parameter - which is ALWAYS inserted implicitly by Zabbix
#--------------------------------------------------------------------------------------------
shift ;

usage() {
   echo "Usage: $SCRIPT_NAME <discarded_value> <host> <port> <name_in_zabbix>"
}

if [ $# -ne 3 ]
then
    usage ;
    exit ;
fi


#--------------------------------------------------------------------------------------------
# First 2 parameters are required for connecting to Hadoop NameNode
# The 3th parameter HADOOP_NAME_IN_ZABBIX is required to be sent back to Zabbix to identify the 
# Zabbix host/entity for which these metrics are destined.
#--------------------------------------------------------------------------------------------
export CLUSTER_HOST=$1
export METRICS_PORT=$2
export HADOOP_NAME_IN_ZABBIX=$3

#--------------------------------------------------------------------------------------------
# Set the data output file and the log fle from zabbix_sender
#--------------------------------------------------------------------------------------------
export RAW_FILE="/tmp/${HADOOP_NAME_IN_ZABBIX}.raw"
export DATA_FILE="/tmp/${HADOOP_NAME_IN_ZABBIX}.txt"
export LOG_FILE="/tmp/${HADOOP_NAME_IN_ZABBIX}.log"


#--------------------------------------------------------------------------------------------
# Use curl to get the metrics data from Hadoop NameNode and use screen-scraping to extract
# metrics. 
# The final result of screen scraping is a file containing data in the following format -
# <HADOOP_NAME_IN_ZABBIX> <METRIC_NAME> <METRIC_VALUE>
#--------------------------------------------------------------------------------------------

python zabbix_hadoop_nn_mikoomi.py $CLUSTER_HOST $METRICS_PORT $DATA_FILE $HADOOP_NAME_IN_ZABBIX

#--------------------------------------------------------------------------------------------
# Perform a ping check of the host. Having this item/check makes it easy to debug issues.
#--------------------------------------------------------------------------------------------
ping -w 1 -W 1 -c 1 $CLUSTER_HOST 2>/dev/null 1>/dev/null
if [ $? -gt 0 ]
then
   echo "$HADOOP_NAME_IN_ZABBIX ping_check FAILED"
else
   echo "$HADOOP_NAME_IN_ZABBIX ping_check PASSED"
fi >> $DATA_FILE


#--------------------------------------------------------------------------------------------
# Check the size of $DATA_FILE. If it is not empty, use zabbix_sender to send data to Zabbix.
#--------------------------------------------------------------------------------------------
if [[ -s $DATA_FILE ]]
then
   zabbix_sender -vv -z 127.0.0.1 -i $DATA_FILE 2>>$LOG_FILE 1>>$LOG_FILE
   echo  -e "Successfully executed $COMMAND_LINE" >>$LOG_FILE
else
   echo "Error in executing $COMMAND_LINE" >> $LOG_FILE
fi
