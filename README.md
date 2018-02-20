# fingerpi

[![Code Issues](https://www.quantifiedcode.com/api/v1/project/1cbb69065eb748f18b315ddaccad0e12/badge.svg)](https://www.quantifiedcode.com/app/project/1cbb69065eb748f18b315ddaccad0e12)

Python library for GT-511C3. The library was tested on Raspberry Zero.

<img src="demo_code.png" alt="Code" width="300"/>

<img src="demo.png" alt="Demo Image" width="300"/>


## Connectivity

R-Pi GPIO pinout: https://pinout.xyz/

### Raspberry Pi Zero (40 pin, 3.3 V IOs)
I used optional resistors in case there is [another FTDI connection](http://www.billporter.info/2011/06/26/how-to-add-multiple-uart-connections/)

```
                       (Optional)
----------------------   1kOhm    ------------------------
GT-511C3     Tx (1)--|----/\/\----|--(10) RxD   R-Pi Zero
             Rx (2)--|----/\/\----|--(8)  TxD
            Gnd (3)--|------------|--(6) Gnd
             5V (4)--|------------|--(2) 5V
----------------------            ------------------------
```

### Raspberry Pi (40 pin, 5 V IOs)
```
----------------------                 ------------------------
GT-511C3     Tx (1)--|-----------------|--(10) RxD   R-Pi
             Rx (2)--|---.-----/\/\----|--(8)  TxD
                     |   |    1kOhm    |
                     |   \             |
                     |   /             |
                     |   \ 2kOhm       |
                     |   |             |
            Gnd (3)--|---.-------------|--(6) Gnd
             5V (4)--|-----------------|--(2) 5V
----------------------                 ------------------------
```

## Usage

Run `demo.py` for a demo

## Troubleshooting

If you are stuck at `Opening connection...`, as described out by @Ankush-Pathak in #19:

> - Do "sudo nano /boot/config.txt" via ssh or by opening a terminal on the pi.
> - Scroll down to the end of the file using arrow keys, on a new line add "dtoverlay=pi3-disable-bt".
> - Then do ctrl + o, return(saves your file), ctrl + x(exits nano).
> - Reboot.
> - If this does not work, many people also suggested changing the modes of the required GPIO pins to ALT0 or ALT5. You could try that too.
## TODO
- Documentation
- Unit tests
- GUI
