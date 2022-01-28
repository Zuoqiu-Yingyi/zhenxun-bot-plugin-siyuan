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

    async def addInbox(self, group_id: str, doc_path: str, doc_id: str = None) -> bool:
        """
        :说明:
            将群聊加入收集箱名单
        :参数:
            group_id: 群号
            doc_path: 文档完整路径(含笔记本)
            doc_id: 当天文档的 ID
        """
        if not self.isInInboxList(group_id):
            # 移除前导的 '/' 并分割笔记本与文档路径
            path = doc_path.lstrip('/').split('/', 1)
            self.inbox_list[group_id] = {
                'box': path[0],  # 笔记本 ID
                'path': f"/{path[-1]}",  # 该收集箱文档路径
                'assets': f"/{path[0]}/{path[-1].removesuffix('.sy')}/assets/",  # 资源文件路径
                'parentID': doc_id,  # 当天文档的 ID
            }
            await self.updateData()
            return True
        return False

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
            (box, path, assets, parentID)
        """
        inbox = self.inbox_list[group_id]
        return (
            inbox.get('box'),
            inbox.get('path'),
            inbox.get('assets'),
            inbox.get('parentID'),
        )
