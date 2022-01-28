from pathlib import Path
from typing import Optional

from configs.path_config import DATA_PATH
from configs.config import Config

from .model import SiyuanManager
from .API import API

siyuan_manager: Optional[SiyuanManager] = SiyuanManager(
    Path(DATA_PATH) / "siyuan.json",
)

siyuan_api: Optional[API] = API(
    token=Config.get_config("siyuan", "SIYUAN_TOKEN"),
    host=Config.get_config("siyuan", "SIYUAN_HOST"),
    port=Config.get_config("siyuan", "SIYUAN_PORT"),
    ssl=Config.get_config("siyuan", "SIYUAN_SSL"),
)
