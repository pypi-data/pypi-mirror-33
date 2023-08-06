toputils
========

Collection of sports betting tools

Included Packages
/////////////////

`toputils.db`: Context manager with inbuilt retry logic wrapped around mysql.connector.
  Uses configuration file for connection parameters and credentials.
`toputils.rmq`: Context manager wrapped around pika blocking publish and blocking consume methods.
  Uses configuration file for connection parameters and credentials.

Installation
////////////

Pipenv.. too easy::

     $ pipenv install toputils


toputils.db
===========

Connection and query boilerplate built around mysql.connector.

If no exceptions are raised inside context manager, connection is
automatically committed upon exiting the context manager. However,
if the connection is to be held open for extended periods, the user can
also commit their own transactions using DataBase.commit().

Connection parameters are fetched from a configuration file and used
to establish the connection. Example .cnf file::

    [test_db]
    user = user-name
    password = password1
    database = my-database
    host = 0.0.0.0
    charset = utf8
    ssl_ca = /dir/to/ca.pem
    ssl_cert = /dir/to/client-cert.pem
    ssl_key = /dir/to/client-key.pem
    ...

There can be multiple sections in the .cnf file enabling DataBase
objects being created for multiple databases within a single application.

Basic Usage
///////////

No dict_cursor::

    >>> from toputils.db import DataBase
    >>> with DataBase("db_top_feed") as dbse:
    ...     cur = dbse.execute("SELECT * FROM tbl_top_events LIMIT 1")
    ...     print(cur.fetchone())
    ...
    (1, 92, 'Match Price Model Example Match', 2, 
     datetime.datetime(2022, 7, 14, 14, 27), 
     datetime.datetime(2022, 7, 14, 14, 27), 0)

With dict_cursor::

    >>> import json
    >>> with DataBase("db_top_feed") as dbse:
    ...     cur = dbse.execute(
                "SELECT event_id, description  FROM tbl_top_events LIMIT 3", 
                dict_cursor=True
            )
    ...     print(json.dumps(cur.fetchall(), sort_keys=True, indent=4))
    ...
    [
        {
            "description": "Match Price Model Example Match",
            "event_id": 1
        },
        {
            "description": "child_comp_1",
            "event_id": 2
        },
        {
            "description": "child_comp_2",
            "event_id": 3
        }
    ]


toputils.rmq
============

Boilerplate for publishing and (soon) consuming off RabbitMQ Queues.

User can create the RMQConn object themselves and be responsible 
for managing the connect() and close() methods however it's preferrable
to use the context manager functionality wherever possible.

All necessary parameters are established in a configuration file. The 
following example lists all possible parameters and the default values 
that pika carries for each. All can be individually set for a connection 
but this is an exhaustive list and much of the time the defaults will do.
The ``[cnf_identifier]`` is the string passed to the RMQConn constructor
which allows it to identify the configuration setup you are using for
the connection. The cnf file can contain multiple sections for 
connections to different queues, each just needs it's own 
``[cnf_identifier]`` header. Uncomment out and change any of the 
following::

    [cnf_identifier]

    ### CONNECTION PARAMETERS ###
    ## see :class:`pika.connection.ConnectionParameters ##
    # host = localhost
    # port = 5672
    # virtual_host = /
    # username = guest
    # password = guest
    # channel_max = 65535
    # frame_max = 131072
    # heartbeat
    # ssl = False
    # connection_attempts = 1
    # retry_delay = 2.0
    # socket_timeout = 0.25
    # locale = en_US
    # backpressure_detection = False
    # blocked_connection_timeout
    # client_properties
    ## these will only be searched if ssl = True
    ## specify path for each
    # keyfile
    # certfile
    # ca_certs

    ### QUEUE PARAMETERS ###
    ## see :meth:`pika.channel.Channel.queue_declare` ##
    # queue =
    # q_passive = False
    # q_durable = False
    # exclusive = False
    # q_auto_delete = False
    # q_nowait = False
    # q_arguments

    ### EXCHANGE PARAMETERS ###
    ## see :meth:`pika.channel.Channel.exchange_declare` ##
    # exchange
    # exchange_type = direct
    # ex_passive = False
    # ex_durable = False
    # ex_auto_delete = False
    # internal = False
    # ex_nowait = False
    # ex_arguments

    ### BIND PARAMETERS ###
    ## see :meth:`pika.channel.Channel.exchange_bind` ##
    # b_nowait = False
    # b_arguments

    ### PUBLISH PARAMETERS ###
    ## see :meth:`pika.channel.Channel.basic_publish` ##
    # routing_key =
    # mandatory = False
    # immediate = False
    
    ### BASIC PROPERTIES PARAMETERS ###
    ## see :class:`pika.spec.BasicProperties` ##
    # content_type
    # content_encoding
    # headers
    # delivery_mode
    # priority


Example Usage::

    >>> from toputils.rmq import RMQConn
    >>> with RMQConn("cnf_identifier") as r:
    ...     r.publish('{"some": "message"}')
