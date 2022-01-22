import requests


class APIError(RuntimeError):
    def __init__(self, response):
        self.response = response


class ResponseBody(object):

    def __init__(self, body):
        self.body = body
        self.code = body.get('code')
        self.msg = body.get('msg')
        self.data = body.get('data')


def parse(request):
    def wrapper(*args, **kw):
        response = request(*args, **kw)
        if response.status_code == 200:
            return ResponseBody(response.json())
        else:
            raise APIError(response)
    return wrapper


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
        self.socket = f"{self._protocol}://{self._host}:{self._port}"
        self.url = URL(self.socket)
        self._session = requests.Session()
        self._session.headers.update(self._headers)
        if proxies is not None:
            self._session.proxies.update(proxies)

    @parse
    def post(self, url, body=None):
        if body is None:
            return self._session.post(url)
        else:
            return self._session.post(url, json=body)

    @parse
    def upload(self, path: str, files: list):
        return self._session.post(
            self.url.upload,
            data={
                'assetsDirPath': path,
            },
            files=[('file[]', file) for file in files]
        )
