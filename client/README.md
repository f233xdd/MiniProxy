# Client

* This is the client part.
* You should only run **_host_main.py_** or **_visitor_main.py_** in order to get started.

### HOW-TO(config.json)

* **data_max_length**( int ) decides how much a packet will be sent.
* **server_address**( str ) decides which server you'll connect with.
* **virtual_server_port**( int ) decides which port will be open to a visitor's Minecraft.
* **debug**( bool ) decides whether the data will be printed on the terminal.

#### Tips:

* Host client only reads the config in "host".
* Visitor client only reads the config in "visitor".
* server_address includes both a server internet ip and a server open port, such as: 127.0.0.1:25565.
* please check the config before you start.