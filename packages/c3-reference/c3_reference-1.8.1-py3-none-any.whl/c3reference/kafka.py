# #!/bin/env python
# import argparse
# import asyncio
# import json
# import os
# import signal
#
# from aiokafka import AIOKafkaProducer
#
# from .protocol import SecBeaconProtocol
# from .beacon import set_master_key
#
# # Config
# topic = 'beacons'
#
# parser = argparse.ArgumentParser(
#     description='Start a Kafka producer that forwards decoded beacon packets')
# parser.add_argument('--listen-address', '-l', default="127.0.0.1",
#                     help="Address on which to listen")
# parser.add_argument('--topic', '-t', default="beacons",
#                     help="Destination topic")
# parser.add_argument('--listen-port', '-p', type=int, default=9999,
#                     help="Port as which to listen")
# parser.add_argument('--server', '-s', default="127.0.0.1",
#                     help="Address of kafka bootstrap server")
# parser.add_argument('--server-port', '-q', type=int, default=9092,
#                     help="Kafka Server Port")
# parser.add_argument('--master-key', '-key', default=('c3' * 16),
#                     help="Key from which to derive beacon keys")
#
# args = parser.parse_args()
# loop = asyncio.get_event_loop()
# producer = AIOKafkaProducer(
#     loop=loop,
#     bootstrap_servers=':'.join([args.server, str(args.server_port)]))
#
#
# async def kafka_produce(proto, beacon_dict):
#     print(beacon_dict)
#     await producer.send(args.topic, json.dumps(beacon_dict).encode('ascii'))
#
#
# class SecBeaconProtoCallback(SecBeaconProtocol):
#     callback = kafka_produce
#
#
# def start_server(loop):
#     return loop.create_server(
#         SecBeaconProtoCallback, host=args.listen_address,
#         port=args.listen_port)
#
#
# def main():
#     loop.run_until_complete(producer.start())
#
#     set_master_key(args.master_key)
#
#     if signal is not None and os.name != 'nt':
#         loop.add_signal_handler(signal.SIGINT, loop.stop)
#
#     server = loop.run_until_complete(start_server(loop))
#     print("Listening on {}:{}".format(args.listen_address, args.listen_port))
#     loop.run_forever()
#     loop.run_until_complete(producer.stop())
#     server.close()
#     loop.close()
