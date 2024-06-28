import machine
import ssd1306
import time
import neopixel

# set up ADC
adc = machine.ADC(machine.Pin(26, machine.Pin.IN))

# set up OLED
i2c = machine.I2C(1, sda=machine.Pin(14), scl=machine.Pin(15))
print(i2c.scan())
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# set up neopixel
pixels1 = neopixel.Neopixel(5, 0, 22, "GRB") # 5 pixel strand on GP22
pixels2 = neopixel.Neopixel(11, 1, 19, "GRB") # 11 pixel strand on GP19

def burst_sample(duration:float = 1.0, samples:int = 100) -> int:
    """Takes average of analog reading over short period of time."""
    delay:float = duration / samples
    total:int = 0
    for _ in range(samples):
        total = total + adc.read_u16()
        time.sleep(delay)
    return int(round(total / samples, 0))

while True:

    # turn on the pixels (we put this in the while loop because I may be taking them attaching them on and off to experiemtn with voltage, so keep showing!)
    pixels1.fill((255, 255, 255))
    pixels2.fill((255, 255, 255))
    pixels1.show()
    pixels2.show()
    
    # sample
    val:int = burst_sample()

    # based on the sample reading, try to calculate volts
    full:tuple[int, float] = (53100, 2.62)
    dead:tuple[int, float] = (40400, 1.98)
    PercentOfRange:float = (val - dead[0]) / (full[0] - dead[0])
    volts:float = dead[1] + (PercentOfRange * (full[1] - dead[1]))

    # but now scale upward to remove the divider
    volts_scaled:float = volts / 0.32

    # display
    oled.fill(0)
    oled.text(str(val), 0, 0)
    oled.text(str(round(volts, 2)) + "v ADC", 0, 12)
    oled.text(str(round(volts_scaled, 2)) + "v", 0, 24)
    oled.show()

    time.sleep(0.5)
