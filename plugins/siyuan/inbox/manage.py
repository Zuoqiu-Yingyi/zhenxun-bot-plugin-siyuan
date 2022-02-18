from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State
from nonebot.adapters.cqhttp import Bot, MessageEvent

from services.log import logger
from utils.utils import (
    get_message_text,
    is_number,
)

from ..data_source import siyuan_manager
from ..utils import createDoc

__zx_plugin_name__ = "思源收集箱管理 [Superuser]"
__plugin_usage__ = """
usage:
    思源笔记收集箱管理
    管理作为收集箱的群, 可以将该群所有的消息/内容发送到指定路径中
    指令:
        设置为收集箱 [文档路径完整路径] [群号]
        从收集箱移除 *[群号]
        列出收集箱
""".strip()
__plugin_des__ = "管理作为思源收集箱的群"
__plugin_cmd__ = [
    "设置为收集箱 [doc_path] [group_id]",
    "从收集箱移除 *[group_id]",
    "列出收集箱",
]
__plugin_version__ = 0.1
__plugin_author__ = "Zuoqiu-Yingyi"

__plugin_type__ = ('思源笔记', 1)
# __plugin_resources__ = {
#     "siyuan": Path("resources/files/siyuan/inbox")
# }

# REF [#](https://v2.nonebot.dev/docs/api/plugin#on_commandcmd-rulenone-aliasesnone-_depth0-kwargs)
inbox_manage = on_command(
    cmd="设置为收集箱",  # 命令名称
    aliases={"从收集箱移除"},  # 命令别名
    priority=1,  # 事件响应器优先级
    permission=SUPERUSER,  # 事件响应权限
    block=True,  # 是否阻止事件向更低优先级传递
)

inbox_list = on_command(
    cmd="列出收集箱",  # 命令名称
    priority=1,  # 事件响应器优先级
    permission=SUPERUSER,  # 事件响应权限
    block=True,  # 是否阻止事件向更低优先级传递
)


@inbox_manage.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    msg = get_message_text(event.json()).split()  # 获取所有传入命令
    doc_path = msg[0]  # 文档的完整路径
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
            if state['_prefix']['raw_command'] in ["设置为收集箱"]:
                if await siyuan_manager.addInbox(
                    group_id=group_id,
                    doc_path=doc_path,
                ):
                    notebook, path, _, _ = siyuan_manager.getInboxInfo(group_id=group_id)
                    doc_id, _ = await createDoc(
                        notebook=notebook,
                        path=path,
                    )
                    await siyuan_manager.updateParentID(group_id=group_id, doc_id=doc_id)
                    success_list.append(group_id)
                    break
            elif state['_prefix']['raw_command'] in ["从收集箱移除"]:
                if await siyuan_manager.deleteInbox(group_id=group_id):
                    success_list.append(group_id)
        success_list = '\n'.join(map(str, success_list))
        reply = f"已成功将群 {success_list} {state['_prefix']['raw_command']}"
    else:
        reply = f"{state['_prefix']['raw_command']}时没有发送有效的群号..."

    await inbox_manage.send(reply)
    logger.info(reply)


@inbox_list.handle()
async def _(bot: Bot, event: MessageEvent, state: T_State):
    groups = '\n'.join(siyuan_manager.inbox_list.keys())  # 获取所有作为收集箱的群号
    if groups:
        reply = f"目前作为思源收集箱的群名单:\n{groups}"
    else:
        reply = "目前没有任何群作为思源收集箱..."

    await inbox_list.send(reply)
    logger.info(reply)
