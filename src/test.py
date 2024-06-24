import neopixel
import rainbow
import time

s = rainbow.Strand(12, rainbow.MODE_RUN_TRAIL)
pixs = neopixel.Neopixel(12, 0, 22, "GRB")
re = rainbow.RainbowEngine()
re.add((s, pixs))

while True:
    re.next()
    time.sleep(0.25)