import neopixel

# init and clear
pixels = neopixel.Neopixel(5, 0, 22, "GRB")
pixels.fill((0, 0, 0))
pixels.show()

