# rpi_access_control

This is a daemon for controlling access to the certain areas with turnstiles, doors and stuff. RPi, that this script must be connected to the turnstile via relay on pin 16. Optionally, refusal indicator may be placed onto 12 pin.

This scripts is written for a certain api of a certain service, details of which cannot be disclosed at the time of this publication.

It runs internal DB that allows the device function even when it is disconnected from the service.

To run the daemon, run main.py file.

To learn how to run script as daemon follow the link:
http://www.raspberrypi-spy.co.uk/2015/10/how-to-autorun-a-python-script-on-boot-using-systemd/

