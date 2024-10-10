#!/usr/bin/env python3

import os
import json
import sqlite3
import sys

sys.path.append('/home/martin/Sites/temperature-controller/')
from constants import *

con = sqlite3.connect(DB_NAME)
cur = con.cursor()

# get query string
query_string = os.getenv("QUERY_STRING")
query_string = query_string.split("&")
target_temp = query_string[0].split("=")[1]
buffer_temp = query_string[1].split("=")[1]

cur.execute(
    """
    UPDATE settings
    SET value = ?
    WHERE key = 'target_temp'
    """,
    (str(target_temp),)
)

cur.execute(
    """
    UPDATE settings
    SET value = ?
    WHERE key = 'buffer_temp'
    """,
    (str(buffer_temp),)
)

con.commit()

output = json.dumps(1)

print(
    f"""\
Content-Type: application/json

{output}

"""
)