from machine import Pin, ADC, PWM
import network
import urequests as request
import uasyncio as asyncio

flex_sensor = ADC(Pin(27))
motor = PWM(Pin(15, Pin.OUT))

motor.freq(1000)
PWM_DUTY_OFF = 0
PWM_DUTY_LOW = 16256
PWM_DUTY_MED = 48,767
PWM_DUTY_HIGH = 65025

test_led = Pin("LED", Pin.OUT)
test_led.on()

API = "http://sps-api-ce9301a647f2.herokuapp.com"
SSID = "Jason"
PASSWORD = "88888887"
DEVICE_ID = 1

connected = False

flex_sensitvitity = 1000 # get local settings
vibration_duration = 1000
vibration_strength = 1 # 0|1|2

async def get_settings():
    url = API + f"/settings?device_id={DEVICE_ID}"

    response = request.get(url)
    json = response.json()
    return json

async def update_settings():
    global connected
    global flex_sensitvitity
    global vibration_duration
    while connected:
        try:
            settings = await get_settings()
            flex_sensitvitity = int(settings["flex_sensitivity"])
            vibration_duration = int(settings["vibration_duration"])
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
        wlan.connect(SSID, PASSWORD)
        print('Waiting for connection...')
        await asyncio.sleep(3)
        if wlan.isconnected():
            print('Connected to network')
            connected = True
            await asyncio.create_task(update_settings())
            connected = False

async def work():
    global motor
    global vibration_strength
    while True:
        flex = flex_sensor.read_u16()
        print(flex)
        if flex > flex_sensitvitity:
            match vibration_strength:
                case 0:
                    motor.duty_u16(PWM_DUTY_LOW)
                case 1:
                    motor.duty_u16(PWM_DUTY_MED)
                case 2:
                    motor.duty_u16(PWM_DUTY_HIGH)
            await asyncio.sleep_ms(vibration_duration)
            motor.duty_u16(PWM_DUTY_OFF)
        else:
            motor.duty_u16(PWM_DUTY_OFF)
        await asyncio.sleep(1)

async def main():
    work_task = asyncio.create_task(work())
    connect_task = asyncio.create_task(connect())
    await asyncio.get_event_loop().run_until_complete(asyncio.gather(work_task, connect_task))


asyncio.run(main())