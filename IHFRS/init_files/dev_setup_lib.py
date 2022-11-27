import os
import sys
import re


def install_prereqs():
    is_64bits = sys.maxsize > 2 ** 32
    is_armv7 = os.uname()[4] == "armv7l"

    os.system('clear')
    os.system('apt update')
    os.system('clear')
    os.system('apt upgrade')
    print()
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
    print()


def configure_cmdline():
    print()
    print("---------------------------------------------------")
    print()
    print("Testing \"cmdline.txt\" for correct \"bufsiz\" for TCAM")
    print()
    print("---------------------------------------------------")
    print()
    print("Checking for cmdline settings...")
    with open("/boot/cmdline.txt", "r") as f, open("/boot/cmd_temp.txt", "w+") as f2:
        spi_text = " spidev.bufsiz=65536"
        new_changes = 0
        error = 0

        everything_old = f.read().rstrip()
        shell_serial = re.search("console=[a-zA-Z]+[0-9]{1},[0-9]*\s", everything_old)
        if shell_serial:
            print("Disabling shell over serial...")
            new_content = re.sub("console=[a-zA-Z]+[0-9]{1},[0-9]*\s", "", everything_old)
            if f2.write(new_content) > 0:
                print("     ...Shell over serial disabled.")
                new_changes = 1
            else:
                print()
                print("!!! ERROR !!! Error writing new change (Removing Sh_o_Ser). Sh_o_Ser was enabled.")
                print()
                error += 1
        else:
            print("     ...Shell over serial is already disabled, moving on...")

        if spi_text.strip() in everything_old:
            print("     ...\"bufsiz\" is already present, moving on...")
        elif spi_text.strip() not in everything_old:
            print("Appending \"bufsiz\"...")
            everything_new = f2.read().rstrip()

            if new_changes:
                pre_text = everything_new
            elif not new_changes:
                pre_text = everything_old

            if f2.write(pre_text + spi_text) > 0:
                print("     ...\"bufsiz\" successfully appended.")
                new_changes = 1
            else:
                print()
                print("!!! ERROR !!! Couldn't add bufsiz.")
                print()
                error += 1

    if new_changes and not error:
        print("Exchanging \"cmdline\" files...")
        os.remove("/boot/cmdline.txt")
        os.rename("/boot/cmd_temp.txt", "/boot/cmdline.txt")
        if os.path.isfile('/boot/cmdline.txt'):
            print("     ...File exchange successful!")
        else:
            print()
            print("!!! ERROR !!! Issue occurred when trying to replace `cmdline.txt` file.")
            print("Please ensure proper `cmdline.txt` file is present in `/boot/`.")
            print()
    elif new_changes and error > 0:
        print()
        print("!!! ERROR !!! New Changes were attempted, but " + str(error) + " error(s) occurred.")
        print()
    elif not new_changes and error > 0:
        print()
        print("!!! ERROR !!! No Changes were attempted, but " + str(error) + " error(s) occurred.")
        print()
    else:
        print("No changes needed.")
        os.remove("/boot/cmd_temp.txt")
    print()
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
    print()
    print("Checking for I2C, SPI, and Serial settings...")
    with open("/boot/config.txt", "r") as f, open("/boot/config_temp.txt", "w") as f2:
        i2c = "dtparam=i2c_arm="
        spi = "dtparam=spi="
        serial = "enable_uart="
        new_changes = 0
        error = 0

        for line in f:
            li = line.strip()
            if (i2c in li) and not (li.startswith("#") or ("off" in li)):
                print("     ...I2C is already enabled, moving on...")
                if not f2.write(line) > 0:
                    print()
                    print("!!! ERROR !!! Error writing data (I2C param line). I2C was enabled.")
                    print()
                    error += 1
            elif (i2c in li) and (li.startswith("#") or ("off" in li)):
                print("Enabling I2C...")
                if f2.write(i2c + "on\n") > 0:
                    print("     ...I2C enabled.")
                    new_changes = 1
                else:
                    print()
                    print("!!! ERROR !!! Error writing new change (I2C param line). I2C was disabled.")
                    print()
                    error += 1
            elif (spi in li) and not (li.startswith("#") or ("off" in li)):
                print("     ...SPI is already enabled, moving on...")
                if not f2.write(line) > 0:
                    print()
                    print("!!! ERROR !!! Error writing data (SPI param line). SPI was enabled.")
                    print()
                    error += 1
            elif (spi in li) and (li.startswith("#") or ("off" in li)):
                print("Enabling SPI...")
                if f2.write(spi + "on\n") > 0:
                    print("     ...SPI enabled.")
                    new_changes = 1
                else:
                    print()
                    print("!!! ERROR !!! Error writing new change (SPI param line). SPI was disabled.")
                    print()
                    error += 1
            elif (serial in li) and not (li.startswith("#") or ("0" in li)):
                print("     ...Serial is already enabled, moving on...")
                if not f2.write(line) > 0:
                    print()
                    print("!!! ERROR !!! Error writing data (Serial param line). Serial was enabled.")
                    print()
                    error += 1
            elif (serial in li) and (li.startswith("#") or ("0" in li)):
                print("Enabling Serial...")
                if f2.write(serial + "1\n") > 0:
                    print("     ...Serial enabled.")
                    new_changes = 1
                else:
                    print()
                    print("!!! ERROR !!! Error writing new change (Serial param line). Serial was disabled.")
                    print()
                    error += 1
            else:
                if not f2.write(line) > 0:
                    print()
                    print("!!! ERROR !!! Error writing data (Any other param line).")
                    print()
                    error += 1

    if new_changes and not error:
        print("Exchanging \"config\" files...")
        os.remove("/boot/config.txt")
        os.rename("/boot/config_temp.txt", "/boot/config.txt")
        if os.path.isfile('/boot/config.txt'):
            print("     ...File exchange successful!")
        else:
            print()
            print("!!! ERROR !!! Issue occurred when trying to replace `config.txt` file.")
            print("Please ensure proper `config.txt` file is present in `/boot/`.")
            print()
    elif new_changes and error > 0:
        print()
        print("!!! ERROR !!! New Changes were attempted, but " + str(error) + " error(s) occurred.")
        print()
    elif not new_changes and error > 0:
        print()
        print("!!! ERROR !!! No Changes were attempted, but " + str(error) + " error(s) occurred.")
        print()
    else:
        print("No changes needed.")
        os.remove("/boot/config_temp.txt")
    print()
    print("---------------------------------------------------")
    print()
    print("\"config.txt\" setup COMPLETE!")
    print()
    print("---------------------------------------------------")
    print()


def configure_as_service():
    print()
    print("---------------------------------------------------")
    print()
    print("Configuring IHFRS to run automatically on restart...")
    print()
    print("---------------------------------------------------")
    print()
    print("Checking for `systemd` directory existence...")
    new_changes = 0
    error = 0

    if os.path.isdir('/etc/systemd/system'):
        print("     ...Success.")
        print("Checking for `IHFRS.service` file existence...")
        if not os.path.isfile('/etc/systemd/system/IHFRS.service'):
            print("Coping IHFRS service file...")
            os.system('cp init_files/IHFRS.service /etc/systemd/system/IHFRS.service')
            print("     ...Copy complete.")
            new_changes = 1
        else:
            print("     ...IHFRS.service already exists, moving on...")
        print("Enabling IHFRS as service...")
        out = os.popen('systemctl is-enabled IHFRS').read()
        if "enabled" in out:
            print("     ...IHFRS is already enabled, moving on...")
        elif "disabled" in out:
            os.system('systemctl enable IHFRS.service')
            out2 = os.popen('systemctl is-enabled IHFRS').read()
            if "enabled" in out2:
                print("     ...IHFRS was successfully enabled.")
                new_changes = 1
            elif "disabled" in out2:
                print()
                print("!!! ERROR !!! IHFRS was not successfully enabled.")
                print("Please manually enable later with `sudo systemctl enable IHFRS.`")
                print()
                error += 1
            else:
                print()
                print("!!! ERROR !!! `systemctl is-enabled IHFRS` returned abnormal response:")
                print("\" " + out2 + " \"")
                print()
                error += 1
        else:
            print()
            print("!!! ERROR !!! `systemctl is-enabled IHFRS` returned abnormal response:")
            print("\" " + out + " \"")
            print()
            error += 1
    else:
        print()
        print("!!! ERROR !!! Systemd directory is not where it is expected. Cannot add IHFRS as service at this time.")
        print()
        error += 1

    if new_changes and not error:
        print("Changes were successful.")
    elif new_changes and error > 0:
        print()
        print("!!! ERROR !!! New Changes were attempted, but " + str(error) + " error(s) occurred.")
        print()
    else:
        print("No changes needed.")
    print()
    print("---------------------------------------------------")
    print()
    print("IHFRS Service Configuration COMPLETE!")
    print()
    print("---------------------------------------------------")
    print()
