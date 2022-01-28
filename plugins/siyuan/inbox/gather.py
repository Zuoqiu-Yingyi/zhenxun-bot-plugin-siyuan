from functools import partial

from nonebot import (
    on_message,
    on_notice,
)
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import (
    Bot,
    GroupMessageEvent,
    GroupUploadNoticeEvent,
)

from services.log import logger
from configs.config import Config
from utils.utils import scheduler, get_bot

from .rule import (
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
    blockFormat,
    handle,
)

__zx_plugin_name__ = "思源收集箱 [Hidden]"

__plugin_des__ = "将群里所有消息都发送到指定"

__plugin_version__ = 0.1
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
        bot = get_bot()
        for group_id, config in siyuan_manager.inbox_list.items():
            # 获取该收集箱路径 -> 获取可读路径 -> 新建文档 -> 更新文档 ID
            doc_id, title = await createDoc(
                notebook=config.get('box'),
                path=config.get('path'),
            )
            await siyuan_manager.updateParentID(group_id=group_id, doc_id=doc_id)

            message = f"收集箱 {group_id} 新建文档 {title} 成功 {SIYUAN_URL}/stage/build/desktop/?id={doc_id}"
            logger.info(message)
            await bot.send_msg(
                user_id=int(list(bot.config.superusers)[0]),
                message=message,
            )

    except SiyuanAPIError as e:
        logger.error(f"思源 API HTTP 响应错误 e:{e}")
    except SiyuanAPIException as e:
        logger.error(f"思源 API 内核错误 e:{e}")
    except Exception as e:
        logger.error(f"新建今日文档错误 e:{e}")


# 群文件
@inbox_upload.handle()
async def _(bot: Bot, event: GroupUploadNoticeEvent, state: T_State):
    try:
        event_body = await eventBodyParse(event.json())
        group_id = event_body.get('group_id')  # 群号
        _, _, uploadPath, parentID = siyuan_manager.getInboxInfo(group_id=str(group_id))

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

        await inbox_upload.send(reply)
        logger.info(reply.replace('\n', ' '))
    except SiyuanAPIError as e:
        logger.error(f"思源 API HTTP 响应错误 e:{e}")
    except SiyuanAPIException as e:
        logger.error(f"思源 API 内核错误 e:{e}")
    except Exception as e:
        logger.error(f"群消息处理错误 e:{e}")


# 群消息
@inbox_message.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: T_State):
    try:
        event_body = await eventBodyParse(event.json())
        group_id = event_body.get('group_id')  # 群号
        _, _, uploadPath, parentID = siyuan_manager.getInboxInfo(group_id=str(group_id))

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
        await inbox_upload.send(reply)
        logger.info(reply)
    except SiyuanAPIError as e:
        logger.error(f"思源 API HTTP 响应错误 e:{e}")
    except SiyuanAPIException as e:
        logger.error(f"思源 API 内核错误 e:{e}")
    # except Exception as e:
    #     logger.error(f"群消息处理错误 e:{e}")
