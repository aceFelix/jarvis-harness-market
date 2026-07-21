# Jarvis Harness Market

J.A.R.V.I.S 官方 harness 市场 — 让 Jarvis 操控更多桌面软件。

## 简介

本仓库提供 J.A.R.V.I.S 的官方 harness 市场，用于控制 CLI-Anything 官方市场未覆盖的桌面软件。

每个 harness 包含：
- `SKILL.md` — harness 定义（能力描述、参数、触发场景）
- `run.py` — 执行入口（接收 `--action`、`--target` 等参数）

## 可用 Harness

| ID | 软件 | 控制方式 | 状态 |
|----|------|----------|------|
| qq | QQ 桌面版 | pywinauto + pyautogui | 框架 |
| wechat | 微信桌面版 | pywinauto + pyautogui | 框架 |
| firefox | Firefox 浏览器 | Selenium WebDriver | 框架 |
| wps | WPS Office | COM 自动化 (win32com) | 框架 |
| xmind | Xmind 思维导图 | 文件操作 (.xmind=zip) | 框架 |

## 安装方式

### 通过 Jarvis 命令安装（推荐）

```bash
# 在 Jarvis REPL 中执行
/cli_anything market          # 查看可用 harness
/cli_anything install qq      # 安装 QQ harness
/cli_anything install wechat  # 安装微信 harness
```

### 手动安装

将 `harnesses/<id>/` 目录复制到 `~/.jarvis/cli_anything/<id>/`：

```bash
# Windows
xcopy /E harnesses\qq %USERPROFILE%\.jarvis\cli_anything\qq\

# macOS/Linux
cp -r harnesses/qq ~/.jarvis/cli_anything/qq/
```

## 配置

在 `~/.jarvis/settings.toml` 中配置自定义市场源：

```toml
[cli_anything]
market_url = "https://raw.githubusercontent.com/<user>/jarvis-harness-market/main"
market_local = "path/to/jarvis-harness-market"
```

Jarvis 加载顺序：自定义市场远程 → 官方 CLI-Anything → 本地回退。

## 开发指南

### 添加新 harness

1. 在 `harnesses/` 下创建新目录（如 `harnesses/dingtalk/`）
2. 编写 `SKILL.md`（frontmatter 必须包含 id、name、description、command）
3. 编写 `run.py`（解析参数，输出 JSON 结果）
4. 在 `registry.json` 的 `harnesses` 数组中添加条目
5. 提交并推送

### run.py 规范

```python
# 接收参数
--action <操作类型>    # 必填
--target <操作对象>    # 可选
--harness-dir <路径>   # harness 所在目录（自动注入）
--workdir <路径>       # 当前工作目录（自动注入）

# 输出格式（stdout JSON）
{"status": "ok", "action": "send_msg", "result": "..."}
{"status": "error", "action": "send_msg", "error": "..."}
```

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](./LICENSE) 文件。
