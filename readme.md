## Trying GPIO's with Neopixels
On a Raspberry Pi Pico, I tested and was able to get Neopixel control of the WS2812b strand with almost every GPIO pin (tested and confirmed functionality on GP 0, 1, 2, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 19, 20, 21, 22, 27, 28).

However, for whatever reason, I was not able to confirm functionality on GP 3 and 26. I don't know if this is specific to the board I was working on (maybe I didn't solder the pin correctly and there is a short), but worth noting.

## Learning Resources
- [This article](https://www.raspberrypi.com/news/how-to-power-loads-of-leds-with-a-single-raspberry-pi-pico/) describes the purpose of the StateMachine pretty well and why there is only a maximum of 8 neopixel strands it can support.

## Voltage Dividing
This project uses a voltage divider to proportionally scale down the voltage of the full battery pack to a window that can be read by the Raspberry Pi Pico's ADC pins (below 3.3v).

![voltage divider](https://i.imgur.com/WzduiHU.png)

As you can see in the image above, a voltage divider with a 100,000 ohm resistor on the positive terminal and a 47,000 ohm resistor on the negative terminal will cut the source voltage to only 32% of its original state. This **32%** is very important for proportionally calculating what the battery pack's voltage is, based upon the 32% the pico will be reading on its ADC pins (read on below).

Recording voltage of a separate system from the system that is powering the Pico:
|Situation|Battery Pack Voltage|Divided Voltage (32%)|ADC Reading|
|-|-|-|-|
|Two fully charged 18650s in series|8.2|2.62|53100|
|Two fully depleted 18650s in series|6.2|1.98|40400|

Recording voltage of a power source that is *also* powering the Pico itself:
|Situation|Battery Pack Voltage|Divided Voltage (32%)|ADC Reading|
|-|-|-|-|
|Two fully charged 18650s in series|8.2|2.62|50710|
|Two fully depleted 18650s in series|6.2|1.98|38715|

After observing the readings above, we can say the proportion is a difference in 20,195 ADC reading is a 1.0V difference in the reading. 

However, keep in mind this is the *divded* voltage. Because our voltage divider reduces the voltage here to 32% of its *actual voltage at the terminals of the battery pack*, we must restore it to its full size to get the actual voltage of the battery pack. 

So, for example:
```
The ADC reading is 48034.

Scaled within the known range above, we can interpret that reading as being 2.36 volts on the ADC pin (scaled within range, use proportions).

But, since this is the divided voltage, we must re-scale it to get the actual voltage of the battery pack. 

Since we know the voltage divider brought the voltage down to 32%, we can just divide the read voltage by 0.32.

2.36 / 0.32 = 7.37 volts is the battery pack's voltage.
```

## Voltage Sag?
I performed tests of recording the voltage of the battery pack via the ADC channel in three configurations: no neopixels attached (the only thing consuming from the battery was the buck converter and Pi), a single strand of 5 neopixels attached, and then both strands of 5 neopixels and 11 neopixels attached (totaling 16 neopixels).

In both scenarios of neopixels being attached, every neopixel was on its max brightness, 255,255,255. 

In these all of these tests, the actual voltage of the battery pack was >= 7.76v (what I measured at the end of all of the tests). So, the voltage is being underestimated even with little to no load (other than the Raspberry Pi and buck converter), and the underestimation continues even further when under load of neopixels.

|Scenario|ADC Reading|Read Voltage|Scaled Pack Voltage|
|-|-|-|-|
|0 neopixels|48670|2.4|7.49|
|5 neopixels @ 255,255,255|48450|2.39|7.45|
|16 neopixels @ 255,255,255|48200|2.37|7.41|

## Observing the Correlation Between Voltage Sag and Neopixel Battery Consumption
Using the `NeopixelManager` class from [here](https://github.com/TimHanewich/MicroPython-Collection/blob/master/NeopixelManager/neopixel.py) from commit `6aa62f56df12e6f01aa5c7ae18877555ad04907a`, I am now able to estimate the current consumption of the neopixel strands that are being powered, based on their number of pixels and color each pixel is showing.

I set up a test to observe the correlation between voltage sag and the estimated current being drawn from the power source based. You can find that test [here](./tests/voltage/) on commit `37df69d80cada195c118876c04fcdca3f32cb3f1` of this repository. 

The test continues to show random colors across two neopixel strands, displaying the estimated current consumption of those strands and the ADC reading from the voltage divider. The test flips back and forth between a random color and the color (0,0,0) (all off), allowing you to observe the immediate voltage sag from the power source despite there not being a change in voltage (I recorded these tests from a DC power supply so there really isn't sag I don't think). Regardless, these are the results:

These are the results, at varying power source supply voltage levels:

|ADC Reading at (0,0,0)|ADC Reading w/ Random Color|NeopixelManager Estimated Current (mA)|
|-|-|-|
|46800|44900|413|
|46800|44550|479|
|46800|45721|233|
|46800|46180|148|
|46800|44920|413|
|46800|45350|311|
|46800|44600|462|
|46800|43900|608|
|46800|44750|449|
|46800|45634|246|
|46800|45500|278|
|46800|44700|458|
|46800|46000|213|
|46800|44300|568|
|40555|38100|475|
|40555|38132|472|
|40555|39923|136|
|40555|38850|341|
|40555|37700|554|
|40555|38570|394|
|40555|37688|567|

Using the readings above, it is actually not hard at all to find a correlation, and a very linear and predictable one at that...

On average, for every mA of current draw out of the neopixels, we can expect the ADC reading to be lowered (due to voltage sag?) by **4.7040504848760** points.

So how can we accomodate for this voltage sag when estimating the voltage of the battery? For every estimated mA of current draw by the `NeopixelManager`, add **4.7040504848760** back on top *before* using the read ADC to calculate the actual voltage on that pin and then the scaled voltage of the full pack.

## Estimating Total Current Consumption for the Entire System
From waist to ground is about 38 inches.

We want 8 full strands from waist to ground. So, 38*8 = 304 inches of neopixels.

The [strands I am using](https://a.co/d/03c6hYHa) are 150 LEDs per 16.4 ft, or 196 inches. Or a density of 0.765 pixels per inch (another way of saying 1.31 inches in between each pixel, just flipped).

So, for 304 inches, at 0.765 pixels per inch, that would be approximately 232 pixels.

Estimated current consumption @ 5V:
|Color|Total Amps (neopixel only)|
|-|-|
|255,255,255|8.8|
|255,0,0|3.04|
|0,255,0|3.04|
|0,0,255|3.02|
|128,128,128|4.52|
|0,0,0|0.15|

The good news, at only 0.15 amps idling, the system could certainly turn on. But the other values are exceptionally high. Don't think my two 18650 batteries in a series can support such a high discharge rate. And if they could, likely not for long.

However, keep in mind that not all pixels will be on at the same time. Will likely adopting a pattern in which they twinkle, "fall", etc.

## Measuring Capacity of my 18650 Batteries
I have a handful of unprotected 18650 batteries that I salvaged out of an old drill battery pack.

I charged one up to fully charged, according to my balance charger (4.1V) and used the balance charger to fully discharge down to 3.1V, fully discharged according to my balance charger. I discharged at a rate of 0.8 amps.

The amperage extracted from the battery after ~82 minutes after fully discharging totalled 1109mAh, or 1.11 Ah.

But, charging it back up to 4.1V only reads that it put back 985 mAh. Weird.

## Tests I Created and Performed
- [voltage](./tests/voltage/) on commit `534b1bc19a855027a01a37e4c7f81d3ae7e5f558` contains simple code that reads the incoming ADC and translates this to a voltage on the battery pack. Consistently lower voltage reading on the pack by 0.41 volts lower than actual. Need to adjust measurements?
- [voltage](./tests/voltage/) on commit `8e1ac485fb3d0d026500dfda2ca8cdc88c92eb62` does the same as above, but also turns on two strands of neopixels at full brightness. This test is to observe any voltage sag when the battery is under load!