---
name: Firefox
id: firefox
description: 通过 Selenium WebDriver 控制 Firefox 浏览器（打开网页、点击、输入、截图、获取文本）
when_to_use: 用户需要用 Firefox 浏览器打开网页、自动化操作网页元素、截取网页或提取页面内容时
trigger_words: [firefox, 火狐, 浏览器, 网页, 打开网站]
command: python
args:
  - name: action
    type: string
    required: true
    enum: [open_url, click, type_text, screenshot, get_text, go_back, go_forward, close]
    description: "操作类型：open_url=打开网址, click=点击元素, type_text=输入文本, screenshot=截取页面, get_text=获取页面文本, go_back=后退, go_forward=前进, close=关闭浏览器"
  - name: target
    type: string
    required: false
    description: "操作对象（URL地址 或 CSS选择器）"
  - name: text
    type: string
    required: false
    description: "要输入的文本内容（action=type_text 时必填）"
  - name: output_path
    type: string
    required: false
    description: "截图保存路径（action=screenshot 时可选，默认保存到工作目录）"
examples:
  - "用 Firefox 打开百度搜索 Python 教程"
  - "截取当前 Firefox 页面"
  - "获取 Firefox 当前页面的标题和文本"
  - "在 Firefox 的搜索框里输入关键词并点击搜索"
---

# Firefox Harness

通过 Selenium WebDriver（Marionette 协议）控制 Firefox 浏览器。

## 支持的操作

| action | 说明 | 必填参数 |
|--------|------|----------|
| open_url | 打开指定网址 | target(URL) |
| click | 点击匹配 CSS 选择器的元素 | target(CSS选择器) |
| type_text | 在匹配元素中输入文本 | target(CSS选择器), text |
| screenshot | 截取当前页面为 PNG | output_path(可选) |
| get_text | 获取页面 body 文本内容 | 无 |
| go_back | 浏览器后退 | 无 |
| go_forward | 浏览器前进 | 无 |
| close | 关闭浏览器实例 | 无 |

## 前置条件

- 已安装 Firefox 浏览器
- 已安装 `selenium` 包（pip install selenium）
- geckodriver 在 PATH 中（selenium 4+ 可自动管理）

## 使用方式

```bash
python run.py --action open_url --target "https://www.baidu.com" --harness-dir <dir> --workdir <dir>
```

## 注意事项

- 浏览器实例在多次调用间保持（通过远程调试端口复用）
- 截图结果会以图片形式回传给 LLM
- CSS 选择器支持标准语法（#id, .class, tag[attr=val]）
