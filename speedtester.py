#!/usr/bin/env python

"""Speed tester
This module checks your internet speed periodically, tells it to you and saves
it to a file.
Tested with Python 3.9.2 & 3.10.5 on Debian & Fedora respectively.
Text to voice only works with Debian for now.
"""

import this
import time
import os
import sys
import subprocess
import json
from datetime import datetime


MINUTES = 60


def distro():
    os = input('What is your operating system? arch/debian/fedora: ')
    while os != 'arch' and os != 'debian' and os != 'fedora':
        os = input('What is your operating system? arch/debian/fedora: ')
    return os


def install_pip():
    os = distro() # cannot have the same name
    print(os)
    if os == 'debian':
        subprocess.run(['sudo', 'apt', 'install', '-y', 'pip'],
        check=True)
        import pip
    elif os == 'fedora':
        subprocess.run(['sudo', 'dnf', 'install', '-y', 'pip'],
        check=True)
        import pip
    elif os == 'arch':
        pass
    else:
        print('unknown distro, exiting...')


def install_system_package(package_name):
    install_pip_package('distro')
    import distro
    dst = distro.id()
    dst_like = distro.like()
    if dst == 'debian' or dst_like == 'debian':
        subprocess.run(['sudo', 'apt', 'install', '-y', package_name],
        check=True)
    elif dst == 'fedora' or dst_like == 'fedora':
        subprocess.run(['sudo', 'dnf', 'install', '-y', package_name],
        check=True)
    elif dst == 'arch' or dst_like == 'arch':
        subprocess.run(['sudo', 'pacman', '-S', '-y', package_name],
        check=True)
    else:
        print('unknown distro, exiting...')


def install_pip_package(package_name):
    subprocess.check_call([sys.executable, '-m', 'pip', 'install',
    package_name])


def install_pip_package_v2(package_name):
    pip.main(['install', package_name])


def main():
    try:
        import pip
    except ModuleNotFoundError as error:
        print(error)
        install_pip()
    finally:
        import pip

    install_pip_package('webdriver-manager')

    try:
        # selenium 4
        from selenium import webdriver
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.common.by import By
        from selenium.common.exceptions import TimeoutException
        from selenium.webdriver.firefox.service import Service as FirefoxService
        from selenium.webdriver.firefox.options import Options as FirefoxOptions
        from webdriver_manager.firefox import GeckoDriverManager
    except ModuleNotFoundError as error:
        print(error)
        install_pip_package('selenium')
        # even importlib module did not help, I have to restart it completely
        os.execl(sys.executable, sys.executable, *sys.argv)
        # print('Selenium is installed. Please re-run the program.')
        # sys.exit()

    if sys.platform == 'linux':
        # linux
        install_system_package('speech-dispatcher')
        options = FirefoxOptions()
        options.add_argument('--headless')
        driver = webdriver.Firefox(service=FirefoxService(
        GeckoDriverManager().install()
        ), options=options)

        driver.get('https://librespeed.org')
        delay = 20 #  seconds
        try:
            myElem = WebDriverWait(driver, delay).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="startStopBtn"]')))
            # EC.presence_of_element_located((By.XPATH, '//*[@id="startStopBtn"]')))
            # print("Button is ready!")
        except TimeoutException:
            print("Loading took too much time!")

        while True:
            driver.find_element(By.XPATH, '//*[@id="startStopBtn"]').click()
            # print(driver.find_element(By.XPATH, '//*[@id="dlText"]').text)
            time.sleep(10) #  wait a little bit for the test to start
            last_speed = -1
            speed = 0
            while last_speed != speed:
                speed = driver.find_element(By.XPATH, '//*[@id="dlText"]').text
                # print(speed)
                temp = speed
                time.sleep(1)
                speed = driver.find_element(By.XPATH, '//*[@id="dlText"]').text
                last_speed = temp
            speed = speed.split('.')[0] #  get the first part before the point
            speed_text = f'Your internet speed is {speed} megabits.'
            os.system('spd-say "'+ speed_text + '"')
            data = dict()
            # check if file exists
            try:
                with open('speed.json', 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except FileNotFoundError:
                print('Creating the file..')
            dt = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
            data[dt] = speed
            with open('speed.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                print('File updated', dt, '\n', speed_text)
            time.sleep(MINUTES * 60)

    elif sys.platform == 'darwin':
        # macOS
        os.system('say "not implemented"')
    elif sys.platform == 'win32':
        print('not implemented')

if __name__ == '__main__':
    print()
    i = input('pip, selenium, webdriver-manager, their dependencies, and '
    'speech-dispatcher (if on Debian and derivatives) will be installed. '
    ' Continue? Y/N: ').lower()
    if i == 'y':
        mins = input('Check every ? minutes? (enter a number): ')
        try:
            MINUTES = int(mins)
        except ValueError:
            print('Invalid value, using 60 minutes as default.')
        if MINUTES > 0:
            main()


