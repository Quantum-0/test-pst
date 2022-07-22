#!/usr/bin/python3

import platform
import sys
import os
from colorama import init, Fore

init(autoreset=True)

if __name__ == '__main__':
    print(Fore.BLUE + 'Welcome to python service installation script made by Quantum0')

    print('Check OS is Linux: ', end='')
    if platform.system() != 'Linux':
        print(Fore.RED + "FAIL")
        exit(1)
    print(Fore.GREEN + "OK")

    print('Check running as root: ', end='')
    if os.getuid() != 0:
        print(Fore.RED + "FAIL")
        exit(2)
    print(Fore.GREEN + "OK")

    print('Check we are in /opt : ', end='')
    if not os.path.abspath(__file__).startswith('/opt/'):
        print(Fore.RED + "FAIL")
        exit(3)
    print(Fore.GREEN + "OK")

    # print('Check run from venv : ', end='')
    # if not 'venv' in sys.executable:
    #     print(Fore.RED + "FAIL")
    #     exit(4)
    # print(Fore.GREEN + "OK")

    working_dir = '/'.join(os.path.abspath(__file__).split('/')[:-2])

    print('Installing venv and requirements: ', end='')
    if (
        os.system(
            f'cd {working_dir} && '
            f'pip install virtualenv > /dev/null && '
            f'virtualenv venv > /dev/null && '
            f'. venv/bin/activate > /dev/null && '
            f'pip install -r requirements.txt > /dev/null'
        )
        != 0
    ):
        print(Fore.RED + "FAIL")
        exit(5)
    print(Fore.GREEN + "OK")

    print('Enter the service name or leave empty for default: ', end='')
    service_name = input()
    if service_name == '':
        service_name = os.path.abspath(__file__).split('/')[-3]
    print('Service name: ' + Fore.BLUE + service_name)
    print('Working dir is: ' + Fore.BLUE + working_dir)

    print('Generating service file: ', end='')

    # user = pwd.getpwuid(os.getuid())[0]
    user = os.environ['SUDO_USER']

    service_file = f'''[Unit]
    Description={service_name}
    After=network.target

    [Service]
    Type=simple
    WorkingDirectory={working_dir}
    User={user}
    Restart=on-failure
    ExecStart={sys.executable} {working_dir}/src/main.py
    EnvironmentFile={working_dir}/.env
    StandardOutput=/var/log/{service_name}.output.log
    StandardError=/var/log/{service_name}.error.log

    [Install]
    WantedBy=multi-user.target
    '''
    print(Fore.GREEN + "OK")
    print('Saving .service file: ', end='')
    try:
        with open(f'{working_dir}/{service_name}.service', 'w+') as f:
            f.write(service_file)
        print(Fore.GREEN + "OK")
    except:
        print(Fore.RED + "FAIL")
        exit(6)

    print('Creating symlink in /etc/systemd/system/: ', end='')
    if os.system(f'ln -s {working_dir}/{service_name}.service /etc/systemd/system/{service_name}.service') != 0:
        print(Fore.RED + "FAIL")
        exit(7)
    print(Fore.GREEN + "OK")

    print('Reloading systemctl: ', end='')
    if os.system(f'systemctl daemon-reload') != 0:
        print(Fore.RED + "FAIL")
        exit(8)
    print(Fore.GREEN + "OK")

    print('Enabling service: ', end='')
    if os.system(f'systemctl enable {service_name}') != 0:
        print(Fore.RED + "FAIL")
        exit(9)
    print(Fore.GREEN + "OK")

    print('Creating .env file: ', end='')
    try:
        with open(f'{working_dir}/.env', 'w+') as f:
            f.write('# TODO: Fill with environment variables\n\n')
            f.write('TEST_ENV=1\nPYTHONUNBUFFERED=1')
        print(Fore.GREEN + "OK")
    except:
        print(Fore.RED + "FAIL")
        exit(10)

    print(Fore.BLUE + 'Service is installed.\nNow you can start it with:\n>', end='')
    print(Fore.GREEN + f'systemctl start {service_name}')

    # Check for flask
    with open(f'{working_dir}/requirements.txt', 'r') as f:
        req_data = f.read()
    if 'flask' not in req_data and 'Flask' not in req_data:
        exit(0)

    print('\n\nFlask was found in the project')
    with open(f'{working_dir}/src/main.py', 'r') as f:
        main_text = f.read()
    if 'Flask' in main_text:
        import re

        flask_match = re.search(r"(\w+) ?= ?Flask.*\1\.run\(.*port=(\d+).*\)", main_text, flags=re.S)
        if flask_match:
            flask_port = flask_match.group(2)
            print('Port: ' + Fore.GREEN + flask_port)
        else:
            print('Cannot find port automatically, please define it: ', end='')
            flask_port = input()
    print('Hostname: ', end='')
    flask_hostname = input()
    with open(f'{working_dir}/install/nginx.template', 'r') as f:
        nginx_template = f.read()
    with open(f'{working_dir}/nginx-config', 'w+') as f:
        f.write(
            nginx_template.replace('%HOSTNAME%', flask_hostname)
            .replace('%PORT%', flask_port)
            .replace('%SERVICENAME%', service_name)
        )
    os.system(f'ln -s {working_dir}/nginx-config /etc/nginx/sites-available/{flask_hostname}')
    os.system(f'ln -s {working_dir}/nginx-config /etc/nginx/sites-enabled/{flask_hostname}')
    os.system('systemctl restart nginx')
    print('Nginx config file generated')
    exit(0)
