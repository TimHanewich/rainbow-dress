from rainbow import *
import machine
import neopixel
import time

def test() -> None:

    re = RainbowEngine()

    # add strand 1
    s1 = Strand(5, MODE_TWINKLE)
    s1.new_twinkle_chance = 0.05
    re.add((s1, neopixel.Neopixel(5, 0, 22, "GRB")))

    # add strand 2
    s2 = Strand(12, MODE_TWINKLE)
    s2.new_twinkle_chance = 0.1
    re.add((s2, neopixel.Neopixel(12, 1, 19, "GRB")))

    while True:
        re.next()
        time.sleep(0.1)