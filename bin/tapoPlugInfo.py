"""P100 and P105 Example"""

import asyncio
import os

from tapo import ApiClient


async def main():
    # todo get from env
    tapo_username = ""
    tapo_password = ""
    ip_address = ""

    client = ApiClient(tapo_username, tapo_password)
    device = await client.p100(ip_address)

    print("Turning device on...")
    await device.on()

    device_info = await device.get_device_info()
    print(f"Device info: {device_info.to_dict()}")

    device_usage = await device.get_device_usage()
    print(f"Device usage: {device_usage.to_dict()}")
    print("Waiting 2 seconds...")
    await asyncio.sleep(2)

    print("Turning device off...")
    await device.off()


asyncio.run(main())