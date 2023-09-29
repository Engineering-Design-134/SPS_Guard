import machine
import time


flex_sensor = machine.ADC(machine.Pin(26, machine.Pin.IN))
led = machine.Pin("LED", machine.Pin.OUT)
led.off()

while True:
    flex_value = flex_sensor.read_u16()
    if flex_value > 100:
        led.on()
    else:
        led.off()
    print(flex_value)
    time.sleep(0.1)
