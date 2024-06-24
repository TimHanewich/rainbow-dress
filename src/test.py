from rainbow import *
import machine
import neopixel

def test() -> None:

    re = RainbowEngine()
    re.add((Strand(5, 0.1), neopixel.Neopixel(5, 0, 22, "GRB")))

    while True:
        re.next()
        input("Did it!")