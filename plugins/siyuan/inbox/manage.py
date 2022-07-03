from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Bot, MessageEvent

from services.log import logger
from configs.config import Config
from utils.utils import (
    get_message_text,
    is_number,
)

from ..data_source import siyuan_manager
from ..utils import createDoc
from ..API import (
    SiyuanAPIError,
    SiyuanAPIException,
)

command = {
    "append": "设置为收集箱",
    "remove": "从收集箱移除",
    "list": "列出收集箱",
}

__zx_plugin_name__ = "思源收集箱管理 [Superuser]"
__plugin_usage__ = f"""
usage:
    思源笔记收集箱管理
    管理作为收集箱的群, 可以将该群所有的消息/内容发送到指定路径中
    指令:
        {command['append']} [文档路径完整路径] [群号]
        {command['remove']} *[群号]
        {command['list']}
""".strip()
__plugin_des__ = "思源收集箱管理"
__plugin_cmd__ = [
    f"{command['append']} [doc_path] [group_id]",
    f"{command['remove']} *[group_id]",
    f"{command['list']}",
]
__plugin_version__ = 0.21
__plugin_author__ = "Zuoqiu-Yingyi"

__plugin_type__ = ('思源笔记', 1)
# __plugin_resources__ = {
#     "siyuan": Path("resources/files/siyuan/inbox")
# }

# REF [#](https://v2.nonebot.dev/docs/api/plugin#on_commandcmd-rulenone-aliasesnone-_depth0-kwargs)
inbox_manage = on_command(
    cmd=command['append'],  # 命令名称
    aliases={command['remove']},  # 命令别名
    priority=1,  # 事件响应器优先级
    permission=SUPERUSER,  # 事件响应权限
    block=True,  # 是否阻止事件向更低优先级传递
)

inbox_list = on_command(
    cmd=command['list'],  # 命令名称
    priority=1,  # 事件响应器优先级
    permission=SUPERUSER,  # 事件响应权限
    block=True,  # 是否阻止事件向更低优先级传递
)

SIYUAN_URL = Config.get_config("siyuan", "SIYUAN_URL")


@inbox_manage.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    try:
        error_info = None
        msg = get_message_text(event.json()).split()  # 获取所有传入命令
        # print(msg)
        doc_path = msg[1]  # 文档的完整路径
        all_group = map(
            lambda g: g['group_id'],
            await bot.get_group_list(self_id=int(bot.self_id)),
        )  # 获取机器人所有加入的群号

        group_list = filter(
            lambda group: is_number(group) and int(group) in all_group,
            msg,
        )
        if group_list:
            success_list = []  # 成功处理的群
            for group_id in group_list:
                if state['_prefix']['raw_command'] in {command['append']}:
                    if not siyuan_manager.isInInboxList(group_id=group_id):
                        box, path, assets = siyuan_manager.pathParser(doc_path=doc_path)
                        doc_id, _ = await createDoc(
                            notebook=box,
                            path=path,
                        )
                        if await siyuan_manager.addInbox(
                            group_id=group_id,
                            box=box,
                            path=path,
                            assets=assets,
                            doc_id=doc_id,
                        ):
                            success_list.append(group_id)
                        break
                elif state['_prefix']['raw_command'] in {command['remove']}:
                    if await siyuan_manager.deleteInbox(group_id=group_id):
                        success_list.append(group_id)
            success_list = '\n'.join(map(str, success_list))
            reply = f"已成功将群 {success_list} {state['_prefix']['raw_command']}"
        else:
            reply = f"{state['_prefix']['raw_command']}时没有发送有效的群号..."
    except SiyuanAPIException as e:
        error_info = f"思源 API 内核错误 e: {e.msg}"
    except SiyuanAPIError as e:
        error_info = f"思源 API HTTP 响应错误 e: {e}"
    except Exception as e:
        error_info = f"消息处理错误 e: {e}"
    else:
        await inbox_manage.send(reply)
        logger.info(reply)
    finally:
        if error_info is not None:
            await inbox_manage.send(error_info)
            logger.error(error_info)


@inbox_list.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    try:
        error_info = None
        inboxs = []
        for group_id in siyuan_manager.inbox_list.keys():
            doc_id = siyuan_manager.inbox_list[group_id]['path'][-25:-3]
            inboxs.append(f"{group_id}: {SIYUAN_URL}/stage/build/desktop/?id={doc_id}")
        inboxs = '\n'.join(inboxs)
        if inboxs:
            reply = f"目前作为思源收集箱的群名单:\n{inboxs}"
        else:
            reply = "目前没有任何群作为思源收集箱..."
    except SiyuanAPIException as e:
        error_info = f"思源 API 内核错误 e: {e.msg}"
    except SiyuanAPIError as e:
        error_info = f"思源 API HTTP 响应错误 e: {e}"
    except Exception as e:
        error_info = f"消息处理错误 e: {e}"
    else:
        await inbox_list.send(reply)
        logger.info(reply)
    finally:
        if error_info is not None:
            await inbox_list.send(error_info)
            logger.error(reply)
