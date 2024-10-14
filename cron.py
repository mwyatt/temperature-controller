# exit('cron is off')

import os
import time
import pickle
import sqlite3
from pathlib import Path
from inspect import getmembers
from pprint import pprint
import importlib.util
from dotenv import load_dotenv

load_dotenv()

# check if running in rasberry pi environment
RPi_spec = importlib.util.find_spec("RPi")
is_rasberry_pi_enviroment = RPi_spec != None
if is_rasberry_pi_enviroment:
    import RPi.GPIO as GPIO
    GPIO.setwarnings(False)

con = sqlite3.connect(os.getenv('DB_NAME'))
cur = con.cursor()

# get start time
start_time = time.time()

run_time = 59
sleep_time = 5
heater_gpio_pin = int(os.getenv('CERAMIC_HEATER_GPIO_PIN'))

# loop infinitely
while True:

    # get all settings stored
    cur.execute("SELECT * FROM settings")
    settings = dict(cur.fetchall())

    # get current time
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # get target temperature
    target_temp = int(settings["target_temp"])
    
    # get current temperature
    # current_temp = float(settings['current_temp'])

    # get current temperature from sensor
    current_temp = Path(os.getenv('TEMPERATURE_FILE_PATH')).read_text()
    current_temp = int(current_temp) / 1000 # 20.753
    current_temp = round(current_temp, 1) # 20.8

    # compare current temperature to target temperature
    heater_status = "on" if current_temp < target_temp else "off"
    # print(heater_status)

    if heater_status == "on" and is_rasberry_pi_enviroment:
        GPIO.setup(heater_gpio_pin, GPIO.OUT)

    # if heater is on increment otherwise decrement
    # current_temp += 1 if heater_status == "on" else -1

    # if heater should be on turn it on otherwise don't
    if is_rasberry_pi_enviroment:
        GPIO.setmode(GPIO.BCM)
        GPIO.output(heater_gpio_pin, True if heater_status == "on" else False)
        if GPIO.input(heater_gpio_pin) == 0:
            GPIO.cleanup()

    epoch_time = int(time.time())

    # store the results in the database
    cur.execute(
        """
        INSERT INTO temp_history (current_temp, heater_on, timestamp)
        VALUES (?, ?, ?)
        """,
        (current_temp, heater_status == "on", epoch_time)
    )

    # store current temp setting
    cur.execute(
        """
        UPDATE settings
        SET value = ?
        WHERE key = 'current_temp'
        """,
        (str(current_temp),)
    )

    con.commit()

    print(f"Current temp: {current_temp}, Heater: {heater_status}, Time: {current_time}, Target: {target_temp}")

    time.sleep(sleep_time)
    
    # check if runtime has elapsed
    if time.time() - start_time >= run_time:
        break

