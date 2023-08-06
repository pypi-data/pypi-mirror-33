#!/bin/env python
"""Reference Implementation of v1 C3 Security Beacon Auth Server."""
# import argparse
# import asyncio
# import os
# import pprint
# import signal

# from .beacon import set_master_key
# from .protocol import SecBeaconProtocol

# parser = argparse.ArgumentParser(
#     description='Start a debug authserver that prints decoded packets')
# parser.add_argument('--listen-address', '-l', default="127.0.0.1",
#                     help="Address on which to listen")
# parser.add_argument('--port', '-p', type=int, default=9999,
#                     help="Port as which to listen")
# parser.add_argument('--master-key', '-key', default=('c3' * 16),
#                     help="Key from which to derive beacon keys")
#
# args = parser.parse_args()

# pp = pprint.PrettyPrinter(indent=4)
#
#
# async def printing_callback(proto, msg_dict):
#     pp.pprint(msg_dict)
#
#
# class SecBeaconProtoCallback(SecBeaconProtocol):
#     callback = printing_callback
#
#
# def start_server(loop):
#     return loop.create_server(SecBeaconProtoCallback,
#                               host=args.listen_address, port=args.port)
#
#
# def main() -> None:
#     set_master_key(args.master_key)
#     loop = asyncio.get_event_loop()
#     if signal is not None and os.name != 'nt':
#         loop.add_signal_handler(signal.SIGINT, loop.stop)
#
#     server = loop.run_until_complete(start_server(loop))
#     print("Listening on {}:{}".format(args.listen_address, args.port))
#     loop.run_forever()
#     server.close()
#     loop.close()
#
#
# if __name__ == '__main__':
#     main()
