# Server

* This is the server part.
* You can simply run **_main.py_** in order to get started.

### HOW-TO(config.json)

* `data_max_length( int )` It decides how much a packet will be sent.
* `private_ip( str )` It's the Intranet IP of your server.
* `ports( list[int, int] )` It decides which ports you'll open for connections.
* `file_log( bool )` What is printed on the console will be kept in a file called ServerLog.log except exceptions.

#### Tips:

* `local_address` only includes the **Intranet IP** address of your server.
* Please check the config before you start.