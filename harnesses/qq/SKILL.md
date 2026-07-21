---
name: QQ
id: qq
description: 通过 GUI 自动化控制 QQ 桌面客户端（发消息、读消息、搜索联系人、截图）
when_to_use: 用户需要通过 QQ 发送消息、查看聊天记录、搜索联系人或截取 QQ 界面时
trigger_words: [qq, 企鹅, 发消息, 聊天]
command: python
args:
  - name: action
    type: string
    required: true
    enum: [send_msg, read_msgs, search_contact, screenshot, list_contacts]
    description: "操作类型：send_msg=发送消息, read_msgs=读取最近消息, search_contact=搜索联系人, screenshot=截取QQ窗口, list_contacts=列出联系人"
  - name: target
    type: string
    required: false
    description: "操作对象（联系人名称或群名）"
  - name: message
    type: string
    required: false
    description: "要发送的消息内容（action=send_msg 时必填）"
  - name: count
    type: integer
    required: false
    default: 10
    description: "读取消息数量（action=read_msgs 时有效）"
examples:
  - "用 QQ 给张三发一条消息：明天见"
  - "看看 QQ 上李四发了什么"
  - "在 QQ 里搜索联系人王五"
  - "截取 QQ 聊天窗口"
---

# QQ Harness

通过 pywinauto 控件定位 + pyautogui 模拟操作来控制 QQ 桌面客户端。

## 支持的操作

| action | 说明 | 必填参数 |
|--------|------|----------|
| send_msg | 向指定联系人/群发送消息 | target, message |
| read_msgs | 读取指定联系人/群的最近消息 | target, count(可选) |
| search_contact | 搜索联系人或群 | target |
| screenshot | 截取当前 QQ 窗口 | 无 |
| list_contacts | 列出最近联系人列表 | 无 |

## 前置条件

- Windows 系统
- QQ 桌面客户端已登录并在运行
- 已安装 `pyautogui` 和 `pywinauto`

## 使用方式

Jarvis 会把参数拼接为命令行调用：

```bash
python run.py --action send_msg --target "张三" --message "明天见" --harness-dir <dir> --workdir <dir>
```

## 注意事项

- 操作期间请勿移动鼠标或切换窗口
- 首次使用可能需要根据 QQ 版本调整控件定位逻辑
- 截图结果会以图片形式回传给 LLM
