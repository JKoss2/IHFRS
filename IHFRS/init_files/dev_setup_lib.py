import os
import sys


def install_prereqs():
    is_64bits = sys.maxsize > 2 ** 32
    is_armv7 = os.uname()[4] == "armv7l"

    os.system('clear')
    os.system('apt update')
    os.system('clear')
    os.system('apt upgrade')
    print("-----------------------------------------------------------")
    print("---------------------------------------------------")
    print()
    print("Installing pre-requisites......")
    print()
    print("---------------------------------------------------")
    print("Installing apt libraries...")
    os.system('apt install python3 python3-rpi.gpio python3-pip python3-pil python3-pil.imagetk dnsmasq hostapd '
              'libavahi-compat-libdnssd-dev -y')
    print("-----------------------------------------------------------")
    print("Upgrading pip...")
    os.system('pip3 install --upgrade pip')
    print("-----------------------------------------------------------")
    print("Installing pip libraries...")
    os.system('pip3 install pyOpenSSL cryptography==38.0.1 twilio flask pyserial')
    print("-----------------------------------------------------------")
    print("Trying to install HAP-python...")
    if is_64bits or is_armv7:
        os.system('pip3 install HAP-python[QRCode]')
    else:
        print("You're using armv6l, HAP-python can't be used :( , moving on...")
    print("-----------------------------------------------------------")
    print("Installing PiWiFi_Setup...")
    os.system('apt install /home/pi/IHFRS/PiWiFiSetup_0.0.5/pi-wifi-setup_0.0.5_all.deb -y')
    os.system('apt autoremove')
    print("-----------------------------------------------------------")
    print("---------------------------------------------------")
    print()
    print("Install of pre-requisites COMPLETE!")
    print()
    print("---------------------------------------------------")


def add_buf_to_cmdline():
    spi_text = " spidev.bufsiz=65536"
    print("---------------------------------------------------")
    print()
    print("Testing \"cmdline.txt\" for correct \"bufsiz\" for TCAM")
    print()
    print("---------------------------------------------------")
    with open("/boot/cmdline.txt", "r") as f:
        everything_old = f.read().rstrip()
        if spi_text.strip() in everything_old:
            print("\"bufsiz\" is already correct, moving on...")
            return
        with open("/boot/cmd_temp.txt", "w") as f2:
            if f2.write(everything_old + spi_text) > 0:
                print("\"bufsiz\" successfully appended.")
    print("Exchanging \"cmdline\" files...")
    os.remove("/boot/cmdline.txt")
    os.rename("/boot/cmd_temp.txt", "/boot/cmdline.txt")
    print("---------------------------------------------------")
    print()
    print("\"cmdline.txt\" setup COMPLETE!")
    print()
    print("---------------------------------------------------")


def configure_initial_files():
    print("---------------------------------------------------")
    print()
    print("Exchanging \"/boot/config.txt\" file with correct settings...")
    print()
    print("---------------------------------------------------")
    os.system('sudo cp /boot/config.txt /boot/config.txt.bak')
    os.system('sudo cp init_files/boot_config_init.txt /boot/config.txt')
    print("---------------------------------------------------")
    print()
    print("Exchange of \"/boot/config.txt\" file COMPLETE!")
    print()
    print("---------------------------------------------------")




