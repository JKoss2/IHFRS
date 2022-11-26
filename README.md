# IHFRS - Senior Design Team 12

This repository contains code and libraries for the project our senior design team has undertaken.

**Installation**
1. On the SD card for your Raspberry Pi, **install Raspbian OS Lite**. (You must choose 32-bit if using Pi Zero W, read below)
   1. If using Raspberry Pi Imager (suggested), make sure to use the settings cog to set the following BEFORE installing...
      1. **Hostname**: your choice
      2. **Enable SSH**: (password authentication)
      3. **Set username and password**: Username must = "pi" for now. Password can be your choice.
      4. **Configure wireless LAN**: Be sure to choose a 2.4GHz capable network.
         1. **Set wireless LAN country**: "US"
      5. **Set locale settings**
   2. If you choose to flash the OS using other means, ensure you set the above settings, so you can connect wirelessly to the PI.
2. Download the IHFRS code files using either of these methods:
   1. From the "top-level" of this repository: (where you currently are)
      * Click the green "Code" button and download the zip file to your computer
      * **OR**
      * Right-click on the `IHFRS` folder, then "Download linked file as.."
3. Insert SD card into RPI and turn on. Allow RPI to boot and connect to Wi-Fi (~2 mins).
   * If you did not set up the Wi-Fi, hostname, etc., now is the time to connect a keyboard and monitor and use `sudo raspi-config` to set up those settings. There are other ways to do this as well.
4. Ensure your RPI is on your local network:
   * Use terminal or command prompt to `ping *hostname*` 
   * **OR**
   * Try connecting to RPI using SSH 
   * **OR**
   * Try connecting with FTP or SFTP utility
5. Use FTP or SFTP to upload `IHFRS` folder only to home directory `/home/pi/` on the RPI.
6. SSH into your RPI and run the following, in order:
   1. `cd /IHFRS`
   2. `sudo python init_setup.py` (~8 mins)
      * Observe the output as it runs. You will be required to answer multiple questions. No *RED* text should appear.
      * use `y` to reboot the PI when it reaches the end.
7. Make the necessary hardware connections. Pictures are shown at the very bottom of this README.
   * TCAM hardware connection (**JUMPER [MODE - GND], 5V, GND, TXD0, RXD0, SPI0_MISO, SPI0_CE0, SPI0_CLK**)
   * MQ2 Sensor connection (**5V, GND, GPIO4**) (Use "DO" (Digital Out) on the MQ2 sensor for GPIO4, **NOT** "AO")
8. In the SSH session (Working directory is still IHFRS) run `python IHFRS_run.py`
9. The code is now running. (This will be automatic later on.)

## Acknowledgements:
### Dan Julio
https://github.com/danjulio
* Hardware and base code for TCAM board featuring the FLIR Lepton 3.5 sensor.

### Todd Lawall
https://github.com/bitreaper
* Python Implementation of TCAM code and special assistance with tracking down errors.

### Ivan Kalchev
https://github.com/ikalchev
* HAP-Python Library for Homekit Integration

### Jason Burgett
https://github.com/jasbur
* RaspiWiFi - Initial WiFi configuration for RPI


