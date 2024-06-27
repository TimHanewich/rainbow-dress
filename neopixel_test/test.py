import neopixel

def test_gp(gp:int) -> None:
    pixels = neopixel.Neopixel(12, 0, gp, "GRB")
    pixels.fill((10, 0, 10))
    pixels.show()
    print("Showed color on GP " + str(gp))