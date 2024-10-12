#!/usr/bin/env python3

import os
import json
import sqlite3
import time
from calendar import timegm
import sys
from dotenv import load_dotenv

load_dotenv()

# ???
sys.path.append('/home/martin/Sites/temperature-controller/')

con = sqlite3.connect(os.getenv('DB_NAME'))
cur = con.cursor()

# get query string
query_string = os.getenv("QUERY_STRING")
start_date_input = ""
end_date_input = ""

default_last_seconds = 60 * 10
if query_string == "latest=true":
    default_last_seconds = 5

epoch_now = int(time.time())
epoch_time_start = epoch_now - default_last_seconds
epoch_time_end = epoch_now

# if query_string is null
if query_string != "" and query_string != "latest=true":
    query_string = query_string.split("&")
    start_date_input = query_string[0].split("=")[1]
    end_date_input = query_string[1].split("=")[1]

if start_date_input != "":
    utc_time = time.strptime(start_date_input, "%Y-%m-%dT%H:%M")
    epoch_time_start = timegm(utc_time)

if end_date_input != "":
    utc_time = time.strptime(end_date_input, "%Y-%m-%dT%H:%M")
    epoch_time_end = timegm(utc_time)

# get temp history
cur.execute("SELECT * FROM temp_history WHERE timestamp BETWEEN ? AND ?", (epoch_time_start, epoch_time_end))

temp_history = cur.fetchall()

def convert_epoch_to_string(x):
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(x[3]))

time_history = list(map(convert_epoch_to_string, temp_history))
temperature_history = list(map(lambda x: x[1], temp_history))

output = json.dumps({
    "labels": time_history,
    "data": temperature_history,
    "dataHeater": list(map(lambda x: 1 if x[2] == 1 else 0, temp_history))
})

print(
    f"""\
Content-Type: application/json

{output}

"""
)