import asyncio
import json
import sys

import aiohttp
import telnetlib3
import yaml
from loguru import logger

from crypto import encrypt_password


async def telnet_password(
    host: str, port: int, username: str, password: str, file_path: str, pattern: str
) -> str:
    reader = writer = None

    for _ in range(2):
        try:
            reader, writer = await telnetlib3.open_connection(host, port)
            break
        except ConnectionRefusedError:
            logger.warning(
                f"Connection to {host}:{port} refused. Try enabling Telnet..."
            )
            await open_telnet(HOST, PORT)

    if reader is None or writer is None:
        logger.error(
            f"Failed to connect to {host}:{port}, please check the configuration."
        )
        exit(1)

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


async def open_telnet(host: str, port: str):
    url = f"http://{host}/boaform/set_telnet_enabled_url.cgi"
    data: dict[str, str] = {
        "mode_name": "/boaform/set_telnet_enabled_url",
        "telnet_port": port,
        "telnet_lan_enabled": "1",
        "telnet_wan_enabled": "0",
        "default_flag": "1",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            logger.debug(json.loads(await response.text()))
            if response.status != 200:
                logger.error(f"Failed to enable Telnet on {host}:{port}")
                exit(1)


async def login(host: str, password: str):
    url = f"http://{host}/boaform/web_login_exe.cgi"
    data: dict[str, str] = {
        "mode_name": "/boaform/web_login_exe",
        "web_login_name": "CMCCAdmin",
        "web_login_password": encrypt_password(password),
    }

    async with aiohttp.ClientSession() as session:
        async with session.get(url, data=data) as response:
            logger.debug(json.loads(await response.text()))
            if response.status != 200:
                logger.error(f"Failed to login to {host}")
                exit(1)
            return response.headers.get("token")


async def main():
    logger.remove()
    logger.add("debug.log", rotation="1 MB", level="DEBUG")
    logger.add(sys.stdout, level="WARNING")
    load_config()
    password = await telnet_password(HOST, PORT, USERNAME, PASSWORD, FILE_PATH, PATTERN)
    print(f"Password: {password}")
    token = await login(HOST, password)
    print(f"Token: {token}")
    print(
        f"You can now visit http://{HOST}/webcmcc/index_content.html without authentication :)"
    )


if __name__ == "__main__":
    asyncio.run(main())
