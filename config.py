import yaml
from pydantic import BaseModel, PositiveInt


class Config(BaseModel):
    host: str = "192.168.1.1"
    port: PositiveInt = 23
    username: str = "user"
    password: str
    file_path: str = "/config/workb/backup_lastgood.xml"
    pattern: str = "aucTeleAccountPassword"


def load_config():
    with open("config.yaml", "r") as file:
        raw_config = yaml.safe_load(file)
    config = Config(**raw_config)
    return config
