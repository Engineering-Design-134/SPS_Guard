from machine import Pin, ADC
import network
import urequests as request
import uasyncio as asyncio

flex_sensor = ADC(Pin(27))
motor = Pin(14, Pin.OUT)

test_led = Pin("LED", Pin.OUT)
test_led.on()

api = "http://sps-api-ce9301a647f2.herokuapp.com"
ssid = "Jason"
password = "88888887"

connected = False

flex_sensitvitity = 1000 # get local settings

async def get_settings():
    url = api + f"/settings?device_id={1}"

    response = request.get(url)
    json = response.json()
    return json

async def update_settings():
    global connected
    global flex_sensitvitity
    while connected:
        try:
            settings = await get_settings()
            flex_sensitvitity = int(settings["flex_sensitivity"])
        except:
            await asyncio.sleep(5)
            return
        await asyncio.sleep(5)

async def connect():
    global flex_sensitvitity
    global connected
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    while True:
        wlan.connect(ssid, password)
        print('Waiting for connection...')
        await asyncio.sleep(3)
        if wlan.isconnected():
            print('Connected to network')
            connected = True
            await asyncio.create_task(update_settings())
            connected = False


async def work():
    while True:
        flex = flex_sensor.read_u16()
        print(flex)
        if flex > flex_sensitvitity:
            motor.on()
        else:
            motor.off()
        await asyncio.sleep(1)

async def main():
    work_task = asyncio.create_task(work())
    connect_task = asyncio.create_task(connect())
    await asyncio.get_event_loop().run_until_complete(asyncio.gather(work_task, connect_task))


asyncio.run(main())