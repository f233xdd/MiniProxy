# Client

* This is the client part.
* You can simply run **_host_main.py_** or **_visitor_main.py_** in order to get started.

### HOW-TO(config.json)

* `data_max_length( int )` It's the room of one packet which is sent.
* `internet_ip( str )` It's the internet ip of your server.
* `port( int )` It's the port you'll connect with your server.
* `virtual_server_port( int )` The program opens this port on your local net to let Minecraft connect with it.
* `debug( bool )` Data will be printed on the terminal if this is true.

#### Tips:

* Host client only reads the config in "host".
* Visitor client only reads the config in "visitor".
* `server_address` only includes the **Internet IP** address of your server.
* Please check the config before you start.