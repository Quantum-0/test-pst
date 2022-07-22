#!/usr/bin/python3

import platform
import sys
import os
import glob
from colorama import init, Fore

init(autoreset=True)

if __name__ == '__main__':
    print(Fore.BLUE + 'Welcome to python service uninstallation script made by Quantum0')

    print('Check OS as Linux: ', end='')
    if platform.system() != 'Linux':
        print(Fore.RED + "FAIL")
        exit(1)
    print(Fore.GREEN + "OK")

    print('Check running on root: ', end='')
    if os.getuid() != 0:
        print(Fore.RED + "FAIL")
        exit(2)
    print(Fore.GREEN + "OK")

    print('Check we are in /opt : ', end='')
    if os.path.abspath(__file__).startswith('/opt/'):
        print(Fore.RED + "FAIL")
        exit(3)
    print(Fore.GREEN + "OK")

    working_dir = '/'.join(os.path.abspath(__file__).split('/')[:-2])

    print('Search for .service : ', end='')
    os.chdir(working_dir)
    search = glob.glob("*.service")
    if len(search) != 1:
        print(Fore.RED + "FAIL")
        exit(4)
    service_file = search[0]
    service_name = service_file[:-8]
    print(Fore.GREEN + "OK")

    print('Stopping and disabling service: ', end='')
    if os.system(f'systemctl stop {service_name} && systemctl disable {service_name}') != 0:
        print(Fore.RED + "FAIL")
        exit(5)
    print(Fore.GREEN + "OK")

    print('Removing symlink in /etc/systemd/system/: ', end='')
    if os.system(f'rm /etc/systemd/system/{service_name}.service') != 0:
        print(Fore.RED + "FAIL")
        exit(6)
    print(Fore.GREEN + "OK")

    print('Reloading systemctl: ', end='')
    if os.system(f'systemctl daemon-reload') != 0:
        print(Fore.RED + "FAIL")
        exit(7)
    print(Fore.GREEN + "OK")

    print(Fore.BLUE + 'Service is uninstalled.')
