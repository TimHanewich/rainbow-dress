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

    # based on the sample reading, try to calculate volts
    full:tuple[int, float] = (54700, 2.69)
    dead:tuple[int, float] = (39150, 1.92)
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
