## Trying GPIO's with Neopixels
- Confirmed to work
    - 22
    - 19
- Cannot get to work for whatever reason.
    - 3

## Learning Resources
- [This article](https://www.raspberrypi.com/news/how-to-power-loads-of-leds-with-a-single-raspberry-pi-pico/) describes the purpose of the StateMachine pretty well and why there is only a maximum of 8 neopixel strands it can support.

## Voltage Dividing
This project uses a voltage divider to proportionally scale down the voltage of the full battery pack to a window that can be read by the Raspberry Pi Pico's ADC pins (below 3.3v).

It is 32%

|Situation|Battery Pack Voltage|Divided Voltage|ADC Reading|
|-|-|-|-|
|Two fully charged 18650s in series|8.4|2.69|54700|
|Two fully depleted 18650s in series|6.0|1.92|39150|

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


