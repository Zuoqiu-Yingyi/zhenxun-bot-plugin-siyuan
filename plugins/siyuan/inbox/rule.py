from nonebot.typing import T_State
from nonebot.adapters.cqhttp import (
    Bot,
    Event,
    GroupMessageEvent,
    GroupUploadNoticeEvent,
)

from ..data_source import siyuan_manager


async def checkInboxMessage(bot: Bot, event: Event, state: T_State) -> bool:
    if isinstance(event, GroupMessageEvent):
        return bool(siyuan_manager.isInInboxList(group_id=str(event.group_id)))
    return False


async def checkInboxNotice(bot: Bot, event: Event, state: T_State) -> bool:
    if isinstance(event, GroupUploadNoticeEvent):
        return bool(siyuan_manager.isInInboxList(group_id=str(event.group_id)))
    return False
