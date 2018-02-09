#!/usr/bin/python


import struct
import time
import socket
import logging

try:
    import json
except:
    import simplejson as json



#
# Creating Metric Class to get parameters
#
# HOST name                    ->   self.host   = host
# KEY creating in Zabbix Item  ->   self.key    = key
# VALUE from the XML processed ->   self.value  = value
# CLOCK information
# (if not given then uses
# current server time)         ->   self.clock  = clock
#
# Sample JSON below -> https://www.zabbix.org/wiki/Docs/protocols/zabbix_sender/2.0
#
# {
# "request":"sender data",
# "data":[
#         {
#             "host":"Host name 1",
#             "key":"item_key",
#             "value":"33",
#             "clock":"123123123123"
#         },
#         {
#             "host":"Host name 2",
#             "key":"item_key",
#             "value":"55",
#             "clock":"23423423423"
#         }
#     ]
# }
#
# Metric is taken from the code url below (BSD License)
# url='https://github.com/pistolero/zbxsend'
#
class Metric(object):
    def __init__(self, host, key, value, clock=None):
        self.host = host
        self.key = key
        self.value = value
        self.clock = clock

    def __repr__(self):
        if self.clock is None:
            return 'Metric(%r, %r, %r)' % (self.host, self.key, self.value)
        return 'Metric(%r, %r, %r, %r)' % (self.host, self.key, self.value, self.clock)


#
# Sending data to Zabbix server on port 10051 by default.
# url='https://github.com/pistolero/zbxsend'
#
def send_to_zabbix(metrics, zabbix_host='127.0.0.1', zabbix_port=10051):
    #
    # Send set of metrics to Zabbix server.


    json_dumps = json.dumps
    #
    # Zabbix has very fragile JSON parser, and we cannot use json to dump whole packet

    metrics_data = []
    #
    # Read through the Metrics created above and Process it to create a JSON.
    # Currently we are create a Metrice for each subTree.
    #
    for metric_read in metrics:
        clock = metric_read.clock or time.time()
        metrics_data.append(('\t\t{\n'
                             '\t\t\t"host":%s,\n'
                             '\t\t\t"key":%s,\n'
                             '\t\t\t"value":%s,\n'
                             '\t\t\t"clock":%s}') % (json_dumps(metric_read.host),
                                                     json_dumps(metric_read.key),
                                                     json_dumps(metric_read.value), clock))

    #
    # Creating JSON to be sent to Zabbix server.
    #
    json_data = ('{\n'
                 '\t"request":"sender data",\n'
                 '\t"data":[\n%s]\n'
                 '}') % (',\n'.join(metrics_data))

    logging.debug(json_data)
    #
    # Creating Data Packet to send to Zabbix
    # JSON is prepped up and Packet ready to send.
    #
    data_len = struct.pack('<Q', len(json_data))
    packet = 'ZBXD\1' + data_len + json_data

    try:
        #
        # Creating Socket/Connect to server on 10051 port
        # Send the data and wait for a response.
        # We get a JSON response which can be read for success information
        #
        zabbix = socket.socket()
        zabbix.connect((zabbix_host, zabbix_port))

        # Data send.
        zabbix.sendall(packet)

        # Receive a Response from server.
        response_header = _recv_all(zabbix, 13)

        # Error Checking
        if not response_header.startswith('ZBXD\1') or len(response_header) != 13:
            logger.error('Wrong zabbix response')
            return False

        # Check for reponse
        response_body_length = struct.unpack('<Q', response_header[5:])[0]
        response_body = zabbix.recv(response_body_length)
        zabbix.close()

        # Loading JSON to see the response
        response_from_server = json.loads(response_body)
        logger.debug('Got response from Zabbix: %s' % response_from_server)
        logger.info(response_from_server.get('info'))

        #
        if response_from_server.get('response') != 'success':
            logger.error('Got error from Zabbix: %s', response_from_server)
            return False
        return True

    except:
        logger.exception('Error while sending data to Zabbix')
        return False


logger = logging.getLogger('zbxsender')


def _recv_all(sock, count):
    receive_buffer = ''

    while len(receive_buffer) < count:
        receive_chunk = sock.recv(count - len(receive_buffer))
        if not receive_chunk:
            return receive_buffer
        receive_buffer += receive_chunk

    return receive_buffer



# Process XML and send data to Zabbix Server.
#

if __name__ == '__main__':
    #
    # Zabbix Server information
    # IP and Port
    #
    ZABBIX_SERVER = '127.0.0.1'
    ZABBIX_SERVER_PORT = 10051

    logging.basicConfig(level=logging.DEBUG)
    sender_value = [Metric('localhost', 'SampleTrapperKey', 121),
                    Metric('localhost', 'SampleTrapperKey2', 12135),
                    Metric('localhost', 'SampleTrapperKey3', 1251),
                    Metric('localhost', 'SampleTrapperKey4', 1251)]
    send_to_zabbix(sender_value, ZABBIX_SERVER, ZABBIX_SERVER_PORT)
