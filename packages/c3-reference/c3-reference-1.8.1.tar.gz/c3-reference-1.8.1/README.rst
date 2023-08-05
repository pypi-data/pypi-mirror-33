Fake Listener and Auth Server Reference Implementation
======================================================

Requirements
------------

1. Python >= 3.5 (new asyncio syntax)
2. PyCryptodome
3. aiokafka

Installation
------------
::

   pip install c3-reference

Running the Listener Simulation / Traffic Generator
---------------------------------------------------

Start listener with 1 beacon, send reports to UDP 127.0.0.1:9999 :

::

      listener

Listener simulating 500 beacons, send reports to google.com:35309 :

::

      listener -nb 500 --server google.com --port 35309


Running the reference Authentication Server
-------------------------------------------

::

      authserver

The auth server listens on 0.0.0.0:9999 and decodes and verifies any
rx'd packets from the listener simulation *or* real listeners.

Running the reference Authentication Server (Advanced)
------------------------------------------------------

::

      authserver -l 192.168.8.1 -p 9876 --master-key 000102030405060708090a0b0c0d0e0f

Start the authserver listening on 192.168.8.1:9876 and decodes and
verifies any rx'd packets using beacon keys derived from the given
master key (default testing key is c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3c3).

Running the Kafka producer
--------------------------

::

      kafka

The producer will listens on 0.0.0.0:9999 and decode and verify any
rx'd packets from the listener simulation *or* real listeners; the
data is then serialized via json and sent to the topic 'beacons' using
the bootstrap_server 127.0.0.1:9092

Running the Kafka producer (Advanced)
------------------------------------------------------

::

      kafka -l 192.168.8.1 -p 9876 -s 192.168.99.1 -q 9920 -t my-topic --master-key 000102030405060708090a0b0c0d0e0f

Listen on 192.168.8.1:9999 for listener traffic, then derive beacon
keys from the given master key, decode then forward to topic
'my-topic' on Kafka bootstraped by 192.168.99.1:9920
