from machine import Pin, ADC, PWM
import network
from time import sleep
import urequests as request
import uasyncio as asyncio

flex_sensor = ADC(Pin(27))
motor = PWM(Pin(14))

motor.freq(1000)
PWM_DUTY_OFF = 0
PWM_DUTY_LOW = 50767
PWM_DUTY_MED = 58767
PWM_DUTY_HIGH = 65025

test_led = PWM(Pin(13))
test_led.duty_u16(PWM_DUTY_OFF)

API = "http://sps-api-ce9301a647f2.herokuapp.com"
SSID = "Jason"
PASSWORD = "88888887"
DEVICE_ID = 1

connected = False

flex_sensitvitity = 1000 # get local settings
vibration_duration = 1000
vibration_strength = 2 # 0|1|2

async def get_settings():
    url = API + f"/settings?device_id={DEVICE_ID}"

    response = request.get(url)
    json = response.json()
    return json

async def update_settings(wlan):
    global connected
    global flex_sensitvitity
    global vibration_duration
    global vibration_strength
    if wlan.isconnected() == False:
        return
    while connected:
        try:
            settings = await get_settings()
            print(settings)
            flex_sensitvitity = int(settings["flex_sensitivity"])
            vibration_strength = int(settings["vibration_strength"])
            vibration_duration = int(settings["vibration_duration"])
        except:
            return
        await asyncio.sleep(3)

async def connect():
    global flex_sensitvitity
    global connected
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(SSID, PASSWORD)
    print('Waiting for connection...')
    await asyncio.sleep(5)
    while True:
        # 10 tries before retrying
        for _ in range(10):
            print("Waiting for connection...")
            await asyncio.sleep(2)
            if wlan.isconnected():
                print('Connected to network')
                connected = True
                await asyncio.create_task(update_settings(wlan))
                connected = False
        wlan.connect(SSID, PASSWORD)
        

async def work():
    global motor
    global vibration_strength
    while True:
        flex = flex_sensor.read_u16()
        print(flex)
        if flex > flex_sensitvitity:
            if vibration_strength == 0:
                motor.duty_u16(PWM_DUTY_LOW)
                test_led.duty_u16(int(PWM_DUTY_LOW / 4))
            elif vibration_strength == 1:
                print(PWM_DUTY_MED)
                motor.duty_u16(PWM_DUTY_MED)
                test_led.duty_u16(int(PWM_DUTY_MED / 2))
            elif vibration_strength == 2:
                motor.duty_u16(PWM_DUTY_HIGH)
                test_led.duty_u16(PWM_DUTY_HIGH)
            await asyncio.sleep_ms(vibration_duration)
            motor.duty_u16(PWM_DUTY_OFF)
            test_led.duty_u16(PWM_DUTY_OFF)
        else:
            test_led.duty_u16(PWM_DUTY_OFF)
            motor.duty_u16(PWM_DUTY_OFF)
        await asyncio.sleep(1)

async def main():
    work_task = asyncio.create_task(work())
    connect_task = asyncio.create_task(connect())
    await asyncio.get_event_loop().run_until_complete(asyncio.gather(work_task, connect_task))


# async def cycle_strengths():
#     global vibration_strength
#     while True:
#         vibration_strength = 0
#         print("0")
#         motor.duty_u16(PWM_DUTY_LOW)
#         await asyncio.sleep(5)
#         vibration_strength = 1
#         print("1")
#         motor.duty_u16(PWM_DUTY_MED)
#         await asyncio.sleep(5)
#         print("2")
#         vibration_strength = 2
#         motor.duty_u16(PWM_DUTY_HIGH)
#         await asyncio.sleep(5)

asyncio.run(main())