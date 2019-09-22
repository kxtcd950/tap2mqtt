# tap2mqtt
Hue tap poller to publish tap button events to MQTT

## Config file
The JSON config file should contain two dictionaries, "mqtt" and "hue".

The "mqtt" dictionary should contain the items:
* "server" - a string containing the hostname of the MQTT server.  May be an IP address, but in string form.
* "username" - a string containing the username used to connect to the MQTT server
* "password" - a string containing the password used to connect to the MQTT server
* "port" - an integer for the port to connect to the MQTT server.

The "hue" dictionary should contain the items:
* "hub" - a string containing the IP address of the hue hub.
* "username" - the hue API username for the connection to the hub.

## Misc
The poller runs every three seconds.  This is to provide a reasonable responsiveness to users pressing the buttons but also not
overload the hue hub, which will only process one API request per user per second.
One second will occasionally come in under the one second the hub likes; two crashed on me too, three never has.
This shouldn't need to be three seconds, but empirically it must be.
