#!/usr/bin/env python

import pika
import time
import argparse

# Parse command line arguments
parser = argparse.ArgumentParser()
parser.add_argument('broker', help='Network or IP address of message broker')
parser.add_argument('logger_id', help='Logger name or ID')
parser.add_argument('log_file', help='Location of log file')
args = parser.parse_args()

# Attemps to connect to server and run data broadcast loop.
# If it fails to connect to the broker, it will wait some time
# and attempt to reconnect infinitely.
while True:
    try:
        connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=args.broker))
        channel = connection.channel()

        channel.exchange_declare(exchange='logs',
                                 type='fanout')

        while True:
            message = (time.ctime()+',%s,200') % (args.logger_id)
            channel.basic_publish(exchange='logs',
                                  routing_key='',
                                  body=message)
            print 'Sent %r' % (message)
            with open(args.log_file, 'a+') as text_file:
                text_file.write(message+'\n')
            time.sleep(1)

        connection.close()
    except:
        print 'No broker found. Retrying in 30 seconds...'
        time.sleep(30)