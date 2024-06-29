import machine
import ssd1306
import time
import neopixel
import color_toolkit

# set up ADC
adc = machine.ADC(machine.Pin(26, machine.Pin.IN))

# set up OLED
i2c = machine.I2C(1, sda=machine.Pin(14), scl=machine.Pin(15))
print(i2c.scan())
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# set up neopixel
pixels1 = neopixel.NeopixelManager(neopixel.Neopixel(11, 0, 22, "GRB")) # 11 pixel strand on GP22
pixels2 = neopixel.NeopixelManager(neopixel.Neopixel(11, 1, 19, "GRB")) # 11 pixel strand on GP19

def burst_sample(duration:float = 1.0, samples:int = 100) -> int:
    """Takes average of analog reading over short period of time."""
    delay:float = duration / samples
    total:int = 0
    for _ in range(samples):
        total = total + adc.read_u16()
        time.sleep(delay)
    return int(round(total / samples, 0))

flip_every_ms:int = 15000
last_flipped_ticks_ms:int = time.ticks_ms()
leds_on:bool = False
while True:

    # turn on the pixels (we put this in the while loop because I may be taking them attaching them on and off to experiemtn with voltage, so keep showing!)
    if (time.ticks_ms() - last_flipped_ticks_ms) > flip_every_ms:
        print("Time to flip!")

        # select random color
        color:tuple[int, int, int] = color_toolkit.random_color()

        if leds_on == False:
            print("Flipped to on")
            pixels1.fill(color)
            pixels2.fill(color)
            leds_on = True
        else:
            print("Flipped to off")
            pixels1.fill((0, 0, 0))
            pixels2.fill((0, 0, 0))
            leds_on = False
        pixels1.show()
        pixels2.show()
        last_flipped_ticks_ms = time.ticks_ms()

    # estimate the total current being drawn from the neopixels using the NeopixelManagers!
    current_ma:float = pixels1.current + pixels2.current
    
    # sample the raw ADC reading of the battery
    val:int = burst_sample()

    # "add back" ADC points to accomodate for the voltage sag due to the current consumption of the neopixels!
    adc_drop_per_ma:float = 4.7040504848760 # determined this through observations (see readme!)
    val = val + int(adc_drop_per_ma * current_ma) # add back!

    # based on the sample reading, try to calculate volts
    full:tuple[int, float] = (50710, 2.62) # full, when on same power source
    dead:tuple[int, float] = (38715, 1.98) # depleted, when on same power source
    PercentOfRange:float = (val - dead[0]) / (full[0] - dead[0])
    volts:float = dead[1] + (PercentOfRange * (full[1] - dead[1]))

    # but now scale upward to remove the divider
    volts_scaled:float = volts / 0.32

    

    # display
    oled.fill(0)
    oled.text(str(val), 0, 0)
    oled.text(str(round(volts, 2)) + "v ADC", 0, 12)
    oled.text(str(round(volts_scaled, 2)) + "v", 0, 24)
    oled.text(str(int(current_ma)) + " mA", 0, 36)
    oled.show()

    time.sleep(0.5)
