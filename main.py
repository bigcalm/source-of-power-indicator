from time import sleep
from machine import Pin, PWM
from network import WLAN, STA_IF
from urequests import get

from config import config

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
        "sensor": config['sensors']['grid'],
        "led": pwm_red_led
    },
    {
        "sensor": config['sensors']['battery'],
        "led": pwm_amber_led
    },
    {
        "sensor": config['sensors']['solar'],
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


# connect to the wifi network
wlan = WLAN(STA_IF)
wlan.active(True)
wlan.connect(config['wifi']['ssid'], config['wifi']['password'])


# ramp down all LEDs in turn
for pwm_led in pwm_leds:
    led_ramp_down([pwm_led], 2)



headers = {
    "Authorization": "Bearer " + config['api']['token'],
    "content-type": "application/json",
}

while True:

    for item in items:

        led = item['led']
        sensor = item['sensor']

        response = get(config['api']['base_url'] + sensor, headers = headers)
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

