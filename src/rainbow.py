import color_toolkit
import sys
import random

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
    
class LEDTwinkle:
    """Used for purposes of tracking LED Twinkles"""
    def __init__(self) -> None:
        self.index:int = None
        self.color:tuple[int, int, int] = None
        self.strength:float = None # 0.0 to 1.0
        self.direction:bool = None # True = on way up (strengthening), False = on way down (weakening)

# Strand modes and Strand class
MODE_RUN:int = 0
MODE_TWINKLE:int = 1
MODE_RUN_TRAIL:int = 2
class Strand:

    """Coordinates the pixel patterns on a single WS2812B strand."""

    def __init__(self, pix_count:int, mode:int, strength:float = 1.0) -> None:

        # strand mode
        self.mode:int = mode

        # create the slices
        self.palette:list[tuple[int, int, int]] = color_toolkit.rainbow_slices(pix_count)

        # dull the palette if needed
        new_palette:list[tuple[int, int, int]] = []
        if strength < 1.0:
            for color in self.palette:
                new_palette.append(brighten(color, strength))
            self.palette = new_palette

        # MODE_RUN related settings (if it isn't in run mode, whatever, don't use it)
        self.on:int = None # index-based, what pixel is currently "on". self.on represents the pixel that is CURRENTLY illumniated at any point in time. Start with none to indicate NOTHING is turned on!

        # MODE_TWINKLE related settings
        self.new_twinkle_chance:float = 0.1 # likelihood a new twinkle will start someone on the strip in any given frame.
        self.twinkles:list[LEDTwinkle] = []
        self.strength_jump:float = 0.1 # the percent to move up/down in strength with each passing frame.

        # MODE_RUN_TRAIL
        self.trail_length:int = 2 # how many LED's will 'trail' behind the lead 




    def next(self) -> list[PixelInstruction]:
        if self.mode == MODE_RUN:

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
        
        elif self.mode == MODE_TWINKLE:

            # first continue the current twinkles
            # update the twinkle status below
            for twinkle in self.twinkles:
                if twinkle.strength == 1.0: # we are at the very top as is! So time to turn it around
                    twinkle.direction = False # Start going down!
                    twinkle.strength = twinkle.strength - self.strength_jump # go down!
                else: # we have not peaked yet, so continue with direction
                    if twinkle.direction == True: # on the way up
                        twinkle.strength = min(twinkle.strength + self.strength_jump, 1.0)
                    else: # we are on the way down
                        twinkle.strength = max(twinkle.strength - self.strength_jump, 0.0)

            # add new twinkle?
            if random.random() <= self.new_twinkle_chance: # chance struck! 

                # before we go ahead to make a new one, ensure that not every single pixel is already occupied with an ongoing twinkle
                if len(self.twinkles) < len(self.palette): # if the # of twinkles open right now is less than the total number of indexes

                    nt:LEDTwinkle = LEDTwinkle()

                    # select index at random until we get an index that is not currently already undergoing a twinkle sequence
                    nt.index == None
                    while nt.index == None:
                        possible_nt_index = random.randint(0, len(self.palette) - 1)

                        # validate that there isn't an open twinkle for that LED right now
                        for twinkle in self.twinkles:
                            if twinkle.index == possible_nt_index:
                                possible_nt_index = None
                        
                        # if it isn't cleared, that means it is free! so take it
                        if possible_nt_index != None:
                            nt.index = possible_nt_index

                    # select color, based on palette
                    nt.color = self.palette[nt.index]

                    # start it off
                    nt.strength = 0.0 # start at nothing
                    nt.direction = True # go up

                    self.twinkles.append(nt)

            # now convert all of the twinkles into PixelInstructions
            ToReturn:list[PixelInstruction] = []
            for twinkle in self.twinkles:
                pi:PixelInstruction = PixelInstruction()
                pi.index = twinkle.index
                pi.color = brighten(twinkle.color, twinkle.strength)
                ToReturn.append(pi)

            # Now that we have translated them into pixel instructions that will be returned, now we can strip out any completed twinkles
            # it is important to do this AFTER the pixel instructions have been made. Because if you strip them out before making the Pixel Instructions, the instruction to turn that partcular LED off (0, 0, 0) will not be realized.
            # strip out any twinkles that have ended (strenght at 0.0 and direction of False, down)
            CompletedTwinkles:list[LEDTwinkle] = []
            for twinkle in self.twinkles:
                if twinkle.direction == False and twinkle.strength == 0.0:
                    CompletedTwinkles.append(twinkle)
            for twinkle in CompletedTwinkles:
                self.twinkles.remove(twinkle)
            
            return ToReturn

        elif self.mode == MODE_RUN_TRAIL:

            # determine which index is next
            next_index:int = None
            if self.on == None: # not on anything! It is brand new!
                next_index = 0
            else:
                next_index = self._increment(self.on)

            # collect a list of trailing indexes, in order from closest to furthest away from the leading index selected above.
            trail:list[int] = []
            for x in range(self.trail_length):
                trail.append(self._decrement_by(next_index, x + 1))
            
            # turn these into a list of pixel commands
            ToReturn:list[PixelInstruction] = []

            # first pixel command - turn off the very last one from the end of the trail in the last frame
            if self.on != None: # if there is something on right now! (there may not be if this is brand new)
                to_turn_off_index:int = self._decrement_by(self.on, self.trail_length) # select last one
                ToReturn.append(PixelInstruction(to_turn_off_index, (0, 0, 0)))

            # next ones, the trail. 
            max_strength:float = 0.8 # max strength of the trail
            min_strength:float = 0.1 # min strength of the trail
            percent_step:float = (max_strength - min_strength) / self.trail_length
            at_strength:float = max_strength
            for index in trail:
                this_color:tuple[int, int, int] = self.palette[index]
                this_color = brighten(this_color, at_strength) # dim it, so it is a trail
                ToReturn.append(PixelInstruction(index, this_color)) # add it
                at_strength = at_strength - percent_step # increment strength so the next in the trail is higher
            
            # now, lets do the leading pixel (the "on")
            ToReturn.append(PixelInstruction(next_index, self.palette[next_index]))

            # before returning, increment "on" (save state)
            self.on = next_index

            return ToReturn
        
        else:
            raise Exception("Mode '" + str(self.mode) + "' not a valid mode.")
        

    def _increment(self, _from:int) -> int:
        """Increments index upward, given the length of the strand (will revert back to 0 if over length). Just a mathematical helper."""

        if _from == (len(self.palette) - 1): # if we are on the last one
            return 0
        else:
            return _from + 1
    
    def _decrement(self, _from:int) -> int:
        """Decrements index downward, given the length of the strand (will revert back to the top if needed). Just a mathematical helper."""

        if _from == 0:
            return len(self.palette) - 1
        else:
            return _from - 1
        
    def _decrement_by(self, _from:int, steps:int) -> int:
        ToReturn:int = _from
        for _ in range(steps):
            ToReturn = self._decrement(ToReturn)
        return ToReturn


## platform dependent!
if sys.platform == "rp2": # if on Raspberry Pi Pico

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

                