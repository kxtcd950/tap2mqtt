#!/usr/bin/python3
""" Hue tap to mqtt poller.
On events from the polled hue taps, publish the events into the configured MQTT instance.
"""
import json
import pprint
from time import sleep
import requests
import paho.mqtt.client as mqtt

CONFIG_FILENAME = "tap2mqtt.json"

SWITCHMODEL = "ZGPSWITCH"
BUTTONNAMES = {"34": "Face", "16": "Two", "17": "Three", "18": "Four", "0": "None"}

# The callback for the CONNACK from the mqtt server
def cb_on_connect(client, userdata, flags, result):
    """callback from paho"""
    print("Connected to MQTT server OK")
    #client.subscribe("#")

def cb_on_message(client, userdata, msg):
    """ callback from paho """
    print(msg.topic+" "+str(msg.payload))

def read_config(conf_file):
    """ read config from json settings. """
    with open(conf_file) as json_file:
        the_json = json.load(json_file)
    return the_json

def connect_to_mqtt(config, client):
    """ connects to mqtt, mutates client parameter """
    client.on_connect = cb_on_connect
    client.on_message = cb_on_message
    client.username_pw_set(config["username"], config["password"])
    client.connect(config["server"], config["port"], 60)
    client.loop_start()

def setup_hue(tap, huetaps, pretty_printer):
    """ setup hue objects and return the current state of the taps. """
    for obj in tap.values():
        if obj["modelid"] == SWITCHMODEL:
            pretty_printer.pprint(obj)
            print("Got a Hue tap ("+str(obj["name"])+")")
            curstate = obj["state"]
            print("ID: "+str(obj["uniqueid"])+"\n")
            print("Button state:\n")
            print(" * Button: "+BUTTONNAMES[str(curstate["buttonevent"])])
            print(" * updated: "+str(curstate["lastupdated"])+"\n")
            huetaps[obj["uniqueid"]] = {"button": curstate["buttonevent"],
                                        "updated": curstate["lastupdated"],
                                        "name": obj["name"]}
    return curstate

def process_values(tap, curstate, huetaps, client):
    """ Having got the tap values from Hue, process them """
    for obj in tap.values():
        if obj["modelid"] == SWITCHMODEL:
            curstate = obj["state"]
            if obj["uniqueid"] in huetaps:   # Updating (?) an old tap we've seen before.
                if curstate["lastupdated"] != huetaps[obj["uniqueid"]]["updated"]:
                    print("New button "+str(curstate["buttonevent"])+
                          " pressed on tap "+huetaps[obj["uniqueid"]]["name"]+
                          " "+curstate["lastupdated"])
                    # New button press!
                    huetaps[obj["uniqueid"]]["updated"] = curstate["lastupdated"]
                    if curstate["buttonevent"] == "null":
                        buttonevent = "None"
                    else:
                        buttonevent = str(curstate["buttonevent"])
                    huetaps[obj["uniqueid"]]["button"] = buttonevent
                    if curstate["buttonevent"] != "null":
                        buttonfriendly = BUTTONNAMES[str(curstate["buttonevent"])]
                    else:
                        buttonfriendly = "None"
                    client.publish("huepoller/tap/"+obj["name"]+"/"+buttonfriendly, "pressed")
            else:
                # Insert a new tap which has just come online.
                huetaps[obj["uniqueid"]] = {"button": curstate["buttonevent"],
                                            "updated": curstate["lastupdated"],
                                            "name": obj["name"]}

def main():
    """ It's main. """
    pretty_printer = pprint.PrettyPrinter(indent=4)

    config = read_config(CONFIG_FILENAME)

    client = mqtt.Client()
    connect_to_mqtt(config["mqtt"], client)

    tap = json.loads(requests.get('http://'+config["hue"]["hub"]+
                                  '/api/'+config["hue"]["username"]+'/sensors').text)

    print("\n")

    huetaps = {}
    cur_state = setup_hue(tap, huetaps, pretty_printer)


    # huetaps now contains all the hue taps which are connected to the Hue Hub we interrogated.
    # From here, we just need to keep polling the Hue hub for taps, and keep comparing against
    # the held state of that tap.  When the time of the last buttonpress changes, we know that
    # someone has done something to the tap in question.
    # At this point, we publish to the mqtt broker a new event and let everyone else sort out
    # what they're going to do as a result.

    while 1:
        respvalid = 0
        while respvalid == 0:
            sleep(3)
            try:
                response = requests.get('http://'+config["hue"]["hub"]+'/api/'+
                                        config["hue"]["username"]+'/sensors').text
                tap = json.loads(response)
                respvalid = 1
            except ValueError:
                print("Got invalid response from hub (doesn't appear to be JSON): "+response)
                respvalid = 0
                continue
            except ConnectionResetError:
                print("Hue Hub reset the connection.  Capricious thing.")
                respvalid = 0
                continue
            except ConnectionError:
                print("Too many connections to Hue hub - connection refused")
                respvalid = 0
                continue
            except:
                print("An unknown exception ocurred.  Retrying.")
                respvalid = 0
                continue

        process_values(tap, cur_state, huetaps, client)

main()
