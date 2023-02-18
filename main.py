import configparser
# from machine import Pin
import requests
import time
import json

config = configparser.ConfigParser()
config.read("./config.ini")

home_assistant_api_url_base = config['Home Assistant']['api_base_url']
home_assistant_api_token = config['Home Assistant']['api_token']

items = [
    {
        "sensor": config['Home Assistant']['sensor_grid'],
        "colour": "red",
        # "gpio_pin": Pin(18, Pin.OUT)
    },
    {
        "sensor": config['Home Assistant']['sensor_battery'],
        "colour": "amber",
        # "gpio_pin": Pin(19, Pin.OUT)
    },
    {
        "sensor": config['Home Assistant']['sensor_solar'],
        "colour": "green",
        # "gpio_pin": Pin(20, Pin.OUT)
    }
]

# ---

headers = {
    "Authorization": "Bearer " + home_assistant_api_token,
    "content-type": "application/json",
}

while True:

    for item in items:

        response = requests.get(home_assistant_api_url_base + item["sensor"], headers = headers)
        response_dict = json.loads(response.text)

        print(item["sensor"] + ": " + response_dict["state"] + "W")
        
        led_state = "on" if int(response_dict["state"]) > 0 else "off"
        print(item["colour"] + " light : " + led_state)

        # set LED state
        # item["gpio_pin"].value(1 if int(response_dict["state"]) > 0 else 0)

        print("\n")

    print("- sleeping 30s -")
    print("\n")
    time.sleep(30)
