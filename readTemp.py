# remove me

from pathlib import Path
from inspect import getmembers
from pprint import pprint

temp = Path('/sys/bus/w1/devices/28-3ce10457e721/temperature').read_text()
temp = int(temp) / 1000
temp = round(temp, 1)

print(temp)
