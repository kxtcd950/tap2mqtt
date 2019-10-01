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

Example:

```json
{
  "mqtt": {
    "server": "localhost",
    "username": "user",
    "password": "pass",
    "port": 1883
  },
  "hue": {
    "hub": "192.168.0.33",
    "username": "hue-hub-api-user"
  }
}
```

## Misc
The poller runs every three seconds.  This is to provide a reasonable responsiveness to users pressing the buttons but also not
overload the hue hub, which will only process one API request per user per second.
One second will occasionally come in under the one second the hub likes; two crashed on me too, three never has.
This shouldn't need to be three seconds, but empirically it must be.

## Setup
Setting up the taps with Hue is remarkably difficult; the tap devices must be setup in the Hue application and paired with the
hub, but must have absolutely no actions assigned to the buttons.  With any Hue specific configuration assigned to the tap,
the hub will not return any data to this script.
Other than this, it's plain sailing.
