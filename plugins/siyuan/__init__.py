import nonebot

from pathlib import Path
from typing import Optional
from configs.path_config import DATA_PATH

from .model import SiyuanManager

siyuan_manager: Optional[SiyuanManager] = SiyuanManager(
    Path(DATA_PATH) / "siyuan.json",
)

from configs.config import Config

Config.add_plugin_config(
    module="siyuan",
    key="SIYUAN_HOST",
    value=None,
    name="主机名",
    help_="思源笔记内核所在主机名",
    # default_value="localhost",
    # _override=True,
)

Config.add_plugin_config(
    module="siyuan",
    key="SIYUAN_PORT",
    value=None,
    name="端口号",
    help_="思源笔记内核监听端口",
    # default_value="6806",
    # _override=True,
)

Config.add_plugin_config(
    module="siyuan",
    key="SIYUAN_SSL",
    value=None,
    name="启用 SSL",
    help_="思源笔记是否启用 SSL",
    # default_value=False,
    # _override=True,
)

Config.add_plugin_config(
    module="siyuan",
    key="SIYUAN_TOKEN",
    value=None,
    name="Token",
    help_="思源笔记 API Token",
    # default_value="0123456789ABCDEF",
    # _override=True,
)

Config.add_plugin_config(
    module="siyuan",
    key="SIYUAN_URL",
    value=None,
    name="URL",
    help_="思源笔记 URL",
    # default_value="http://localhost:6806",
    # _override=True,
)

# nonebot.load_plugins("plugins/siyuan")
nonebot.load_plugins("plugins/siyuan/inbox")
