import asyncio
import json

import aiohttp
import telnetlib3
from loguru import logger

from config import load_config
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
            await open_telnet(host, port)

    if reader is None or writer is None:
        raise ConnectionRefusedError(
            f"Failed to connect to {host}:{port}, please check the configuration."
        )

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


async def open_telnet(host: str, port: int):
    url = f"http://{host}/boaform/set_telnet_enabled_url.cgi"
    data: dict[str, str] = {
        "mode_name": "/boaform/set_telnet_enabled_url",
        "telnet_port": str(port),
        "telnet_lan_enabled": "1",
        "telnet_wan_enabled": "0",
        "default_flag": "1",
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            logger.trace(json.loads(await response.text()))
            if response.status != 200:
                raise ValueError(f"Failed to enable Telnet on {host}:{port}")


async def login(host: str, password: str):
    url = f"http://{host}/boaform/web_login_exe.cgi"
    data: dict[str, str] = {
        "mode_name": "/boaform/web_login_exe",
        "web_login_name": "CMCCAdmin",
        "web_login_password": encrypt_password(password),
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=data) as response:
            logger.trace(json.loads(await response.text()))
            if response.status != 200:
                raise ValueError(f"Failed to login to {host}")
            return response.headers.get("token")


@logger.catch
async def main():
    logger.add(
        "debug.log", rotation="1 MB", level="TRACE", backtrace=True, diagnose=True
    )
    c = load_config()
    password = await telnet_password(
        c.host, c.port, c.username, c.password, c.file_path, c.pattern
    )
    logger.success(f"Password: {password}")
    token = await login(c.host, password)
    logger.success(f"Token: {token}")
    logger.info(
        f"You can now visit http://{c.host}/webcmcc/index_content.html without authentication :)"
    )


if __name__ == "__main__":
    asyncio.run(main())
