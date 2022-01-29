# zhenxun-bot-plugin-siyuan

<center>

![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/Zuoqiu-Yingyi/zhenxun-bot-plugin-siyuan?include_prereleases)
![GitHub Release Date](https://img.shields.io/github/release-date/Zuoqiu-Yingyi/zhenxun-bot-plugin-siyuan)
![GitHub](https://img.shields.io/github/license/Zuoqiu-Yingyi/zhenxun-bot-plugin-siyuan)
![GitHub last commit](https://img.shields.io/github/last-commit/Zuoqiu-Yingyi/zhenxun-bot-plugin-siyuan)
![GitHub repo size](https://img.shields.io/github/repo-size/Zuoqiu-Yingyi/zhenxun-bot-plugin-siyuan)
![jsDelivr hits (GitHub)](https://img.shields.io/jsdelivr/gh/hy/Zuoqiu-Yingyi/zhenxun-bot-plugin-siyuan?label=hits)
![GitHub all releases](https://img.shields.io/github/downloads/Zuoqiu-Yingyi/zhenxun-bot-plugin-siyuan/total)

</center>

QQ 机器人 [绪山真寻 Bot](https://hibikier.github.io/zhenxun_bot/) 的 [思源笔记](https://github.com/siyuan-note/siyuan) 插件, 可以将 QQ 群转化为思源笔记的收集箱

您需要订阅思源笔记的增值服务，欢迎使用我的推荐码: **`h0sc9rc`** (\*^▽^\*)

## 预览 | PREVIEW

## 功能 | FUNCTION

1. 上传群中所有的资源文件并插入到文档中
   - 资源文件类型
     - 消息中的图片 -> 上传图片并使用图片链接嵌入 `![图片文件名](assets/图片文件名-<文件ID>.<扩展名>))`
     - 上传的群文件 -> 上传文件并使用超链接嵌入 `[文件名](assets/文件名-<文件ID>.<扩展名>))`
     - 语音消息 -> 上传文件并使用音频块嵌入 `<audio controls="controls" src="assets/音频文件名-<文件ID>.<扩展名>))"></audio>`
     - 视频消息 -> 上传文件并使用视频块嵌入 `<video controls="controls" src="assets/视频文件名-<文件ID>.<扩展名>))"></video>`
2. 解析群中的所有消息
   - 普通文本消息 -> 移除空行, 构造并插入一个块(可以直接插入 Markdown 语句)
   - 图文混排 -> 移除空行, 保持混排样式构造并插入一个块(也可以直接插入网络图片)
   - @群成员 -> <u>@<QQ号></u> `<u>@<QQ号></u>`

## 开始 | START

1. 安装 `go-cqhttp` 
   - 安装教程: [安装go-cqhttp | 绪山真寻Bot](https://hibikier.github.io/zhenxun_bot/docs/installation_doc/install_gocq.html)
   - 项目文档: [go-cqhttp 帮助中心](https://docs.go-cqhttp.org/)
   - 项目仓库: [GitHub - Mrs4s/go-cqhttp: cqhttp的golang实现，轻量、原生跨平台.](https://github.com/Mrs4s/go-cqhttp)
2. 安装 `Postgresql` 数据库
   - 安装教程: [安装Postgresql数据库 | 绪山真寻Bot](https://hibikier.github.io/zhenxun_bot/docs/installation_doc/install_postgresql.html)
   - 项目文档:
     - [PostgreSQL: Documentation](https://www.postgresql.org/docs/)
     - [文档目录/Document Index: 世界上功能最强大的开源数据库...](http://www.postgres.cn/v2/document)
3. 安装 `绪山真寻 Bot`
   - 安装教程: [安装真寻Bot | 绪山真寻Bot](https://hibikier.github.io/zhenxun_bot/docs/installation_doc/install_zhenxun.html)
   - 项目文档: [绪山真寻Bot](https://hibikier.github.io/zhenxun_bot/)
   - 项目仓库: [GitHub - HibiKier/zhenxun_bot: 基于 Nonebot2 和 go-cqhttp 开发，以 postgresql 作为数据库，非常可爱的绪山真寻bot](https://github.com/HibiKier/zhenxun_bot)
4. 额外安装本插件的依赖包
   - 使用 `pip` 安装
     ```bash
     pip install httpx
     ```
   - 或者, 使用 `conda` 安装
     ```bash
     conda install httpx -c conda-forge
     ```
5. 配置插件选项
   - 打开文件 `data/configs/plugins2config.yaml`
   - 填写如下 5 个字段的 `value` 与 `default_value` 值
     - `SIYUAN_HOST`: 思源笔记内核所在主机名
       - 类型: 字符串
       - 示例: `'localhost'`
       - 说明: 可以填本机 `localhost`, 其他主机 `IP 地址` 或其他主机 `域名`
       - 备注: 如果思源笔记使用 Nginx 反向代理, 那么填写反向代理指向的主机即可
     - `SIYUAN_PORT`: 思源笔记内核监听端口
       - 类型: 字符串
       - 示例: `'6806'`
       - 说明: 填写思源笔记内核监听的端口
       - 备注: 如果思源笔记使用 Nginx 反向代理, 那么填写反向代理的目标端口即可
     - `SIYUAN_SSL`: 思源笔记是否启用 SSL
       - 类型: 布尔值
       - 示例: `false`
       - 说明: 是否启用 SSL 安全协议
       - 备注: 该选项取决于 `真寻 bot` 访问目标主机是否需要使用 `HTTPS` 协议
     - `SIYUAN_TOKEN`: 思源笔记 API Token
       - 类型: 字符串(16字符)
       - 示例: `'0123456789ABCDEF'`
       - 说明: 若思源笔记启用 `访问授权码 (设置>关于>访问授权码)`, 则需要配置有效的 `API token (设置>关于>API token)`
       - 备注: 若未启用 `访问授权码`, 该字段可以填充任意字符串
     - `SIYUAN_URL`: 思源笔记 URL
       - 类型: 字符串
       - 示例: `'https://your.domain.name:6806'`
       - 说明: 使用 `http` 协议与 `80` 端口或使用 `https` 协议与 `443` 端口可以省略端口号, 请确保 `<该字段值>/stage/build/desktop/` 可以进入思源笔记主界面, 
       - 备注: 该字段用于生成一个指向刚刚插入块的 URL
6. 使用 `theme.js` 为思源笔记添加使用 URL 参数跳转指定块的功能
   - 带参 URL 示例: `https://your.domain.name:6806/stage/build/desktop/?id=20220128232710-huurm0y`
     - 该参数可以在从当前聚焦的页签中切换到 id 为 `20220128232710-huurm0y` 的块
   - 主题 `Dark+` 已内置了该功能, 详情请参考 [Zuoqiu-Yingyi/siyuan-theme-dark-plus](https://github.com/Zuoqiu-Yingyi/siyuan-theme-dark-plus)
   - 其他主题可以将如下 js 片段放在文件 `<工作空间>/conf/appearance/themes/<主题名>/theme.js` 开头(若没有该文件新建即可)
     ```js
     function loadScript(url) {
        let script = document.createElement('script');
        script.setAttribute('type', 'module');
        script.setAttribute('src', url);
        document.getElementsByTagName('head')[0].appendChild(script);
     }

     (function () {
         loadScript("/appearance/themes/goto.js");
     })()
     ```
     并新建文件 `<工作空间>/conf/appearance/themes/goto.js`, 在该文件中写入如下内容
     ```js
     /** 使用形如 id=<块 ID> 的 URL 参数跳转到指定的块
     *  REF [leolee9086](https://github.com/leolee9086)
     */
     function urlParser(url) {
         url = url || '';
         const queryObj = {};
         const reg = /[?&]([^=&#]+)=([^&#]*)/g;
         const queryArr = url.match(reg) || [];
         // console.log(queryArr)
         for (const i in queryArr) {
             if (Object.hasOwnProperty.call(queryArr, i)) {
                 const query = queryArr[i].split('=');
                 const key = query[0].substr(1);
                 const value = decodeURIComponent(query[1]);
                 queryObj[key] ? queryObj[key] = [].concat(queryObj[key], value) : queryObj[key] = value;
             }
         }
         console.log(queryObj)
         return queryObj;
 
     }
     function goto(id) {
         let doc = window.document
         // console.log(doc)
         let link = doc.createElement("span")
         link.setAttribute("data-type", "block-ref")
         link.setAttribute("data-id", id)
         let target = doc.querySelector(".protyle-wysiwyg div[data-node-id] div[contenteditable]")
         if (target) {
             target.appendChild(link)
             link.click()
             link.remove()
         }
         else {
             setTimeout(async () => goto(id), 1000)
         }
     }
     async function jumpToID() {
         let params = urlParser(window.location.href)
         if (params) {
             let id = params.id
             if (id) {
                 goto(id)
             }
         }
     }
     window.onload = setTimeout(jumpToID(), 0)
     ```
7. 在 bot 访问的思源笔记本 Web 端中选择一个文档作为收集箱(选择笔记本内的一个文档而非笔记本), 并记录该文档的绝对路径
   - 假设选择在 `收集箱` 笔记本内的 `Inbox` 文档作为收集箱, 该文档的 ID 为 `20220128203409-j5553g7` (可以从该文档的右键菜单中获取文档的 ID)
   - 从文件系统中搜索 `20220128203409-j5553g7.sy` 文件, 并获得该文件相对于 `<工作空间>/data/` 目录的路径, 例如 `20220128203353-2p55r7q/20220128203409-j5553g7.sy`
     - 其中 `20220128203353-2p55r7q/` 为 `收集箱` 笔记本的目录
     - 其中 `20220128203409-j5553g7.sy` 为 `Inbox` 文档的数据文件
8. 依次启动 `go-cqhttp`, `Postgresql` 与 `绪山真寻 bot`
9.  使用超级用户账户向机器人账户发送如下命令进行收集箱管理
   - `添加到收集箱 [笔记本ID/文档路径] [群号]`
     - 示例: `添加到收集箱 20220128203353-2p55r7q/20220128203409-j5553g7.sy 123456789`
     - `[文档路径完整路径]` 需要填写第 6 步获得的文档完整路径, 这里是 `20220128203353-2p55r7q/20220128203409-j5553g7.sy`
     - `[群号]` 需要填写作为收集箱的群号(机器人必须已经加入该群), 这里是 `123456789`, 该群与 ID 为 `20220128203409-j5553g7` 的文档绑定
       - 注意: 一旦完成绑定, 该文档不可移动, 若需要移动则需要移除收集箱后重新添加收集箱
     - 注: 添加到该收集箱的资源文件在这里会放置在 `20220128203353-2p55r7q/20220128203409-j5553g7/assets/` 目录下
   - `从收集箱移除 *[群号]`
     - 示例: `从收集箱移除 123456789`
     - `*[群号]` 即为想要移除地、作为收集箱的群号列表, 多个群号中间使用空格隔开
     - 注1: 将一个或多个群移除后已经添加到对应收集箱的内容不会随之删除
     - 注2: 移除的群可以再次设置为收集箱
   - `列出收集箱`
     - 示例: `列出收集箱`
     - 该命令会列出所有的作为收集箱的群

## 自定义配置 | CUSTOM CONFIG

配置文件路径: `<绪山真寻bot根目录>/data/configs/plugins2config.yaml`

### 配置示例 | CONFIG EXAMPLE

```yaml
siyuan:
  SIYUAN_HOST:
    value: localhost
    name: 主机名
    help: 思源笔记内核所在主机名
    default_value: localhost
    level_module:
  SIYUAN_PORT:
    value: '6806'
    name: 端口号
    help: 思源笔记内核监听端口
    default_value: '6806'
    level_module:
  SIYUAN_SSL:
    value: false
    name: 启用 SSL
    help: 思源笔记是否启用 SSL
    default_value: false
    level_module:
  SIYUAN_TOKEN:
    value: 0123456789ABCDEF
    name: Token
    help: 思源笔记 API Token
    default_value: 0123456789ABCDEF
    level_module:
  SIYUAN_URL:
    value: https://your.domain.name
    name: Token
    help: 思源笔记 URL
    default_value: https://your.domain.name
    level_module:
```


## 依赖 & 参考 & 感谢 | DEPENDENCE & REFERENCE & THANKS

| 项目 \| Project                                        | 仓库 \| Reop                                                                                                           | 作者 \| Author                                       | 许可证 \| License                                                                      |
| :----------------------------------------------------- | :--------------------------------------------------------------------------------------------------------------------- | :--------------------------------------------------- | :------------------------------------------------------------------------------------- |
| [绪山真寻Bot](https://hibikier.github.io/zhenxun_bot/) | [GitHub - HibiKier/zhenxun_bot](https://github.com/HibiKier/zhenxun_bot)                                               | **[HibiKier](https://github.com/HibiKier)**          | *[AGPL\-3.0 License](https://github.com/HibiKier/zhenxun_bot/blob/main/LICENSE)*       |
| [NoneBot](https://v2.nonebot.dev/)                     | [GitHub - nonebot/nonebot2](https://github.com/nonebot/nonebot2)                                                       | **[NoneBot](https://github.com/nonebot)**            | *[MIT License](https://github.com/nonebot/nonebot2/blob/master/LICENSE)*               |
| [OneBot](https://onebot.dev/)                          | [GitHub - botuniverse/onebot](https://github.com/botuniverse/onebot)                                                   | **[Bot Universe](https://github.com/botuniverse)**   | *[MIT License](https://github.com/botuniverse/onebot/blob/master/LICENSE)*             |
| [GO-CQHTTP](https://go-cqhttp.org/)                    | [GitHub - Mrs4s/go-cqhttp](https://github.com/Mrs4s/go-cqhttp)                                                         | **[Mrs4s](https://github.com/Mrs4s)**                | *[AGPL\-3.0 License](https://github.com/Mrs4s/go-cqhttp/blob/master/LICENSE)*          |
| 真寻 bot 的插件库                                      | [GitHub - AkashiCoin/nonebot_plugins_zhenxun_bot](https://github.com/AkashiCoin/nonebot_plugins_zhenxun_bot)           | **[AkashiCoin](https://github.com/AkashiCoin)**      | *Unknown*                                                                              |
| Nakuru Project                                         | [GitHub - Lxns-Network/nakuru-project](https://github.com/Lxns-Network/nakuru-project)                                 | **[Lxns\-Network](https://github.com/Lxns-Network)** | *[MIT License](https://github.com/Lxns-Network/nakuru-project/blob/master/LICENSE)*    |
| HimesakaBot                                            | [GitHub - mobyw/nonebot-twitter-guild](https://github.com/mobyw/nonebot-twitter-guild)                                 | **[mobyw](https://github.com/mobyw)**                | *[GPL\-3.0 License](https://github.com/mobyw/nonebot-twitter-guild/blob/main/LICENSE)* |
| NoneBot Plugin APScheduler                             | [GitHub - nonebot/plugin-apscheduler: APScheduler Support for NoneBot2](https://github.com/nonebot/plugin-apscheduler) | **[nonebot](https://github.com/nonebot)**            | *[MIT License](https://github.com/nonebot/plugin-apscheduler/blob/master/LICENSE)*     |

<!-- | | | **** | ** | -->

注: 排名不分先后

## 更改日志 | CHANGE LOGS

[CHANGELOG](CHANGELOG.md)
