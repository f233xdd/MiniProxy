# Client

* This is the client part.

## Usage

* Run **GUI.pyw** or **host.py**( _guest.py_ ) in order to get started.
* [ Optional ] Install **cryptography** to enable encrypting function.

## HOW-TO( client\config.json )

* `data_max_length( int )` It's the room of one packet which is sent.
* `internet_ip( str )` It's the Internet IP of your server.
* `port( int )` It's the port you'll connect with your server.
* `virtual_server_port( int )` The program opens this port on your local net to allow your program connect with it.
* `open_port( int )` The program connect this port with your local program.
* `crypt( bool )` Data will be encrypted if it's true

### Tips

* `server_address` only includes the **Internet IP** address of your server.
* Please check the config before you start.
