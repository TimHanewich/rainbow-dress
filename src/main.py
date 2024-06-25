from rainbow import *
import machine
import neopixel
import time
import ssd1306
import voltage
import BatteryMonitor

# set up SSD1306
i2c = machine.I2C(1, sda=machine.Pin(14), scl=machine.Pin(15))
oled = ssd1306.SSD1306_I2C(128, 64, i2c)

# set up voltage reader
vs = voltage.VoltageSensor(26) # GPIO 26

# set up battery monitor to convert the voltage we read to state of charge %'s
bm = BatteryMonitor.BatteryMonitor()

def test() -> None:

    re = RainbowEngine()

    # add strand 1
    s1 = Strand(5, MODE_TRAIL)
    s1.trail_length = 3
    re.add((s1, neopixel.Neopixel(5, 0, 22, "GRB")))

    # add strand 2
    s2 = Strand(12, MODE_TRAIL)
    s2.trail_length = 5
    re.add((s2, neopixel.Neopixel(12, 1, 19, "GRB"))) # has to use a different StateMachine than the first. 0-7. Can only do 8 unique strands.

    # how often to update SSD-1306?
    update_display_every_seconds:float = 1.0
    display_last_updated_ticks_ms:int = 0

    while True:
        re.next() # show next pattern

        # read voltage
        volts:float = vs.voltage()

        # calculate SOC
        soc:float = bm.soc(volts)
        socs:str = str(round(soc * 100, 1)) + "%"
        
        # what to print on SSD-1306
        if (time.ticks_ms() - display_last_updated_ticks_ms) > (update_display_every_seconds * 1000):
            oled.fill(0)
            oled.text(str(round(volts, 2)) + "v", 0, 0)
            oled.text("SOC: " + socs, 0, 12)
            oled.show()
            display_last_updated_ticks_ms = time.ticks_ms()

        # sleep
        time.sleep(0.1)

test()