import color_toolkit
import sys

def brighten(color:tuple[int, int, int], strength:float = 1.0) -> tuple[int, int, int]:

    # convert
    r:float = color[0] * strength
    g:float = color[1] * strength
    b:float = color[2] * strength

    # min/max
    r = min(max(r, 0), 255)
    g = min(max(g, 0), 255)
    b = min(max(b, 0), 255)

    # round
    r:int = int(r)
    g:int = int(g)
    b:int = int(b)

    # return
    return (r, g, b)


class PixelInstruction:
    """Very basic structure - just contains what pixel index to change and what color (RGB) to set it to."""

    def __init__(self, index:int = None, color:tuple[int, int, int] = None) -> None:
        self.index:int = index
        self.color:tuple[int, int, int] = color

    def __str__(self) -> str:
        return str({"index": self.index, "color": self.color})

class Strand:

    """Coordinates the pixel patterns on a single WS2812B strand."""

    def __init__(self, pix_count:int, strength:float = 1.0) -> None:

        # create the slices
        self.palette:list[tuple[int, int, int]] = color_toolkit.rainbow_slices(pix_count)

        # dull the palette if needed
        new_palette:list[tuple[int, int, int]] = []
        if strength < 1.0:
            for color in self.palette:
                new_palette.append(brighten(color, strength))
            self.palette = new_palette

        # on pixel
        self.on:int = None # index-based. self.on represents the pixel that is CURRENTLY illumniated at any point in time. Start with none to indicate NOTHING is turned on!

    def next(self) -> list[PixelInstruction]:

        # determine which to turn on, which to turn off
        to_turn_off:int = self.on # we will turn off the pixel we currently have on
        to_turn_on:int = None # index
        if self.on == None: # if we are on nothing (this has just been initiated)
            to_turn_on = 0
        elif self.on == (len(self.palette) - 1): # We are on the last one
            to_turn_on = 0
        else: # on any other one
            to_turn_on = self.on + 1

        # assemble list
        ToReturn:list[PixelInstruction] = []

        # if there is something currently on, turn it off
        if self.on != None:
            ToReturn.append(PixelInstruction(to_turn_off, (0, 0, 0)))

        # Add the next one we are to turn on
        ToReturn.append(PixelInstruction(to_turn_on, self.palette[to_turn_on]))

        # increment
        self.on = to_turn_on

        # return
        return ToReturn


## platform dependent!
#if sys.platform == "rp2": # if on Raspberry Pi Pico
if 0 == 0:

    import neopixel

    class RainbowEngine:
        def __init__(self) -> None:
            self.pairs:list[tuple[Strand, neopixel.Neopixel]] = [] # Stand, neopixel pairs

        def add(self, pair:tuple[Strand, neopixel.Neopixel]) -> None:
            self.pairs.append(pair)

        def next(self) -> None:
            """Displays the next 'frame' in the sequence for each Strand."""

            for pair in self.pairs:

                # generate next ones to set
                pixins:list[PixelInstruction] = pair[0].next()

                # set them
                for pi in pixins:
                    pair[1].set_pixel(pi.index, pi.color)

                # show the changes on this strand
                pair[1].show()

                

    
def test() -> None:

    re = RainbowEngine()
    re.add((Strand(5, 0.1), neopixel.Neopixel(5, 0, 22, "GRB")))

    while True:
        re.next()
        input("Did it!")

