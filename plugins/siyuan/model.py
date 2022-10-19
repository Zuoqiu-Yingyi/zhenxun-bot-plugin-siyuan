from typing import (
    Optional,
    Tuple,
)
from pathlib import Path

from utils.manager.data_class import StaticData


class SiyuanManager(StaticData):
    """
    思源笔记静态数据管理
    """

    def __init__(self, file: Optional[Path]):
        super().__init__(file)
        if not self._data:
            self._data = {
                "inbox": {"inbox_list": {}},
            }
            self.save()
        self.inbox_list = self._data["inbox"]["inbox_list"]

    async def updateData(self):
        self._data["inbox"]["inbox_list"] = self.inbox_list
        self.save()

    async def addInbox(self, group_id: str, box: str, path: str, assets: str, doc_id: str, enable: bool = True, reply: bool = True) -> bool:
        """
        :说明:
            将群聊加入收集箱名单
        :参数:
            box: 笔记本 ID
            path: 该收集箱文档路径
            assets: 资源文件路径
            doc_id: 当天文档的 ID
            enable: 是否启用收集功能
            reply: 是否回复处理结果
        """
        if not self.isInInboxList(group_id):
            self.inbox_list[group_id] = {
                'box': box,  # 笔记本 ID
                'path': path,  # 该收集箱文档路径
                'assets': assets,  # 资源文件路径
                'parentID': doc_id,  # 当天文档的 ID
                'enable': enable, # 是否启用收集功能
                'reply': reply, # 是否回复对发送到收集箱的消息的处理结果
            }
            await self.updateData()
            return True
        return False

    @staticmethod
    def pathParser(doc_path: str) -> Tuple[str, str, str]:
        """
        :说明:
            路径解析
        :参数:
            doc_path: 文档完整路径(含笔记本)
        :返回:
            box: 笔记本 ID
            path: 该收集箱文档路径
            assets: 资源文件路径
        """
        # 移除前导的 '/' 并分割笔记本与文档路径
        path = doc_path.lstrip('/').split('/', 1)
        return (
            path[0],  # 笔记本 ID
            f"/{path[-1]}",  # 该收集箱文档路径
            f"/{path[0]}/{path[-1].removesuffix('.sy')}/assets/",  # 资源文件路径
        )

    async def deleteInbox(self, group_id: str) -> bool:
        """
        :说明:
            将群聊收集箱名单移除
        :参数:
            group_id: 群号
        """
        if self.isInInboxList(group_id):
            del self.inbox_list[group_id]
            await self.updateData()
            return True
        return False

    async def updateParentID(self, group_id: str, doc_id: str) -> bool:
        """
        :说明:
            更新当天文档的 ID
        :参数:
            group_id: 群号
            doc_id: 当天文档的 ID
        """
        if self.isInInboxList(group_id):
            self.inbox_list[group_id]['parentID'] = doc_id
            await self.updateData()
            return True
        return False

    async def updateEnable(self, group_id: str, enable: bool = True) -> bool:
        """
        :说明:
            更新是否开启回复功能
        :参数:
            group_id: 群号
            enable: 是否开启某个收集箱的收集功能
        """
        if self.isInInboxList(group_id):
            self.inbox_list[group_id]['enable'] = enable
            await self.updateData()
            return True
        return False

    async def updateReply(self, group_id: str, reply: bool = True) -> bool:
        """
        :说明:
            更新是否开启回复功能
        :参数:
            group_id: 群号
            reply: 某个收集箱接收消息并处理完成后是否回复消息处理结果
        """
        if self.isInInboxList(group_id):
            self.inbox_list[group_id]['reply'] = reply
            await self.updateData()
            return True
        return False

    def isInInboxList(self, group_id: str) -> bool:
        """
        :说明:
            检查一个群是否是收集箱
        :参数:
            group_id: 群号
        """
        return group_id in self.inbox_list.keys()

    # 获得一个收集箱的信息
    def getInboxInfo(self, group_id: str) -> Tuple[str, str, str]:
        """
        :说明:
            获得一个收集箱的信息
        :参数:
            group_id: 群号
        :返回:
            (box, path, assets, parentID, enable, reply)
        """
        inbox = self.inbox_list[group_id]
        return (
            inbox.get('box'),
            inbox.get('path'),
            inbox.get('assets'),
            inbox.get('parentID'),
            inbox.get('enable', True),
            inbox.get('reply', True),
        )
