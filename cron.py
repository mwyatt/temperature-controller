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
import asyncio
from tapo import ApiClient

# load environment variables
load_dotenv('/home/martin/Sites/temperature-controller/TempProject/.env')

base_path = os.getenv('BASE_PATH')
db_name = base_path + os.getenv('DB_NAME')
tapo_username = str(os.getenv('TAPO_USERNAME'))
tapo_password = os.getenv('TAPO_PASSWORD')
tapo_ip_address = os.getenv('TAPO_HEATER_IP_ADDRESS')

# create a tapo api client
tapo_client = ApiClient(tapo_username, tapo_password)

async def turnHeaterOff():
    device = await tapo_client.p100(tapo_ip_address)
    await device.off()

async def turnHeaterOn():
    device = await tapo_client.p100(tapo_ip_address)
    await device.on()

con = sqlite3.connect(db_name)
cur = con.cursor()

# times
start_time = time.time()
run_time = 59
sleep_time = 5

# loop infinitely
while True:

    # get all settings stored
    cur.execute("SELECT * FROM tempapp_settings")
    settings = cur.fetchall()

    # get on and off temperatures
    on_temp = float(settings[0][2])
    off_temp = float(settings[1][2])

    # get current time
    current_time = time.strftime("%Y-%m-%d %H:%M:%S")
    
    # get current temperature from sensor
    current_temp = Path(os.getenv('TEMPERATURE_FILE_PATH')).read_text()
    current_temp = int(current_temp) / 1000 # 20.753
    current_temp = round(current_temp, 1) # 20.8

    # compare current temperature to target temperature
    heater_status = "on" if current_temp < on_temp else "off"
    heater_status = "off" if current_temp > off_temp else "on"

    # if heater should be on turn it on otherwise don't
    if heater_status == "on":
        asyncio.run(turnHeaterOn())

    if heater_status == "off":
        asyncio.run(turnHeaterOff())

    epoch_time = int(time.time())

    # store the results in the database
    cur.execute(
        """
        INSERT INTO tempapp_temphistory (current_temp, heater_on, time_created)
        VALUES (?, ?, ?)
        """,
        (current_temp, heater_status == "on", epoch_time)
    )

    con.commit()

    print(f"Current temp: {current_temp}, Heater Status: {heater_status}, On Temp: {on_temp}, Off Temp: {off_temp}, Time: {current_time}")

    time.sleep(sleep_time)
    
    # check if runtime has elapsed
    if time.time() - start_time >= run_time:
        break

