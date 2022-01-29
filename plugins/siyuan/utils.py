import re
import json

import xml.dom.minidom

from datetime import datetime
from functools import partial

from pathlib import Path
from typing import (
    Any,
    Dict,
    Tuple,
    Union,
    Optional,
)

from nonebot.adapters.cqhttp import (
    Bot,
)

from utils.http_utils import AsyncHttpx

from .API import api
from .cqcode import cqparser

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
            文件名
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
            文件名
            下载完成后的文件绝对路径
            若下载失败则返回 None
        """
        name = cls.getFileName(url=file)
        path = Path(SIYUAN_RECORD_PATH) / name
        return name, await cls.download(url=file, path=path)

    @classmethod
    async def video(cls, url: str, file: str) -> str:
        """
        :说明:
            下载消息中的图片
        :参数:
            url: str 文件资源完整路径
            file: str 含扩展名的文件名
        :返回:
            文件名
            下载完成后的文件绝对路径
            若下载失败则返回 None
        """
        path = Path(SIYUAN_VIDEO_PATH) / file
        return file, await cls.download(url=url, path=path)


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


async def createDoc(notebook: str, path: str, date: Optional(datetime) = None, title: str = None) -> str:
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

    date = datetime.now() if date is None else date
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
        return f'{message}\n{l}: custom-post-type="message" custom-message-id="{event.get("message_id")}" custom-message-seq="{event.get("message_seq")}" custom-sender-id="{sender.get("user_id")}" custom-sender-nickname="{sender.get("nickname")}" custom-sender-card="{sender.get("card")}" custom-time="{event.get("time")}"{r}'
    else:
        return f'{message}\n{l}: custom-post-type="notice" custom-sender-id="{event.get("user_id")}" custom-time="{event.get("time")}{r}'


async def XMLFormat(s: str, indent: str = '    ') -> str:
    """
    :说明:
        XML 文本格式化
    :参数:
        s: 原 XML 文本字符串
        indent: 缩进字符
    :返回:
        格式化后的 XML 文本
    :参考:
        REF [Python如何优雅的格式化XML 【Python XML Format】 - sssuperMario - 博客园](https://www.cnblogs.com/atrox/p/13579541.html)
        REF [xml.dom.minidom - 最小化的 DOM 实现](https://docs.python.org/zh-cn/3/library/xml.dom.minidom.html?highlight=xml%20toprettyxml)
        REF [xml.dom.minidom.Node.toprettyxml](https://docs.python.org/zh-cn/3/library/xml.dom.minidom.html?highlight=xml%20toprettyxml#xml.dom.minidom.Node.toprettyxml)
    """
    return re.sub(r"\n\s*\n", r"\n", xml.dom.minidom.parseString(s).toprettyxml(indent=indent))


async def JSONFormat(s: Union[str, Dict[str, Any]], indent: str = '    ') -> str:
    """
    :说明:
        JSON 文本格式化
    :参数:
        s: 原 JSON 文本字符串/已解析的 dict
        indent: 缩进字符
    :返回:
        格式化后的 JSON 文本
    :参考:
        REF [json.dumps](https://docs.python.org/zh-cn/3/library/json.html?highlight=json%20dumps#json.dumps)
    """
    if isinstance(s, str):
        s = json.loads(s)
    return json.dumps(s, indent=indent)


class Handle(object):

    handle = {  # 消息类型 -> 消息处理方法名
        'at': 'Handle.at',  # @

        'text': 'Handle.text',  # 文本
        'plain': 'Handle.text',  # 文本

        'face': 'Handle.face',  # 表情
        'image': 'Handle.image',  # 图片
        'record': 'Handle.record',  # 语音
        'video': 'Handle.video',  # 短视频
        'share': 'Handle.share',  # 分享链接
        'reply': 'Handle.reply',  # 回复
        'redbag': 'Handle.redbag',  # 红包
        'gift': 'Handle.gift',  # 礼物
        'xml': 'Handle.xml',  # XML
        'json': 'Handle.json',  # JSON
        'forward': 'Handle.forward',  # 转发
    }

    def __init__(self):
        pass

    async def __call__(self, t: str, *args, **kw) -> str:
        return await self.run(t, *args, **kw)

    @classmethod
    async def run(cls, t: str, *args, **kw) -> str:
        return await eval(cls.handle.get(t.lower(), f'lambda *args, **kw: "`[CQ:{t}]`"'))(*args, **kw)

    @classmethod
    async def at(cls, data: Dict[str, Any], *args, **kw):
        return f"<u>@{data.get('qq')}</u>"

    @classmethod
    async def text(cls, data: Dict[str, Any], *args, **kw):
        # REF [正则表达式匹配URL - 禅趣 - 博客园](https://www.cnblogs.com/wang1593840378/p/6095500.html)
        href = r"((ht|f)tps?):\/\/([\w\-]+(\.[\w\-]+)*\/)*[\w\-]+(\.[\w\-]+)*\/?(\?([\w\-\.,@?^=%&:\/~\+#]*)+)?"
        t = data.get('text')

        if re.fullmatch(href, t) is not None:  # 整个文本是一个超链接
            t = f"[{t}]({t})"

        return t

    @classmethod
    async def face(cls, data: Dict[str, Any], *args, **kw):
        return f":qq-gif/{data.get('id')}:"

    @classmethod
    async def image(cls, data: Dict[str, Any], uploadPath: str, *args, **kw):
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
    async def record(cls, data: Dict[str, Any], uploadPath: str, *args, **kw):
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
    async def video(cls, data: Dict[str, Any], uploadPath: str, *args, **kw):
        file = await transferFile(
            downloadFunc=partial(
                Download.video,
                url=data.get('url'),
                file=data.get('file'),
            ),
            uploadPath=uploadPath,
        )
        for _, v in file.items():
            return f'<video controls="controls" src="{v}"></video>'

    @classmethod
    async def share(cls, data: Dict[str, Any], uploadPath: str, *args, **kw):
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
        if len(r.data) > 0:  # 从收集箱中查询到了所回复消息对应的块
            reply_block_id = r.data[0].get('block_id')

            # 块引用
            return f'(({reply_block_id} "[CQ:reply,qq={reply["sender"]["user_id"]},id={reply_message_id}]"))\n'

            # 块超链接
            # return f"[[CQ:reply,qq={reply['sender']['user_id']},id={reply_message_id}]](siyuan://blocks/{reply_block_id})\n"
        else:  # 未从收集箱中查询到了所回复消息对应的块
            return f"`[CQ:reply,qq={reply['sender']['user_id']},id={reply_message_id}]`\n"

    @classmethod
    async def redbag(cls, data: Dict[str, Any], *args, **kw):
        return f"`[CQ:redbag,title={data['title']}]`"

    @classmethod
    async def gift(cls, data: Dict[str, Any], *args, **kw):
        return f"`[CQ:gift,qq={data['qq']},id={data['id']}]`"

    @classmethod
    async def xml(cls, data: Dict[str, Any], indent: str = '    ', *args, **kw):
        prefix = '<?xml version=\"1.0\" encoding=\"utf-8\"?>\n    '
        xml_str = data.get('data').removeprefix(prefix)
        xml_str = await XMLFormat(s=xml_str, indent=indent)
        return f"```xml\n{xml_str}\n```"

    @classmethod
    async def json(cls, data: Dict[str, Any], indent: str = '    ', *args, **kw):
        json_str = await JSONFormat(s=data.get('data'), indent=indent)
        return f"```json\n{json_str}\n```"

    @classmethod
    async def forward(cls, data: Dict[str, Any], bot: Bot, *args, **kw):
        forward_msg = await bot.get_forward_msg(id=data.get('id'))
        messages = forward_msg.get('messages')

        l, r = '{', '}'
        reply = []  # 各消息序列化后的字符串列表
        for message in messages:  # 遍历转发的消息
            # print(message)
            msg = []  # 一条消息各组成元素序列化后的字符串列表
            contents = cqparser.parseChain(message.get('content'))
            for content in contents:  # 遍历一条消息的组成部分
                # print(content)
                msg.append(await cls.run(
                    t=content.type,
                    data=content.toDict().get('data'),
                    *args,
                    **kw,
                ))
            msg = re.sub(r"[\r\n]+", r"\n", ''.join(msg)).removeprefix('\n').removesuffix('\n')
            sender = message.get('sender')
            reply.append(f'{msg}\n{l}: custom-post-type="node" custom-sender-id="{sender.get("user_id")}" custom-sender-nickname="{sender.get("nickname")}" custom-time="{message.get("time")}{r}')

        return "{{{row\n%s\n}}}" % '\n\n'.join(reply)


handle = Handle()
