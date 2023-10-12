from machine import Pin, ADC
import network
from time import sleep
import urequests as request

flex_sensor = ADC(Pin(26))
motor = Pin(15, Pin.OUT)

api = "http://sps-api-ce9301a647f2.herokuapp.com"
ssid = "Jason"
password = "88888887"

def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    for _ in range(10):
        print('Waiting for connection...')
        sleep(1)

def get_settings():
    url = api + f"/settings?device_id={1}"
    response = request.get(url)
    json = response.json()
    return json

connect()
settings_file = open("settings.txt", "a")
settings = get_settings()
print(settings)
settings_file.close()

while True:
    flex = flex_sensor.read_u16()
    print(flex)
    if flex > 200:
        motor.on()
    else:
        motor.off()
