---
name: 微信
id: wechat
description: 通过 GUI 自动化控制微信桌面客户端（发消息、读消息、搜索联系人、传文件）
when_to_use: 用户需要通过微信发送消息、查看聊天记录、搜索联系人或传输文件时
trigger_words: [微信, wechat, 发消息, 聊天, 朋友圈]
command: python
args:
  - name: action
    type: string
    required: true
    enum: [send_msg, read_msgs, search_contact, transfer_file, screenshot]
    description: "操作类型：send_msg=发送消息, read_msgs=读取最近消息, search_contact=搜索联系人, transfer_file=传输文件, screenshot=截取微信窗口"
  - name: target
    type: string
    required: false
    description: "操作对象（联系人名称或群名）"
  - name: message
    type: string
    required: false
    description: "要发送的消息内容（action=send_msg 时必填）"
  - name: file_path
    type: string
    required: false
    description: "要传输的文件路径（action=transfer_file 时必填）"
  - name: count
    type: integer
    required: false
    default: 10
    description: "读取消息数量（action=read_msgs 时有效）"
examples:
  - "用微信给张三发一条消息：晚上一起吃饭"
  - "看看微信上产品群的最新消息"
  - "通过微信把报告.pdf发给李四"
  - "截取微信聊天窗口"
---

# 微信 Harness

通过 pywinauto 控件定位 + pyautogui 模拟操作来控制微信桌面客户端。

## 支持的操作

| action | 说明 | 必填参数 |
|--------|------|----------|
| send_msg | 向指定联系人/群发送消息 | target, message |
| read_msgs | 读取指定联系人/群的最近消息 | target, count(可选) |
| search_contact | 搜索联系人或群 | target |
| transfer_file | 向指定联系人发送文件 | target, file_path |
| screenshot | 截取当前微信窗口 | 无 |

## 前置条件

- Windows 系统
- 微信桌面客户端已登录并在运行
- 已安装 `pyautogui` 和 `pywinauto`

## 使用方式

```bash
python run.py --action send_msg --target "张三" --message "晚上一起吃饭" --harness-dir <dir> --workdir <dir>
```

## 注意事项

- 操作期间请勿移动鼠标或切换窗口
- 微信版本更新可能导致控件结构变化，需适配
- 文件传输需要文件路径为绝对路径
