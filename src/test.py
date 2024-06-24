from rainbow import *
import machine
import neopixel

def test() -> None:

    re = RainbowEngine()

    # add strand 1
    s1 = Strand(5, MODE_TWINKLE)
    s1.new_twinkle_chance = 0.05
    re.add((s1, neopixel.Neopixel(5, 0, 22, "GRB")))

    while True:
        re.next()
        input("Did it!")