from typing import (
    Any,
    Callable,
    Dict,
)

import httpx

from configs.config import Config
from utils.utils import get_local_proxy


class SiyuanAPIError(RuntimeError):
    def __init__(self, response):
        self.response = response


class SiyuanAPIException(Exception):
    def __init__(self, response, msg):
        self.response = response
        self.msg = msg


class ResponseBody(object):

    def __init__(self, body: Dict[str, Any]):
        self.body = body
        self.code = body.get('code')
        self.msg = body.get('msg')
        self.data = body.get('data')


class URL:
    lsNotebooks = "/api/notebook/lsNotebooks"
    openNotebook = "/api/notebook/openNotebook"
    closeNotebook = "/api/notebook/closeNotebook"
    renameNotebook = "/api/notebook/renameNotebook"
    createNotebook = "/api/notebook/createNotebook"
    removeNotebook = "/api/notebook/removeNotebook"
    getNotebookConf = "/api/notebook/getNotebookConf"
    setNotebookConf = "/api/notebook/setNotebookConf"

    createDocWithMd = "/api/filetree/createDocWithMd"
    renameDoc = "/api/filetree/renameDoc"
    removeDoc = "/api/filetree/removeDoc"
    moveDoc = "/api/filetree/moveDoc"
    getHPathByPath = "/api/filetree/getHPathByPath"

    upload = "/api/asset/upload"

    insertBlock = "/api/block/insertBlock"
    prependBlock = "/api/block/prependBlock"
    appendBlock = "/api/block/appendBlock"
    updateBlock = "/api/block/updateBlock"
    deleteBlock = "/api/block/deleteBlock"

    setBlockAttrs = "/api/attr/setBlockAttrs"
    getBlockAttrs = "/api/attr/getBlockAttrs"

    sql = "/api/query/sql"

    exportMdContent = "/api/export/exportMdContent"

    bootProgress = "/api/system/bootProgress"
    version = "/api/system/version"
    currentTime = "/api/system/currentTime"

    def __init__(self, socket):
        self.lsNotebooks = socket + URL.lsNotebooks
        self.openNotebook = socket + URL.openNotebook
        self.closeNotebook = socket + URL.closeNotebook
        self.renameNotebook = socket + URL.renameNotebook
        self.createNotebook = socket + URL.createNotebook
        self.removeNotebook = socket + URL.removeNotebook
        self.getNotebookConf = socket + URL.getNotebookConf
        self.setNotebookConf = socket + URL.setNotebookConf
        self.createDocWithMd = socket + URL.createDocWithMd
        self.renameDoc = socket + URL.renameDoc
        self.removeDoc = socket + URL.removeDoc
        self.moveDoc = socket + URL.moveDoc
        self.getHPathByPath = socket + URL.getHPathByPath
        self.upload = socket + URL.upload
        self.insertBlock = socket + URL.insertBlock
        self.prependBlock = socket + URL.prependBlock
        self.appendBlock = socket + URL.appendBlock
        self.updateBlock = socket + URL.updateBlock
        self.deleteBlock = socket + URL.deleteBlock
        self.setBlockAttrs = socket + URL.setBlockAttrs
        self.getBlockAttrs = socket + URL.getBlockAttrs
        self.sql = socket + URL.sql
        self.exportMdContent = socket + URL.exportMdContent
        self.bootProgress = socket + URL.bootProgress
        self.version = socket + URL.version
        self.currentTime = socket + URL.currentTime


def parse(request: Callable) -> Callable:
    async def wrapper(*args, **kw) -> ResponseBody:
        response = await request(*args, **kw)
        if response.status_code == 200:
            body = ResponseBody(response.json())
            if body.code == 0:
                return body
            raise SiyuanAPIException(response, body.msg)
        raise SiyuanAPIError(response)
    return wrapper


class API(object):

    def __init__(
        self,
        token="0123456789ABCDEF",
        host="localhost",
        port="6806",
        ssl=False,
        proxies=None,
    ):
        self._protocol = ("https" if ssl else "http")
        self._host = host
        self._port = port
        self._token = token
        self._headers = {
            "Authorization": f"Token {self._token}",
        }
        self._proxies = proxies
        self.socket = f"{self._protocol}://{self._host}:{self._port}"
        self.url = URL(self.socket)

    @parse
    async def post(self, url, body=None):
        async with httpx.AsyncClient(headers=self._headers, proxies=self._proxies) as client:
            if body is None:
                return await client.post(url)
            else:
                return await client.post(url, json=body)

    @parse
    async def upload(self, path: str, files: list):
        async with httpx.AsyncClient(headers=self._headers, proxies=self._proxies) as client:
            return await client.post(
                self.url.upload,
                data={
                    'assetsDirPath': path,
                },
                files=[('file[]', file) for file in files]
            )


api = API(
    token=Config.get_config("siyuan", "SIYUAN_TOKEN"),
    host=Config.get_config("siyuan", "SIYUAN_HOST"),
    port=Config.get_config("siyuan", "SIYUAN_PORT"),
    ssl=Config.get_config("siyuan", "SIYUAN_SSL"),
    proxies={
        'http://': get_local_proxy(),
        'https://': get_local_proxy(),
    },
)

# api = API(
#     token='arvj70bkd2eajv0a',
#     host='127.0.0.1',
#     port='6806',
#     ssl=False,
# )

# api = API(
#     token='arvj70bkd2eajv0a',
#     host='siyuan.zuoqiu.asia',
#     port='443',
#     ssl=True,
# )
