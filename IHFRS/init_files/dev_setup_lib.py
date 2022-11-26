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


def configure_cmdline():
    spi_text = " spidev.bufsiz=65536"
    new_changes = 0
    print()
    print("---------------------------------------------------")
    print()
    print("Testing \"cmdline.txt\" for correct \"bufsiz\" for TCAM")
    print()
    print("---------------------------------------------------")
    print()
    with open("/boot/cmdline.txt", "r") as f, open("/boot/cmd_temp.txt", "w+") as f2:
        everything_old = f.read().rstrip()
        shell_serial = re.search("console=[a-zA-Z]+[0-9]{1},[0-9]*\s", everything_old)
        if shell_serial:
            print("Disabling shell over serial...")
            new_content = re.sub("console=[a-zA-Z]+[0-9]{1},[0-9]*\s", "", everything_old)
            f2.write(new_content)
            print("Shell over serial disabled.")
            new_changes = 1
        else:
            print("Shell over serial is already disabled, moving on...")

        f.seek(0)

        if spi_text.strip() in everything_old:
            print("\"bufsiz\" is already present, moving on...")
        elif (spi_text.strip() not in everything_old) and new_changes:
            print("Appending \"bufsiz\"...")
            everything_new = f2.read().rstrip()
            if f2.write(everything_new + spi_text) > 0:
                new_changes = 1
                print("\"bufsiz\" successfully appended.")
            else:
                print("Couldn't add bufsiz.")
        elif (spi_text.strip() not in everything_old) and not new_changes:
            print("Appending \"bufsiz\"...")
            if f2.write(everything_old + spi_text) > 0:
                new_changes = 1
                print("\"bufsiz\" successfully appended.")
            else:
                print("Couldn't add bufsiz.")

    if new_changes:
        print()
        print("Exchanging \"cmdline\" files...")
        os.remove("/boot/cmdline.txt")
        os.rename("/boot/cmd_temp.txt", "/boot/cmdline.txt")
    else:
        print()
        print("No changes needed...")
        os.remove("/boot/cmd_temp.txt")
    print("---------------------------------------------------")
    print()
    print("\"cmdline.txt\" setup COMPLETE!")
    print()
    print("---------------------------------------------------")
    print()


def configure_boot():
    print()
    print("---------------------------------------------------")
    print()
    print("Testing \"config.txt\" for correct settings for TCAM")
    print()
    print("---------------------------------------------------")
    with open("/boot/config.txt", "r") as f, open("/boot/config_temp.txt", "w") as f2:
        i2c = "dtparam=i2c_arm="
        spi = "dtparam=spi="
        serial = "enable_uart="
        new_changes = 0

        for line in f:
            li = line.strip()
            if (i2c in li) and not (li.startswith("#") or ("off" in li)):
                print("I2C is enabled.")
                f2.write(line)
            elif (i2c in li) and (li.startswith("#") or ("off" in li)):
                print("Enabling I2C...")
                f2.write(i2c + "on\n")
                new_changes = 1
            elif (spi in li) and not (li.startswith("#") or ("off" in li)):
                print("SPI is enabled.")
                f2.write(line)
            elif (spi in li) and (li.startswith("#") or ("off" in li)):
                print("Enabling SPI...")
                f2.write(spi + "on\n")
                new_changes = 1
            elif (serial in li) and not (li.startswith("#") or ("0" in li)):
                print("Serial is enabled.")
                f2.write(line)
            elif (serial in li) and (li.startswith("#") or ("0" in li)):
                print("Enabling Serial...")
                f2.write(serial + "1\n")
                new_changes = 1
            else:
                f2.write(line)

    if new_changes:
        print()
        print("Exchanging \"config\" files...")
        os.remove("/boot/config.txt")
        os.rename("/boot/config_temp.txt", "/boot/config.txt")
    else:
        print()
        print("No changes needed...")
        os.remove("/boot/config_temp.txt")
    print("---------------------------------------------------")
    print()
    print("\"config.txt\" setup COMPLETE!")
    print()
    print("---------------------------------------------------")
    print()





