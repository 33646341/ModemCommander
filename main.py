import asyncio
import logging

import aiohttp
import telnetlib3
import yaml


async def telnet_password(host, port, username, password, file_path, pattern):
    reader, writer = await telnetlib3.open_connection(host, port)

    try:
        await reader.readuntil(b"login: ")
        writer.write(username + "\n")
        await reader.readuntil(b"Password: ")
        writer.write(password + "\n")
        await reader.readuntil(b"$ ")
        command = "awk -F'\"' '/" + pattern + "/ {print $4}' " + file_path + "\n"
        writer.write(command)
        output = await reader.readuntil(b"$ ")
        line = output.splitlines()[-2]
        return line.decode("utf-8").strip()

    finally:
        writer.close()


def load_config():
    global HOST, PORT, USERNAME, PASSWORD, FILE_PATH, PATTERN

    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)
    HOST = config["host"]
    PORT = config["port"]
    USERNAME = config["username"]
    PASSWORD = config["password"]
    FILE_PATH = config["file_path"]
    PATTERN = config["pattern"]


async def open_telnet(host, port):
    url = f"http://{host}/boaform/set_telnet_enabled_url.cgi"
    data = {
        "mode_name": "/boaform/set_telnet_enabled_url",
        "telnet_port": port,
        "telnet_lan_enabled": "1",
        "telnet_wan_enabled": "0",
        "default_flag": "1",
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, data=data) as response:
            logging.debug(f"Status: {response.status}")
            logging.debug(await response.text())


async def main():
    load_config()
    await open_telnet(HOST, PORT)
    password = await telnet_password(HOST, PORT, USERNAME, PASSWORD, FILE_PATH, PATTERN)
    print(f"Password: {password}")


if __name__ == "__main__":
    asyncio.run(main())
