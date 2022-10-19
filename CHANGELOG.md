# 更改日志 | CHANGE LOG

## v0.2.2/2022-07-04

- [v0.2.1 <=> v0.2.2](https://github.com/Zuoqiu-Yingyi/zhenxun-bot-plugin-siyuan/compare/v0.2.1...v0.2.2)
- 调整自叙文档缩进样式
- 添加机器人主体的一键安装脚本与 Docker 镜像
- 将插件安装目录更改为 `extensive_plugin`
- 添加环境依赖描述文件
- 更新文档前校验当前日期对应文档是否存在
- 为 `列出收集箱` 指令响应结果添加对应笔记 URL 信息
- 修复子功能加载路径问题
- 添加 `开启收集` 与 `关闭收集` 命令, 用于开启/关闭收集箱的回复
- 添加 `开启消息回复` 与 `关闭消息回复` 命令, 用于开启/关闭收集箱的回复

## v0.2.1/2022-04-15

- [v0.2.0 <=> v0.2.1](https://github.com/Zuoqiu-Yingyi/zhenxun-bot-plugin-siyuan/compare/v0.2.0...v0.2.1)
- 添加在笔记中渲染昵称的 CSS 片段
- 修复 `设置为收集箱` 命令解析问题
- 优化错误信息输出内容
- 完善手动配置配置文件 `siyuan.json` 教程

## v0.2.0/2022-03-10

- [v0.1.3 <=> v0.2.0](https://github.com/Zuoqiu-Yingyi/zhenxun-bot-plugin-siyuan/compare/v0.1.3...v0.2.0)
- 适配 [绪山真寻 Bot Release v0.1.4.3](https://github.com/HibiKier/zhenxun_bot/releases/tag/0.1.4.3)

## v0.1.3/2022-02-28

- [v0.1.2 <=> v0.1.3](https://github.com/Zuoqiu-Yingyi/zhenxun-bot-plugin-siyuan/compare/v0.1.2...v0.1.3)
- 修复列出所有收集箱指令错误
- 修正收集箱管理帮助文本
- 统一设置收集箱管理指令
- 修复添加收集箱指令错误
- 新增嵌套合并转发消息解析

## v0.1.2/2022-01-30

- [v0.1.1 <=> v0.1.2](https://github.com/Zuoqiu-Yingyi/zhenxun-bot-plugin-siyuan/compare/v0.1.1...v0.1.2)
- 修复 `Optional` 参数检查错误
- 修复合并转发中回复消息处理异常

## v0.1.1/2022-01-30

- [v0.1.0 <=> v0.1.1](https://github.com/Zuoqiu-Yingyi/zhenxun-bot-plugin-siyuan/compare/v0.1.0...v0.1.1)
- 更新运行环境依赖 `httpx` 安装教程
- 添加回复消息未查询到的处理方案
- 将回复消息由块超链接更换为块引用
- 将由完整的 URL 组成的普通消息渲染为超链接
- 调整新建文档获取时间戳的时间节点

## v0.1.0/2022-01-29

- 收集箱管理(添加/删除/列出)
- 普通消息发送至收集箱
- 合并转发消息发送至收集箱(合并为一个超级块)
- 调整 `添加到收集箱` 指令参数格式
- 完成文档
