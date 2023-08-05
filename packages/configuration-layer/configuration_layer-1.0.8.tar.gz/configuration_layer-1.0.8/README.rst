Initial configuration layer for Microservices
=============================================

|image0|

.. code:: json

        _ _          _       _
       | (_)        | |     (_)
     __| |_ ___  ___| | __ _ _ _ __ ___   ___ _ __
    / _` | / __|/ __| |/ _` | | '_ ` _ \ / _ \ '__|
   | (_| | \__ \ (__| | (_| | | | | | | |  __/ |
    \__,_|_|___/\___|_|\__,_|_|_| |_| |_|\___|_|



This service is in his early age. **DO NOT USE in production** or if you
want to, please be aware you are going to use a piece of code which
probably will be changed or improved ( and not necessarily in this
order) soon and very often. You have been warned! This service requires
at least another service listening to a few KAFKA topics.

Service description
===================

This service has been developed to be used as part of a multilayer
microservice based infrastructure. It provides services with a layer of
functionalities to be used in order to request the needed configuration
settings to start a service. It uses KAFKA as messaging platform in
order to exchange messages among services. In order to be used it needs
a service which acts as a **service-registry** that receive a request
and send back a response.

How to add it to your microservice
==================================

\```python from configuration_layer.service_setup.configuration_request
import ConfigurationSeeker from
configuration_layer.utils.configuration_validation import
validate_service_configuration import
configuration_layer.helpers.producer_messages as message import sys, os
import datetime from messaging_middleware.utils.logger import Logger

def check_configuration_directory(): service_configuration_directory =
os.environ.get(‘service_configuration_directory’, ‘configuration’) if
os.path.isdir(service_configuration_directory): return os.getcwd() +
service_configuration_directory else: return False

def seeker_request(**kwargs): seeker =
ConfigurationSeeker(consumer_topic=‘tcsetconf’,
producer_topic=‘tcgetconf’, bootstrap_servers=“your broker here”,
schema_registry=‘your schema registry here’, message={“cmd”: “get_conf”,
“auth”: “ASC”, “service_name”: “myservicename”},
key_schema={“service_name”: “myservicename”},
service_name=‘myservicename’, service_configuration_directory=
os.environ.get(‘service_configuration_directory’, ‘configuration’),
breakable=kwargs.get(‘breakable’, 1), set=kwargs.get(‘set’, 0) )
seeker.start() seeker.join()

if **name** == “**main**”: if not check_configuration_directory():
sys.exit(

.. |image0| image:: http://www.italiamappe.it/mappa/ImmaginiVetrine/0000106274/Immagine1lrg.jpg