# OpenCode Go · Windows 版

> [macOS 版](https://github.com/Steve233333/OpenCodeGoWidget) 的 Windows 端实现，共用同一套设计 token 和数据引擎。

## 范围

**做**

- 主面板：三档额度（5 小时 / 周 / 月）、按日按模型堆叠花费图、今日模型占比、Go 全模型配额表
- 托盘常驻：左键弹出迷你面板，右键菜单（打开主面板 / 检查更新 / 开机自启 / 退出）
- 一键配置 Codex：写入 `config.toml`、`models.json`、`AGENTS.md`，安装 MCP 搜索与本地代理，注册模型自动发现
- 设置页：API Key 管理、浏览器登录自动获取 Key

**不做**

- Windows 官方小组件（要 MSIX 打包走 Store，且只能画 Adaptive Cards，图表画不了）
- 桌面常驻小窗（用户明确不要）
- 双开副本 / 打补丁：macOS 版靠复制 `ChatGPT-Patched.app` 绕过模型过滤，Windows 上直接配置 Codex，不做副本

## 主界面原型

在仓库根目录起个本地服务，然后浏览器打开：

```sh
python3 -m http.server 8765 --bind 127.0.0.1
# 打开 http://127.0.0.1:8765/prototype/index.html
```

原型用演示数据渲染，配额表数字取自 macOS 版 2026-09-16 的真实截图，方便和原生版并排逐像素比对。

> 直接双击打开 `prototype/index.html` 时，浏览器可能因 `file://` 策略加载不到样式，用上面的本地服务最稳。

## 设计 token 管线

配色和尺寸不手抄，从 macOS 版源码自动生成，两边不会漂移：

```sh
python3 tools/extract_tokens.py --source /path/to/OpenCodeGoWidget
```

会写出 `design/tokens.json`（结构化）和 `design/tokens.css`（CSS 变量）。macOS 版改了配色或布局，重跑一次即可。

来源：`Sources/ModelPalette.swift` 的 39 项模型配色、`Sources/GoQuotaChart.swift` 的配额三段色，以及 `Sources/App.swift` 里的间距与字号。

## 配额图坐标轴

和 macOS 版同一套公式（官网同款对数刻度）：

```
位置(倍率) = 24 + pow(log10(倍率) / log10(最大倍率), 2.2) × (宽度 − 24)
```

倍率以月配额最低的模型为 1x 基准，刻度候选 1x/5x/10x/25x/50x/100x/250x/500x，相邻刻度间距不足 30px 时自动隐藏。柱内三段按线性比例切分：红=5h、橙=周（扣掉 5h）、绿=月（扣掉周）。

## 构建 Windows exe

**不需要 Windows 机器**，在 macOS 上就能交叉编译（靠 .NET 的 `EnableWindowsTargeting`）：

```sh
# 首次先装 SDK（用户目录，不用 sudo）
curl -sSL https://dot.net/v1/dotnet-install.sh | bash -s -- --channel 8.0

export PATH="$HOME/.dotnet:$PATH"
cd src/OpenCodeGoWidget.Windows
dotnet publish -c Release
```

产物在 `bin/Release/net8.0-windows/win-x64/publish/OpenCodeGoWidget.exe`。

exe 自带 .NET 运行时（约 155 MB，zip 后约 63 MB），目标机器不需要装任何东西；界面用系统自带的 WebView2（Win11 预装）。

### 当前这一版能干什么

- 托盘常驻：左键开面板，右键菜单为「打开主面板 / 设置… / 退出」
- 主面板与设置面板的完整界面（就是 `prototype/` 里的两屏）
- 关窗口收进托盘，不退出进程（和 macOS 版一致）

### 还没接的

数据引擎（配额抓取、费用统计）、Codex 一键配置、浏览器登录自动获取 Key。

## 目录

```
design/      设计 token（自动生成，勿手改）
prototype/   主界面 HTML 原型
src/         .NET + WebView2 的 Windows 壳
tools/       扒 token、生成 ico 的脚本
docs/        设计决策与移植笔记
```

## 待定

- **Python 运行时**：本地代理和模型自动发现是 Python 脚本，Windows 默认没有 Python。是内嵌一个运行时（约 20MB）还是让用户自己装，待定。
- **模型过滤**：macOS 版要给 ChatGPT 副本打补丁才能看到自定义模型；Windows 版直接写 Codex 配置是否足够，需要在真机验证。
- **壳**：pywebview（全 Python，复用引擎最省事）还是 Tauri（窗口效果更好），等原型定稿再选。
