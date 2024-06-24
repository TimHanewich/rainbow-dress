from rainbow import *
import machine
import neopixel
import time

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

    while True:
        re.next()
        time.sleep(0.1)

test()