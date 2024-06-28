import machine
import ssd1306
import time

# set up
adc = machine.ADC(machine.Pin(26, machine.Pin.IN))
i2c = machine.I2C(1, sda=machine.Pin(14), scl=machine.Pin(15))
print(i2c.scan())
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

def burst_sample(duration:float = 1.0, samples:int = 100) -> int:
    """Takes average of analog reading over short period of time."""
    delay:float = duration / samples
    total:int = 0
    for _ in range(samples):
        total = total + adc.read_u16()
        time.sleep(delay)
    return int(round(total / samples, 0))

while True:
    
    # sample
    val:int = burst_sample()

    # display
    oled.fill(0)
    oled.text(str(val), 0, 0)
    oled.show()

    time.sleep(0.5)
