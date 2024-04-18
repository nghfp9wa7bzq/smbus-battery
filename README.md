# smbus-battery
Initiate charging on a Dell U4873 battery and read its data.  
This script can be used with other batteries as well.  

I have bought a Dell U4873 battery a long time ago for a project, that I still haven't really started...  
![dell_batt](https://github.com/nghfp9wa7bzq/smbus-battery/assets/149590243/bb9cdb9f-821f-4990-8a7e-58d129aa40de)  
In order to preserve it, I wanted to charge it after many years.  
The first time, I have used a dell laptop to do so, but now I have used my raspberry pi 3b.  
  
This battery needs a charge start code sent to it to allow current to flow.  
I have used an adjustable adapter, first set to 12 V with a series UF5408 3A diode,  
then without the diode.  
The diode lowered the input voltage and with it the input current.  
It also prevents reverse current flow.  
It got hot in the first minute, so I have interrupted the charging,  
but seeing that the current dropped to 1A, which is fine of course,  
I have started charging again.  
After the current has dropped to 300 mA, I have removed the diode,  
allowing more current to flow.  
Because my adapter is 12 V, it wasn't sufficient to fully charge the battery.  
![dell_batt_2024_04_17](https://github.com/nghfp9wa7bzq/smbus-battery/assets/149590243/6b72b164-3f75-4b5e-94ba-07734750a2ca)  
(Sample script output.)  
  
Ideally you would use a lab bench power supply with a constant voltage, that is in the battery data,  
(12.975 V) and a current limit to 1 A.  
Note that the battery sets the charging current data and when it is zero, you must stop charging.  
(The battery charger chip in a laptop reads out this data to control the charging process.)  
Keep an eye on the battery temperature as well, both in the data and also by touching the battery.  
Bad cells may heat up or even cause fire, so **YOU ARE DOING THIS AT YOUR OWN RISK!!!**  
  
I have also tried two old batteries for an acer aspire 5560 laptop.  
![or_batt](https://github.com/nghfp9wa7bzq/smbus-battery/assets/149590243/4a7d8c73-a011-4019-9abc-7cf4ad9bb119)![marked_good_but_dead](https://github.com/nghfp9wa7bzq/smbus-battery/assets/149590243/d2f53388-777c-419b-b680-a85c82fe900b)  
Both were dead, which was later confirmed by dismantling them and trying to charge the parallel cell pairs with a lab PSU set to 4 V and 1 A.  
Essentially no current was flowing, so the cells were dead too...  
The two controller ICs are bq20z955 and SN8765.  
Turns out, these are aliases for [bq20z95](https://www.alldatasheet.com/datasheet-pdf/pdf/209415/TI/BQ20Z95.html) and [bq3050](https://www.ti.com/product/BQ3050) [(datasheet)](https://www.ti.com/lit/ds/symlink/bq3050.pdf?ts=1713364218043) [tech ref.](https://www.ti.com/lit/ug/sluu485a/sluu485a.pdf) gas gauge / battery management chips.  
There is a ton of information for these!  

### Pinouts  
See links.  
**Verify** with a multimeter.  
Generally the two and two edge pins are GND and V+ (battery output).  
The pins between these are:  
 - SCL and SDA for SMBus / I2C communication, next to each other.  
 - Syspres / System Present - This is an input of the battery controller, which should be connected to GND,  
   so that the controller wakes up and allows current to flow. Essentially it is an active low battery enable pin.  
 - Battery present - This is essentially the same, but for the system to know, that a battery is connected.  
   Inside the battery it is connected to GND. NOTE that I have labelled these incorrectly on the battery picture...  
 - T - a temperature output. This is a resistive value, that changes with the temperature.  
   You can use another resistor to form a voltage divider and read the voltage with an ADC.  

My Dell battery: GND, GND, T, SYSPRES, BATTPRES (GND), SDA, SCL, V+, V+  
My Acer batteries: V+, V+, SYSPRES, T, SCL, SDA, GND, GND  (looking at it like the above picture)  
  
### Connections  
You will need to make the following connections:  
GND - connect the [ground of the rpi](https://www.raspberrypi.com/documentation/computers/raspberry-pi.html#gpio-and-the-40-pin-header), the battery, and the charger / lab PSU.  
SCL and SDA - connect these battery to the pins of the rpi (or whatever you are using).  
SYSPRES / Battery enable - I have used a 10 kOhm resistor to ground. I guess it should be fine with a direct connection to GND as well...  
V+ - connect this to the positive side of your charger / lab PSU.

### Using the script  
First, you have to find out, where the battery is connected to.  
Install i2c-tools.
`sudo apt install i2c-tools`  
(You may also need i2c-dev.)  
Use i2cdetect to list I2C buses:  
`sudo i2cdetect -l`  
From this list, try a bus:  
`sudo i2cdetect -y 0`  
The above searches for I2C devices on bus 0 (first in the list.)  
and gives you an ASCII table with active addresses.  
My batteries were at 0x0b.  
You can read data with:  
`sudo i2cget -y 0 0x0b 0x09`  
bus_address device_address memory_address  
This reads the battery voltage.  
  
Use my script:  
`python smbus.py`  
  
### Links  
[Battery Powered Raspberry Pi in Repurposed Laptop : 16 Steps (with Pictures) - Instructables](https://www.instructables.com/Battery-Powered-Raspberry-Pi-in-Repurposed-Laptop/)  
[Pinouts of Laptop/Notebook Batteries: Lötlabor Jena](https://loetlabor-jena.de/doku.php?id=projekte:pinout:laptopbatteries:start)  
[Acer Ac14b8k battery pinout – Acer – Laptop Battery Analyzer and Repair Forum](https://www.laptopu.ro/community/pinouts-for-acer-batteries/acer-ac14b8k-battery-pinout/)  
[How to disassemble ACER laptop battery, what's inside an AS10D81 battery with banks for 10 years - YouTube](https://www.youtube.com/watch?v=H1s2zjchSvs) - NOTE: you probably don't want to bother with this...  
[Acer battery clear pf flag using raspberry pi - Page 1](https://www.eevblog.com/forum/microcontrollers/acer-battery-clear-pf-flag-using-raspberry-pi/)  
[Again on BQ3050 - SN8765 · Issue #22 · laszlodaniel/SmartBatteryHack](https://github.com/laszlodaniel/SmartBatteryHack/issues/22)  
[SmartBatteryHack/Python/RPi2_test.py at master · laszlodaniel/SmartBatteryHack](https://github.com/laszlodaniel/SmartBatteryHack/blob/master/Python/RPi2_test.py) - I haven't tested this, but seems like mine...  
