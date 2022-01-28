import json
import re

from datetime import datetime
from functools import partial

from pathlib import Path
from typing import (
    Any,
    Dict,
    Tuple,
)

from utils.http_utils import AsyncHttpx

from .API import api

SIYUAN_FILE_PATH = Path("resources/siyuan/files/")
SIYUAN_IMAGE_PATH = Path("resources/siyuan/images/")
SIYUAN_RECORD_PATH = Path("resources/siyuan/records/")
SIYUAN_VIDEO_PATH = Path("resources/siyuan/videos/")

SIYUAN_FILE_PATH.mkdir(parents=True, exist_ok=True)
SIYUAN_IMAGE_PATH.mkdir(parents=True, exist_ok=True)
SIYUAN_RECORD_PATH.mkdir(parents=True, exist_ok=True)
SIYUAN_VIDEO_PATH.mkdir(parents=True, exist_ok=True)

SIYUAN_FILE_PATH = str(SIYUAN_FILE_PATH.absolute()) + '/'
SIYUAN_IMAGE_PATH = str(SIYUAN_IMAGE_PATH.absolute()) + '/'
SIYUAN_RECORD_PATH = str(SIYUAN_RECORD_PATH.absolute()) + '/'
SIYUAN_VIDEO_PATH = str(SIYUAN_VIDEO_PATH.absolute()) + '/'


class Download:

    @classmethod
    def getFileName(cls, url: str) -> str:
        return url.split('/')[-1]

    @classmethod
    async def download(cls, url: str, path: str) -> str:
        """
        :说明:
            下载文件到指定目录
        :参数:
            url: 文件 URL
            path: 下载到指定路径
        """
        if await AsyncHttpx.download_file(
            url,
            path,
        ):
            return str(path.absolute())
        return None

    @classmethod
    async def file(cls, url: str, id: str, name: str) -> str:
        """
        :说明:
            下载群文件
        :参数:
            url: str 文件资源完整路径
            id: str 文件 ID
            name: str 含扩展名的文件名
        :返回:
            文件名
            下载完成后的文件绝对路径
                若下载失败则返回 None
        """
        path = Path(SIYUAN_FILE_PATH) / f"{id[1:]}-{name}"
        return name, await cls.download(url=url, path=path)

    @classmethod
    async def image(cls, url: str, file: str) -> str:
        """
        :说明:
            下载消息中的图片
        :参数:
            url: str 文件资源完整路径
            file: str 含扩展名的文件名
        :返回:
            下载完成后的文件绝对路径
            若下载失败则返回 None
        """
        path = Path(SIYUAN_IMAGE_PATH) / file
        return file, await cls.download(url=url, path=path)

    @classmethod
    async def record(cls, file: str) -> str:
        """
        :说明:
            下载语音
        :参数:
            file: str 文件资源完整路径
        :返回:
            下载完成后的文件绝对路径
            若下载失败则返回 None
        """
        name = cls.getFileName(url=file)
        path = Path(SIYUAN_RECORD_PATH) / name
        return name, await cls.download(url=file, path=path)

    @classmethod
    async def video(cls, file: str) -> str:
        """
        :说明:
            下载短视频
        :参数:
            file: str 文件资源完整路径
        :返回:
            下载完成后的文件绝对路径
            若下载失败则返回 None
        """
        name = cls.getFileName(url=file)
        path = Path(SIYUAN_VIDEO_PATH) / name
        return name, await cls.download(url=file, path=path)


async def eventBodyParse(event: str) -> Dict[str, Any]:
    body = json.loads(event)
    print(body)
    return body


async def getFileInfo(event: Dict[str, Any]) -> Tuple[int, str, str, int, str]:
    """
    :说明:
        获得群文件信息
    :参数:
        event: str 事件的 json 字符串
    :返回:
        busid: int 文件类型
        id: str 文件 ID
        name: str 文件名
        size: int 文件大小(字节)
        url: str 文件 URL
    """
    file = event.get('file')
    return (
        file.get('busid'),
        file.get('id'),
        file.get('name'),
        file.get('size'),
        file.get('url'),
    )


async def transferFile(downloadFunc: partial, uploadPath: str) -> Dict[str, str]:
    """
    :说明:
        转存文件
    :参数:
        downloadFunc: 调用的下载方法
        uploadPath: 上传路径
    :返回:
        {'文件名': '文件名资源引用路径'}
    """
    name, path = await downloadFunc()
    if path is not None:
        with open(path, 'rb') as f:
            response = await api.upload(
                path=uploadPath,
                files=[
                    (name, f),
                ]
            )
            return response.data['succMap']


async def createDoc(notebook: str, path: str, date: datetime = datetime.now(), title: str = None) -> str:
    """
    :说明:
        创建指定日期的文档
    :参数:
        notebook: 笔记本的 ID
        path: 上级文档的路径
        date: 作新文档标题的日期
        title: 新建文档的文档标题
    :返回:
        (新建文档 ID, 新建文档标题)
    """
    r = await api.post(
        url=api.url.getHPathByPath,
        body={
            'notebook': notebook,
            'path': path,
        },
    )
    hpath = r.data
    title = f"{date:%F}" if title is None else title
    r = await api.post(
        url=api.url.createDocWithMd,
        body={
            'notebook': notebook,
            'path': f"{hpath}/{title}",
            'markdown': "",
        },
    )
    return r.data, title


async def blockFormat(
    message: str,
    event: Dict[str, Any],
    is_message: bool = True,
    have_text: bool = True,
) -> str:
    """
    :说明:
        将要插入的信息格式化
    :参数:
        message: 字符串形式的消息
        event: 事件
        is_message: 是否是消息
        have_text: 是否有文本消息
    :返回:
        可以发送的格式化字符串
    """

    if is_message and have_text:
        # 将多个换行符替换为一个换行符并移除前导换行与末尾换行
        # REF [Python将字符串中的多个空格替换为一个空格-云社区-华为云](https://bbs.huaweicloud.com/blogs/112292)
        # REF [str.removeprefix](https://docs.python.org/zh-cn/3/library/stdtypes.html#str.removeprefix)
        # REF [str.removesuffix](https://docs.python.org/zh-cn/3/library/stdtypes.html#str.removesuffix)
        message = re.sub(r"[\r\n]+", r"\n", message).removeprefix('\n')
    l, r = '{', '}'
    message.removesuffix('\n')
    if is_message:
        sender = event.get('sender')
        return f'{message}\n{l}: custom-post-type="message" custom-message-id="{event.get("message_id")}" custom-message-seq="{event.get("message_seq")}" custom-sender-id="{sender.get("user_id")}" custom-sender-nickname="{sender.get("nickname")}" custom-sender-card="{sender.get("card")}"{r}'
    else:
        return f'{message}\n{l}: custom-post-type="notice" custom-sender-id="{event.get("user_id")}"{r}'


class Handle(object):

    def __init__(self):

        self.handle = {
            'at': Handle.at,  # @
            'text': Handle.text,  # 文本
            'face': Handle.face,  # 表情
            'image': Handle.image,  # 图片
            'record': Handle.record,  # 语音
            'video': Handle.video,  # 短视频
            'share': Handle.share,  # 分享链接
            'reply': Handle.reply,  # 回复
            'redbag': Handle.redbag,  # 红包
            'gift': Handle.gift,  # 礼物
            'xml': Handle.xml,  # XML
            'json': Handle.json,  # JSON
            'forward': Handle.forward,  # 转发
        }

    async def __call__(self, t: str, *args, **kw) -> str:
        return await self.handle.get(t, lambda _: f"[CQ:{t}]")(*args, **kw)

    @classmethod
    async def at(cls, data, *args, **kw):
        return f"@{data.get('qq')} "

    @classmethod
    async def text(cls, data, *args, **kw):
        return data.get('text')

    @classmethod
    async def face(cls, data, *args, **kw):
        return f":qq-gif/{data.get('id')}:"

    @classmethod
    async def image(cls, data, uploadPath, *args, **kw):
        file = await transferFile(
            downloadFunc=partial(
                Download.image,
                url=data.get('url'),
                file=data.get('file'),
            ),
            uploadPath=uploadPath,
        )
        for k, v in file.items():
            return f'![{k}]({v})'

    @classmethod
    async def record(cls, data, uploadPath, *args, **kw):
        file = await transferFile(
            downloadFunc=partial(
                Download.record,
                file=data.get('file'),
            ),
            uploadPath=uploadPath,
        )
        for _, v in file.items():
            return f'<audio controls="controls" src="{v}"></audio>'

    @classmethod
    async def video(cls, data, uploadPath, *args, **kw):
        file = await transferFile(
            downloadFunc=partial(
                Download.video,
                file=data.get('file'),
            ),
            uploadPath=uploadPath,
        )
        for _, v in file.items():
            return f'<video controls="controls" src="{v}"></video>'

    @classmethod
    async def share(cls, data, uploadPath, *args, **kw):
        url = data.get('url', "")
        title = data.get('title', "")
        content = data.get('content', "")
        image = data.get('image', "")
        if image != "":
            image = await cls.image(
                data={
                    'url': image,
                    'file': Download.getFileName(image),
                },
                uploadPath=uploadPath,
            )
        return f'{image}\n[{content}]({url} "{title}")'.removeprefix('\n')

    @classmethod
    async def reply(cls, reply, *args, **kw):
        reply_message_id = reply.get('message_id')
        r = await api.post(
            url=api.url.sql,
            body={
                "stmt": f"SELECT block_id FROM attributes WHERE name = 'custom-message-id' AND value = '{reply_message_id}'"
            },
        )
        reply_block_id = r.data[0].get('block_id')
        return f"[[CQ:reply,qq={reply['sender']['user_id']},id={reply_message_id}]](siyuan://blocks/{reply_block_id})\n"

    @classmethod
    async def redbag(cls, data, *args, **kw):
        return f"[CQ:redbag,title={data['title']}]"

    @classmethod
    async def gift(cls, data, *args, **kw):
        return f"[CQ:gift,qq={data['qq']},id={data['id']}]"

    @classmethod
    async def xml(cls, data, *args, **kw):
        pass

    @classmethod
    async def json(cls, data, *args, **kw):
        pass

    @classmethod
    async def forward(cls, data, *args, **kw):
        pass


handle = Handle()
