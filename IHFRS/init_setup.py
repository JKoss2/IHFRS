# Run this file to set up the device defaults for IHFRS.
import os
import sys
from init_files import dev_setup_lib

if os.getuid():
    sys.exit('You need root access to install')

os.system('clear')
print()
print()
print("###################################")
print("#####  Initial Setup  #####")
print("###################################")
print()
print()
install_ans = input("Are you ready to commit changes to the system? [y/N]: ")

if install_ans.lower() == 'y':
    dev_setup_lib.install_prereqs()
    dev_setup_lib.configure_initial_settings()


else:
    print()
    print()
    print("===================================================")
    print("---------------------------------------------------")
    print()
    print("Installation cancelled. Nothing changed...")
    print()
    print("---------------------------------------------------")
    print("===================================================")
    print()
    print()
    sys.exit()

os.system('clear')
print()
print()
print("#####################################")
print("#####  Setup Complete  #####")
print("#####################################")
print()
print()
print("Initial setup is complete. A reboot is required to start in WiFi configuration mode...")
reboot_ans = input("Would you like to do that now? [y/N]: ")

if reboot_ans.lower() == 'y':
    os.system('reboot')
