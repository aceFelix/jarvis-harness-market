# Jarvis Harness Market

J.A.R.V.I.S 官方自定义 harness 市场 — 让 Jarvis 操控更多桌面软件。

## 简介

本仓库提供 J.A.R.V.I.S 官方 harness 市场，用于控制 CLI-Anything 官方市场未覆盖的桌面软件。

每个 harness 是一个标准 Python 包，包含：
- `SKILL.md` — harness 定义（能力描述、参数、触发场景）
- `setup.py` — pip 打包配置（console_scripts 入口）
- `jarvis_harness_<id>/` — Python 包（cli.py 入口 + core/ 业务逻辑 + utils/ 工具层）
- `run.py` — 向后兼容入口（支持目录复制安装方式）

## 可用 Harness

| ID | 软件 | 控制方式 | 全局命令 | 状态 |
|----|------|----------|----------|------|
| wps | WPS Office | COM 自动化 (win32com) | `jarvis-harness-wps` | ✅ 可用 |
| qq | QQ 桌面版 | pywinauto + pyautogui | — | 框架 |
| wechat | 微信桌面版 | pywinauto + pyautogui | — | 框架 |
| firefox | Firefox 浏览器 | Selenium WebDriver | — | 框架 |
| xmind | Xmind 思维导图 | 文件操作 (.xmind=zip) | — | 框架 |

## 安装方式

### 通过 Jarvis 命令安装（推荐）

```bash
# 在 Jarvis REPL 中执行
/cli_anything market          # 查看可用 harness
/cli_anything install wps     # 安装 WPS harness（自动 pip install + 迁移 SKILL.md）
/cli_anything install qq      # 安装 QQ harness
```

### pip 安装（对齐官方 CLI-Anything）

```bash
# 从 GitHub 直接安装
pip install git+https://github.com/aceFelix/jarvis-harness-market.git#subdirectory=harnesses/wps

# 或本地开发安装
cd harnesses/wps
pip install -e .
```

安装后即可使用全局命令：

```bash
jarvis-harness-wps version
jarvis-harness-wps status
jarvis-harness-wps writer --action open_doc --target "C:\Users\me\报告.docx"
jarvis-harness-wps --subcommand "sheet --action read_cell --target test.xlsx --cell A1" --json
```

### 手动安装（目录复制，向后兼容）

将 `harnesses/<id>/` 目录复制到 `~/.jarvis/cli_anything/<id>/`：

```bash
# Windows
xcopy /E harnesses\wps %USERPROFILE%\.jarvis\cli_anything\wps\

# macOS/Linux
cp -r harnesses/wps ~/.jarvis/cli_anything/wps/
```

此方式通过 `python run.py ...` 调用，无需 pip 安装。

## 配置

在 `~/.jarvis/settings.toml` 中配置自定义市场源：

```toml
[cli_anything]
market_url = "https://raw.githubusercontent.com/<user>/jarvis-harness-market/main"
market_local = "path/to/jarvis-harness-market"
```

Jarvis 加载顺序：自定义市场远程 → 官方 CLI-Anything → 本地回退。

## 开发指南

### 添加新 harness（pip 包模式，推荐）

1. 在 `harnesses/` 下创建新目录（如 `harnesses/dingtalk/`）
2. 创建 Python 包 `jarvis_harness_dingtalk/`：
   ```
   harnesses/dingtalk/
   ├── jarvis_harness_dingtalk/
   │   ├── __init__.py        # 版本号
   │   ├── __main__.py        # python -m 入口
   │   ├── cli.py             # CLI 主入口（argparse）
   │   ├── core/              # 业务逻辑
   │   │   ├── __init__.py
   │   │   └── messenger.py
   │   └── utils/             # 底层工具
   │       ├── __init__.py
   │       └── backend.py
   ├── setup.py               # pip 打包（console_scripts 入口）
   ├── run.py                 # 向后兼容入口
   └── SKILL.md               # harness 定义
   ```
3. 编写 `setup.py`（entry_points 定义全局命令 `jarvis-harness-<id>`）
4. 编写 `SKILL.md`（command 字段填全局命令名）
5. 在 `registry.json` 中添加条目（含 `install_cmd` 字段）
6. 提交并推送

### setup.py 模板

```python
from setuptools import setup, find_packages

setup(
    name="jarvis-harness-dingtalk",
    version="1.0.0",
    packages=find_packages(include=["jarvis_harness_dingtalk", "jarvis_harness_dingtalk.*"]),
    entry_points={
        "console_scripts": [
            "jarvis-harness-dingtalk=jarvis_harness_dingtalk.cli:main",
        ],
    },
    install_requires=[...],
)
```

### CLI 调用规范

```bash
# 直接子命令格式
jarvis-harness-<id> <component> --action <操作> [--target <对象>] [--json]

# jarvis runner 格式（--subcommand 字符串）
jarvis-harness-<id> --subcommand "<component> --action <操作> [options]" --json

# 输出格式（stdout JSON）
{"status": "ok", "action": "send_msg", "result": "..."}
{"status": "error", "action": "send_msg", "error": "..."}
```

### registry.json 条目格式

```json
{
  "id": "dingtalk",
  "display_name": "钉钉",
  "description": "...",
  "requires": "pywinauto",
  "skill_md": "harnesses/dingtalk/SKILL.md",
  "install_cmd": "pip install git+https://github.com/aceFelix/jarvis-harness-market.git#subdirectory=harnesses/dingtalk"
}
```

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](./LICENSE) 文件。
