#summary Chapter 5: Apache Hadoop Plugin

=Apache Hadoop Plugin=

NOTE : THIS IS ORIGINALLY FROM MIKOOMI TEMPLATES : https://code.google.com/p/mikoomi/ .
I HAVE ADDED A PYTHON SCRIPT TO GET THE VALUES FROM JMX, RATHER THAN FROM PARSING THE HTML WHICH WAS DONE ORIGINALLY. 
FOLLOW THE WIKI ON MIKOOMI ITS CLEARER : https://code.google.com/p/mikoomi/wiki/05

PS : ONLY DIFFERENCE IN SETUP IS THAT YOU NEED TO INCLUDE THE `zabbix_hadoop_nn_mikoomi.py` SCRIPT WHEREEVER YOU PUT THE SHELL SCRIPTS.

==Overview==

The *Apache Hadoop Plugin* can be used to monitor Namenode and Jobtracker of a Hadoop Cluster. [http://hadoop.apache.org Hadoop] is the leading and defacto distributed big data processing system "out there". While it is used by companies like Yahoo (who supposedly have the largest Hadoop cluster), Facebook, Groupon to name a few, there seems to be only two monitoring solution out there - [http://wiki.apache.org/hadoop/GangliaMetrics Ganglia] and [http://opentsdb.net/ openTSDB]. As you read the documentation, you will realize that the two monitoring solutions are very tightly coupled to Hadoop and are very sensitive about its version, libraries, etc.

The Apache Hadoop plugin has been designed to be loosely coupled and does not require installing any software on the Hadoop cluster or the Zabbix server. Sounds too good to be true? Why don't you continue reading below......

==Setup and Configuration==

The Apache Hadoop Plugin uses screen-scraping of the Hadoop NameNode and JobTracker Web UI interfaces. There is no need to add or change any Hadoop configuration parameters or restart your Hadoop cluster. You can be up and running in as little as 5 minutes after downloading the plugin.

The plugin makes use of a command tool called curl which needs to be installed. On the Zabbix appliance, you can do this by logging in as root (default password = zabbix) running the command *`yast -i curl`*. Note that yast will first update its package repository and this takes a couple of minutes, but the curl package itself it is quite small.

Next download the Apache Hadoop Plugin which consists of 2 shell scripts and 2 template xml files from http://mikoomi.googlecode.com/svn/plugins/. Create a directory *`/etc/zabbix/externalscripts`* on the Zabbix appliance and copy the shell scripts to this directory.  

Next open up a browser and download the NameNode and JobTracker Zabbix template files from http://mikoomi.googlecode.com/svn/plugins/.
Open up another browser window or tab and login to the Zabbix frontend (user = admin, password = zabbix).

Navigate as follows: 

  * Configuration >> Templates
  * Click on the "Import Template" button on the top right-hand corner
  * In the "Import file" dialog box, browse/search/enter the filename of the Zabbix template that was downloaded
  * Upload the template

*_Now you are ready to start monitoring your Hadoop cluster as described below.

==Monitoring Your Hadoop Cluster==
 
Follow these steps to start monitoring:

*Monitoring the NameNode* 

  * login to the Zabbix front-end and navigate to *_Configuration >> Hosts_*
  * Click on *_Create Host_* button on the top right-hand corner. 
  * Fill in the details - where Name = your choice of name (every monitored entity in Zabbix is referred to as as a host - but it can be host, a  service, a program, or even a cluster)
  * Next click on the *_Add_* button in the *_Linked templates_* section of the screen.
  * You will see a list of templates - select the NameNode template *_Template_Hadoop_NameNode_*

In the Macros section, add the following macros -

  * *{$HADOOP_NAMENODE_HOST}*
  * *{$HADOOP_NAMENODE_METRICS_PORT}*
  * *{$ZABBIX_NAME}*


The value for {$HADOOP_NAMENODE_HOST} should be the hostname/full-qualified hostname for the Namenode (as "pingable" on your network). The value for {$HADOOP_NAMENODE_METRICS_PORT} is the port for the Web UI Admin screen for the NameNode. And finally {$ZABBIX_NAME} is the name given to this monitored NameNode entity in Zabbix earlier.


Similarly, setup the monitoring of the JobTracker as follows -

*Monitoring the JobTracker* 

  * login to the Zabbix front-end and navigate to *_Configuration >> Hosts_*
  * Click on *_Create Host_* button on the top right-hand corner. 
  * Fill in the details - where Name = your choice of name (every monitored entity in Zabbix is referred to as as a host - but it can be host, a  service, a program, or even a cluster)
  * Next click on the *_Add_* button in the *_Linked templates_* section of the screen.
  * You will see a list of templates - select the JobTracker template *_Template_Hadoop_JobTracker_*

In the Macros section, add the following macros -

  * *{$HADOOP_JOBTRACKER_HOST}*
  * *{$HADOOP_JOBTRACKER_METRICS_PORT}*
  * *{$ZABBIX_NAME}*


The value for {$HADOOP_JOBTRACKER_HOST} should be the hostname/full-qualified hostname for the JobTracker  (as "pingable" on your network). The value for {$HADOOP_JOBTRACKER_METRICS_PORT} is the port for the Web UI Admin screen for the JobTracker. And finally {$ZABBIX_NAME} is the name given to this monitored JobTracker Zabbix entity earlier.


==Monitored NameNode Metrics==

  * Configured Cluster Storage
  * Configured Max. Heap Size (GB)
  * Hadoop Version
  * NameNode Process Heap Size (GB)
  * NameNode Start Time
  * Number of Dead Nodes
  * Number of Decommissioned Nodes
  * Number of Files and Directories in HDFS
  * Number of HDFS Blocks Used
  * Number of Live Nodes
  * Number of Under-Replicated Blocks
  * Ping Check
  * Storage Unit
  * Total % of Storage Available
  * Total % of Storage Used
  * Total Storage Available
  * Total Storage Used by DFS
  * Total Storage Used by non-DFS
  * Least (min) Node-level non-DFS Storage Used
  * Least (min) Node-level Storage Configured
  * Least (min) Node-level Storage Free
  * Least (min) Node-level Storage Free %
  * Least (min) Node-level Storage Used
  * Least (min) Node-level Storage Used %
  * Most (max) Node-level non-DFS Storage Used
  * Most (max) Node-level Storage Configured
  * Most (max) Node-level Storage Free
  * Most (max) Node-level Storage Free %
  * Most (max) Node-level Storage Used
  * Most (max) Node-level Storage Used %
  * Node-level Storage Unit of Measure
  * Node with Least (min) Node-level non-DFS Storage Used
  * Node with Least (min) Node-level Storage Configured
  * Node with Least (min) Node-level Storage Free
  * Node with Least (min) Node-level Storage Free %
  * Node with Least (min) Node-level Storage Used
  * Node with Least (min) Node-level Storage Used %
  * Node with Most (max) Node-level non-DFS Storage Used
  * Node with Most (max) Node-level Storage Configured
  * Node with Most (max) Node-level Storage Free
  * Node with Most (max) Node-level Storage Free %
  * Node with Most (max) Node-level Storage Used
  * Node with Most (max) Node-level Storage Used %


==Monitored Jobtracker Metrics==

  * Average Task Capacity Per Node
  * Hadoop Version
  * JobTracker Start Time
  * JobTracker State
  * Map Task Capacity
  * Number of Blacklisted Nodes
  * Number of Excluded Nodes
  * Number of Jobs Completed
  * Number of Jobs Failed
  * Number of Jobs Retired
  * Number of Jobs Running
  * Number of Jobs Submitted
  * Number of Map Tasks Running
  * Number of Nodes in Hadoop Cluster
  * Number of Reduce Tasks Running
  * Occupied Map Slots
  * Occupied Reduce Slots
  * Reduce Task Capacity
  * Reserved Map Slots
  * Reserved Reduce Slots


==Pre-canned NameNode Triggers==

  * Less than 20% free space available on the cluster
  * NameNode was restarted
  * No monitoring data received for the last 10 minutes
  * One or more nodes have become alive or restarted
  * One or more nodes have become dead
  * One or more nodes have been added to the decommissioned list
  * One or more nodes have been removed from the decommissioned list
  * The number of live nodes has been reduced
  * The number of live nodes has increased
  * There has been a reduction in the number of under-replicated blocks
  * There has been an increase in the number of under-replicated blocks
  * Less than 20% free space available on one or more nodes in the cluster


==Pre-canned JobTracker Triggers==

  * No monitoring data received for the last 10 minutes
  * One or more jobs have failed
  * One or more nodes have become blacklisted
  * One or more nodes have been added to the exclude list
  * One or more nodes have been added to the Hadoop cluster
  * One or more nodes have been removed from the blacklisted nodes
  * One or more nodes have been removed from the exclude list
  * One or more nodes have been removed from the Hadoop cluster
  * The JobTracker was restarted
