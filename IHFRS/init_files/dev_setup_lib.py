import os


def install_prereqs():
    os.system('clear')
    os.system('apt update')
    os.system('clear')
    print("Installing pre-requisites...")
    os.system('apt install python3 python3-rpi.gpio python3-pip python3-pil python3-pil.imagetk dnsmasq hostapd '
              'libavahi-compat-libdnssd-dev -y')
    os.system('clear')
    os.system('pip3 install flask pyopenssl HAP-python[QRCode]')
    os.system('clear')

    print("Install complete.")


def configure_initial_settings():
    os.system('sudo cp /boot/config.txt /boot/config.txt.bak')
    os.system('sudo cp /boot/cmdline.txt /boot/cmdline.txt.bak')
    os.system('sudo cp init_files/boot_config_init.txt /boot/config.txt')
    os.system('sudo cp init_files/cmdline_config_init.txt /boot/cmdline.txt')


def install_prereqs():
    os.system('clear')
    os.system('apt update')
    os.system('clear')
    os.system('apt install python3 python3-rpi.gpio python3-pip dnsmasq hostapd -y')
    os.system('clear')
    print("Installing Flask web server...")
    print()
    os.system('pip3 install flask pyopenssl')
    os.system('clear')



