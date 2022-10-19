from functools import partial
from datetime import datetime

from nonebot import (
    on_message,
    on_notice,
)
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import (
    Bot,
    GroupMessageEvent,
    GroupUploadNoticeEvent,
)

from services.log import logger
from configs.config import Config
from utils.utils import scheduler, get_bot

from ..rule import (
    checkInboxMessage,
    checkInboxNotice,
)

from ..data_source import siyuan_manager
from ..API import (
    api,
    SiyuanAPIError,
    SiyuanAPIException,
)
from ..utils import (
    Download,
    eventBodyParse,
    getFileInfo,
    transferFile,
    createDoc,
    createTodayDoc,
    blockFormat,
    handle,
)

__zx_plugin_name__ = "思源收集箱 [Hidden]"

__plugin_des__ = "将群里所有消息都发送到指定"

__plugin_version__ = 0.3
__plugin_author__ = "Zuoqiu-Yingyi"

__plugin_type__ = ('思源笔记', 1)

# 群消息
inbox_message = on_message(
    priority=1,
    block=True,
    rule=checkInboxMessage,
)

# 群文件上传
inbox_upload = on_notice(
    priority=1,
    block=True,
    rule=checkInboxNotice,
)

SIYUAN_URL = Config.get_config("siyuan", "SIYUAN_URL")


# 定时任务
@scheduler.scheduled_job(
    "cron",
    hour=0,
    minute=0,
    second=1,
)
async def _():
    try:
        error_info = None
        bot = get_bot()
        for group_id, config in siyuan_manager.inbox_list.items():
            # 获取该收集箱路径 -> 获取可读路径 -> 新建文档 -> 更新文档 ID
            doc_id, title = await createDoc(
                notebook=config.get('box'),
                path=config.get('path'),
            )
            await siyuan_manager.updateParentID(group_id=group_id, doc_id=doc_id)

            message = f"收集箱 {group_id} 新建文档 {title} 成功 {SIYUAN_URL}/stage/build/desktop/?id={doc_id}"
    except SiyuanAPIException as e:
        error_info = f"思源 API 内核错误 e: {e.msg}"
    except SiyuanAPIError as e:
        error_info = f"思源 API HTTP 响应错误 e: {e}"
    except Exception as e:
        error_info = f"群消息处理错误 e: {e}"
    else:
        await bot.send_msg(
            user_id=int(list(bot.config.superusers)[0]),
            message=message,
        )
        logger.info(message)
    finally:
        if error_info is not None:
            await bot.send_msg(
                user_id=int(list(bot.config.superusers)[0]),
                message=error_info,
            )
            logger.error(error_info)


async def createDocOnTime(group_id: str):
    """
    :说明:
        根据时间判断是否需要新建文档
    :参数:
        group_id: 群号
    """
    try:
        error_info = None
        bot = get_bot()

        box, path, _, parentID, _, _ = siyuan_manager.getInboxInfo(group_id=group_id)
        # 获取思源系统时间 -> 获取配置文件中当前文档创建时间 -> 比较时间, 若不一致则新建文档并更新配置文件中的文档 ID
        now = datetime.fromtimestamp(float((await api.post(url=api.url.currentTime)).data) / 1000)
        current = datetime.strptime(parentID[:14], '%Y%m%d%H%M%S')
        r = await createTodayDoc(notebook=box, path=path, now=now, current=current)
        if r is not None:
            doc_id, title = r
            await siyuan_manager.updateParentID(group_id=group_id, doc_id=doc_id)
            message = f"收集箱 {group_id} 新建文档 {title} 成功 {SIYUAN_URL}/stage/build/desktop/?id={doc_id}"
            await bot.send_msg(
                user_id=int(list(bot.config.superusers)[0]),
                message=message,
            )
            logger.info(message)
    except SiyuanAPIException as e:
        error_info = f"思源 API 内核错误 e: {e.msg}"
    except SiyuanAPIError as e:
        error_info = f"思源 API HTTP 响应错误 e: {e}"
    except Exception as e:
        error_info = f"群消息处理错误 e: {e}"
    finally:
        if error_info is not None:
            await bot.send_msg(
                user_id=int(list(bot.config.superusers)[0]),
                message=error_info,
            )
            logger.error(error_info)


# 群文件
@inbox_upload.handle()
async def _(bot: Bot, event: GroupUploadNoticeEvent, state: T_State):
    try:
        error_info = None
        event_body = await eventBodyParse(event.json())
        group_id = str(event_body.get('group_id'))  # 群号

        _, _, uploadPath, parentID, enable, is_reply = siyuan_manager.getInboxInfo(group_id=group_id)

        if not enable: # 收集功能已关闭
            return

        await createDocOnTime(group_id)
        _, id, name, _, url = await getFileInfo(event_body)
        file = await transferFile(
            downloadFunc=partial(
                Download.file,
                url=url,
                id=id,
                name=name,
            ),
            uploadPath=uploadPath,
        )

        for k, v in file.items():
            data = await blockFormat(
                message=f"[{k}]({v})",
                event=event_body,
                is_message=False,
            )
            print(data)
            r = await api.post(
                url=api.url.appendBlock,
                body={
                    'parentID': parentID,
                    'dataType': "markdown",
                    'data': data,
                },
            )
            reply = f"""{k}:
{SIYUAN_URL}/stage/build/desktop/?id={r.data[0]['doOperations'][0]['id']}
{SIYUAN_URL}/{v}
{url}"""
            break
    except SiyuanAPIException as e:
        error_info = f"思源 API 内核错误 e: {e.msg}"
    except SiyuanAPIError as e:
        error_info = f"思源 API HTTP 响应错误 e: {e}"
    except Exception as e:
        error_info = f"群消息处理错误 e: {e}"
    else:
        if is_reply: # 开启消息回复, 则直接在群中回复处理结果
            await inbox_upload.send(reply)
        logger.info(reply)
    finally:
        if error_info is not None:
            if is_reply: # 开启消息回复, 则直接在群中回复错误信息
                await inbox_upload.send(error_info)
            else: # 否则在私聊中回复错误信息
                await bot.send_msg(
                    user_id=int(list(bot.config.superusers)[0]),
                    message=error_info,
                )
            logger.error(error_info)


# 群消息
@inbox_message.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    try:
        error_info = None
        event_body = await eventBodyParse(event.json())
        group_id = str(event_body.get('group_id'))  # 群号

        _, _, uploadPath, parentID, enable, is_reply = siyuan_manager.getInboxInfo(group_id=group_id)

        if not enable: # 收集功能已关闭
            return

        await createDocOnTime(group_id)
        have_text = False  # 是否有文本信息
        messages = []

        reply = event_body.get('reply')
        if reply is not None:
            messages.append(await handle(
                t='reply',
                reply=reply,
            ))

        for msg in event_body.get('message'):
            msg_type = msg.get('type')
            if not have_text and msg_type == 'text':
                have_text = True
            messages.append(await handle(
                t=msg_type,
                data=msg.get('data'),
                uploadPath=uploadPath,
                bot=bot,
            ))

        data = await blockFormat(
            message=''.join(messages),
            event=event_body,
            have_text=have_text,
        )
        print(data)
        r = await api.post(
            url=api.url.appendBlock,
            body={
                'parentID': parentID,
                'dataType': "markdown",
                'data': data,
            },
        )
        reply = f"{SIYUAN_URL}/stage/build/desktop/?id={r.data[0]['doOperations'][0]['id']}"
    except SiyuanAPIException as e:
        error_info = f"思源 API 内核错误 e: {e.msg}"
    except SiyuanAPIError as e:
        error_info = f"思源 API HTTP 响应错误 e: {e}"
    except Exception as e:
        error_info = f"群消息处理错误 e: {e}"
    else:
        if is_reply: # 开启消息回复, 则直接在群中回复处理结果
            await inbox_message.send(reply)
        logger.info(reply)
    finally:
        if error_info is not None:
            if is_reply: # 开启消息回复, 则直接在群中回复错误信息
                await inbox_message.send(error_info)
            else: # 否则在私聊中回复错误信息
                await bot.send_msg(
                    user_id=int(list(bot.config.superusers)[0]),
                    message=error_info,
                )
            logger.error(error_info)
