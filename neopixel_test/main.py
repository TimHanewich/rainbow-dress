import neopixel
import time

pixels = neopixel.Neopixel(12, 0, 22, "GRB")

def fill_and_wait(color:tuple[int, int, int]) -> None:
    pixels.fill(color)
    pixels.show()
    time.sleep(5)

# inf loop
while True:
    fill_and_wait((255, 255, 255)) # all white, full brightness (max consumption)
    fill_and_wait((255, 0, 0)) # red
    fill_and_wait((0, 255, 0)) # green
    fill_and_wait((0, 0, 255)) # blue
    fill_and_wait((128, 128, 128)) # all filled, half brightness
    fill_and_wait((0, 0, 0)) # off
    