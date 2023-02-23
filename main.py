from time import sleep
from machine import Pin, PWM
import network
from urequests import get

def led_ramp_up(pwm_leds, duty_step = 1):
    for duty in range(0, 65535, duty_step):
        for pwm_led in pwm_leds:
            pwm_led.duty_u16(duty)
        sleep(0.0005)

def led_ramp_down(pwm_leds, duty_step = 1):
    for duty in range(65535, 0, -duty_step):
        for pwm_led in pwm_leds:
            pwm_led.duty_u16(duty)
        sleep(0.0005)

def led_pulse(pwm_leds, duty_step = 1):
    led_ramp_up(pwm_leds, duty_step)
    led_ramp_down(pwm_leds, duty_step)


def led_on(pwm_led):
    led_current_state = 1 if pwm_led.duty_u16() > 1 else 0
    
    if led_current_state == 1:
        return
    else:
        led_ramp_up([pwm_led])


def led_off(pwm_led):
    led_current_state = 1 if pwm_led.duty_u16() > 1 else 0
    
    if led_current_state == 0:
        return
    else:
        led_ramp_down([pwm_led])


red_led = Pin(12)
pwm_red_led = PWM(red_led)
pwm_red_led.freq(1000)

amber_led = Pin(13)
pwm_amber_led = PWM(amber_led)
pwm_amber_led.freq(1000)

green_led = Pin(14)
pwm_green_led = PWM(green_led)
pwm_green_led.freq(1000)

items = [
    {
        "sensor": "sensor.power_from_grid",
        "led": pwm_red_led
    },
    {
        "sensor": "sensor.battery_discharge",
        "led": pwm_amber_led
    },
    {
        "sensor": "sensor.power_pv_array",
        "led": pwm_green_led
    }
]

# ---

pwm_leds = [
    pwm_red_led,
    pwm_amber_led,
    pwm_green_led
]

# start with all LEDs turned off
for pwm_led in pwm_leds:
    pwm_led.duty_u16(0)

# pulse each LED in turn
for pwm_led in pwm_leds:
    led_pulse([pwm_led], duty_step = 4)

# ramp up all LEDs in turn
for pwm_led in pwm_leds:
    led_ramp_up([pwm_led], 2)

wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.connect('discworld', '12 Wallshead Way')

home_assistant_api_url_base = "http://homeassistant:8123/api/states/"
home_assistant_api_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJkMmFiMDdhODk0Yzc0YTU0YTM4NjU4Mzk2OGFlM2YwYyIsImlhdCI6MTY3NjY3MzM3NCwiZXhwIjoxOTkyMDMzMzc0fQ.IF6H2J2t1EZerY2B380U_s-XE7vNb9yjOgy6r78ikS0"


# ramp down all LEDs in turn
for pwm_led in pwm_leds:
    led_ramp_down([pwm_led], 2)



headers = {
    "Authorization": "Bearer " + home_assistant_api_token,
    "content-type": "application/json",
}

#while True:
for i in range(2):

    for item in items:

        led = item['led']
        sensor = item['sensor']

        response = get(home_assistant_api_url_base + sensor, headers = headers)
        response_dict = response.json()

        print(sensor + ": " + response_dict["state"] + "W")

        # set LED state
        if int(response_dict["state"]) > 0:
            print("LED on")
            led_on(led)
        else:
            print("LED off")
            led_off(led)

        print("\n")

    print("- sleeping 30s -")
    print("\n")
    sleep(30)
