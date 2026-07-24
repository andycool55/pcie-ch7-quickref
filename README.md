# PCIe 5.0 Chapter 7 Quick Reference

**Languages:** English (below) · [繁體中文](#-繁體中文) · [`README.zh-TW.md`](README.zh-TW.md)

---

## ⚠️ Required: You must obtain the PCIe Base Specification PDF yourself

This tool references page numbers in the **PCI Express Base Specification
Revision 5.0**. Due to PCI-SIG copyright, **the PDF is NOT bundled in
this repository** (see [`.gitignore`](.gitignore)).

Before running the GUI, download the spec and save it in the project root as:

```
NCB-PCI_Express_Base_5.0r1.0-2019-05-22.pdf
```

**Where to get the PDF (official sources only):**

| You are | Where to go | Cost |
|---|---|---|
| **PCI-SIG member** (member company employees) | [PCI-SIG Specification Library](https://pcisig.com/specifications) → filter Technology = *PCI Express*, Revision = *5.0*, Document Type = *Specification*. Members log in and download directly. | Free |
| **Non-member** | [PCI-SIG Specification Order Form](https://pcisig.com/specifications/order-form) | Paid purchase |
| **General info** | [PCI-SIG main site](https://pcisig.com/) · [PCI Express on Wikipedia](https://en.wikipedia.org/wiki/PCI_Express) | Free (info only, no spec PDF) |

If the PDF is missing the GUI still works — every register table, section
tree, and search still functions — you just won't be able to click
"📄 Open PDF" to jump into the actual spec page. See the
[Setup](#setup) section for details.

> ⚠️ **PCI-SIG legal notice (copied from pcisig.com/specifications):**
> PCI-SIG Specifications shall not be used for the purpose of creating,
> training, enhancing, developing, maintaining, or contributing to any
> commercially available Artificial Intelligence systems without the
> express, written consent of PCI-SIG. This tool is a personal
> quick-reference aid, not a commercial AI system — but please respect
> PCI-SIG's terms if you fork or extend it.

---

> **For AI Agents / LLMs reading this repo:** please read
> **[`DECISIONS.md`](DECISIONS.md)** first (non-obvious bug fixes and
> operating rules), then **[`PROJECT_MAP.md`](PROJECT_MAP.md)** (file tree,
> code section map with line numbers, and copy-paste prompt templates for
> handing this repo to another model). Ready-made prompts for three common
> scenarios live at the end of `PROJECT_MAP.md`. Key rules:
> - **Never** modify `--global` git config; per-repo identity is set with
>   `git config --local` and must not leak into the author's other account.
> - **Never** commit the PCIe base-spec PDF (`.gitignore` enforces `*.pdf`).
> - Pyright / LSP warnings about `_current = [None]` and `tk.StringVar`
>   `__setitem__` are runtime-safe false positives — leave them alone.
> - Do NOT reintroduce a boolean `_suppress_sel` flag for tree selection,
>   and do NOT `bind_all("<Return>", …)` globally. Both were bugs; see
>   `DECISIONS.md`.

A Tkinter-based desktop GUI for browsing **Chapter 7 (Software Initialization
and Configuration)** of the *PCI Express Base Specification 5.0 r1.0*.

Instead of scrolling 328 pages of PDF looking for a bit-field, this tool gives
you:

- A **left sidebar** with three tabs — full **TOC tree**, **Capability ID**
  lookup, and a flat **Register list** — each with an instant filter box.
- A **right content pane** that renders any register's bit-fields as a
  structured, colour-coded table (attribute badges: `RO`, `RW`, `RW1C`, …).
- **Fuzzy search** across sections / capabilities / registers.
- One-click **Open PDF** at the current spec page (via SumatraPDF if installed,
  else your system default PDF reader).

## Screenshots

*(TBD — add a screenshot of the main window and a bit-field table.)*

## Features

- ~238 indexed sections, 41 Capability IDs, 163 registers with full bit-field
  details baked into the tool (no PDF parsing at runtime).
- Collapsible register cards (lazy-built) so even large sections like §7.5
  (54 registers, 276 bit fields) open instantly.
- Keyboard shortcuts:
  - `Ctrl+F` — focus search box
  - `Esc` — clear search / back to home
  - `Ctrl+H` — Home
  - `Alt+←` — Back
  - `Ctrl+1 / 2 / 3` — switch sidebar tab (TOC / Cap IDs / Registers)
- Debounced search & filter boxes (no lag while typing).
- Dark theme tuned for long reading sessions.

## Requirements

- **Python 3.10+** (tested on 3.14). Uses only the standard library
  (`tkinter`, `os`, `subprocess`).
- **Windows** for the current PDF-launch shortcut (uses `os.startfile` and
  optionally `C:\Program Files\SumatraPDF\SumatraPDF.exe`). Trivially portable
  to macOS/Linux by replacing `open_pdf()`.

## Setup

### 1. Get the PCIe Base Spec PDF

See the ⚠️ block at the very top of this README for official sources.
Save the file next to the scripts as:

```
NCB-PCI_Express_Base_5.0r1.0-2019-05-22.pdf
```

If the PDF is missing the GUI still works — you just won't be able to jump
into the actual spec page.

*(Optional)* Install [SumatraPDF](https://www.sumatrapdfreader.org/) for
per-page deep-linking; otherwise the PDF opens at page 1 with your default
reader.

### 1.1 Quickly switch to a newer PCIe spec (6.0/7.0...)

This project now supports version switching via one config file:

- Use the top-bar profile dropdown to switch spec immediately in UI.
- To add future versions, edit `app/pcie_spec_config.py` and add a profile in
  `SPEC_PROFILES`.
- Full step-by-step: `SPEC_UPGRADE_GUIDE.md`.

Temporary override via environment variable:

```powershell
$env:PCIE_SPEC_PDF = "D:\Path\To\NCB-PCI_Express_Base_6.0r1.0-YYYY-MM-DD.pdf"
python run_gui.py
```

### 2. Clone & run

```powershell
git clone https://github.com/andycool55/pcie-ch7-quickref.git
cd pcie-ch7-quickref
python run_gui.py
```

Or double-click `PCIe_Ch7_Reference.pyw` on Windows for a no-console launch.

## File layout

| File | Purpose |
|---|---|
| `app/` | Non-entry application package (GUI, data, spec config, MCP wrapper). |
| `app/pcie_ch7_tool.py` | All data (TOC, Cap IDs, Registers, bit fields) + fuzzy search functions. Pure-Python, no deps. |
| `app/pcie_ch7_gui.py` | Tkinter GUI. Renders everything and handles navigation. |
| `run_gui.py` | Simple entry point (`python run_gui.py`). |
| `PCIe_Ch7_Reference.pyw` | Windows no-console launcher (double-click). |
| `PCIe_ch7_tool.bat` | Batch launcher (legacy CLI mode). |
| `app/pcie_ch7_mcp.py` | MCP server wrapper (experimental). |
| `DECISIONS.md` | Change log + non-obvious bug fixes + agent rules. |
| `PROJECT_MAP.md` | File tree, code section map, prompt templates. |

## License

TBD — pick one before making the repo widely known.

## Disclaimer

This tool is an independent quick-reference aid. Register layouts and bit
descriptions are transcribed from the public PCIe 5.0 Base Specification but
should be cross-checked against the official spec for anything
safety- or compliance-critical. **The spec is authoritative; this tool is not.**

---

# 🌏 繁體中文

（English version above · 也可直接讀 [`README.zh-TW.md`](README.zh-TW.md)）

## ⚠️ 必要條件：你必須自行下載 PCIe Base 規格 PDF

本工具會參照 **PCI Express Base Specification Revision 5.0**（PCIe 5.0
基礎規格）的頁碼。由於 PCI-SIG 版權規範，**本 repo 不包含 PDF 檔**
（`.gitignore` 排除 `*.pdf`）。

執行 GUI 之前，請下載規格並存放在專案根目錄，檔名必須為：

```
NCB-PCI_Express_Base_5.0r1.0-2019-05-22.pdf
```

**PDF 官方取得管道（唯一合法來源）：**

| 你的身份 | 前往 | 費用 |
|---|---|---|
| **PCI-SIG 會員**（會員公司員工） | [PCI-SIG Specification Library](https://pcisig.com/specifications)：篩選 Technology = *PCI Express*、Revision = *5.0*、Document Type = *Specification*。會員登入後可直接下載。 | 免費 |
| **非會員** | [PCI-SIG Specification 訂購表單](https://pcisig.com/specifications/order-form) | 付費購買 |
| **一般資訊** | [PCI-SIG 官網](https://pcisig.com/) · [PCI Express 維基百科](https://zh.wikipedia.org/wiki/PCI_Express) | 免費（僅資訊，無規格 PDF） |

**如果查不到你公司是不是會員？** 到 [PCI-SIG Member Companies
列表](https://pcisig.com/membership/member-companies) 查詢。SSD / 半導體 /
主機板 / CPU / OS 廠商幾乎都是會員；如果你在這類公司任職，通常公司內部
IT 或韌體團隊已經有這份 PDF，先問內部再說。

若 PDF 缺失，GUI 仍可正常運作——所有 register 表格、章節樹、搜尋功能
都正常——只是無法點「📄 Open PDF」跳到規格對應頁碼而已。詳見下方
[安裝](#安裝)。

> ⚠️ **PCI-SIG 法律聲明**（引自 pcisig.com/specifications）：
> 未經 PCI-SIG 書面同意，PCI-SIG 規格不得用於建立、訓練、增強、開發、
> 維護或貢獻任何商業性人工智慧系統。本工具僅為個人查詢輔助，非商業
> AI 系統——但若你要 fork 或延伸使用，請務必遵守 PCI-SIG 條款。

---

一個以 Tkinter 建構的桌面 GUI，用來瀏覽
**PCI Express Base Specification 5.0 r1.0** 的
**Chapter 7（Software Initialization and Configuration，軟體初始化與組態）**。

不用翻 328 頁 PDF 找某個 bit field，這個工具提供：

- **左側 sidebar** 有三個分頁：完整**章節樹（TOC）**、**Capability ID**
  查詢、扁平的 **Register 列表**——每個分頁都有即時過濾框。
- **右側內容區**：任一 register 的 bit fields 會以結構化、彩色標示的
  表格呈現（attribute badge：`RO`, `RW`, `RW1C`, …）。
- **模糊搜尋**：跨章節 / capabilities / registers。
- 一鍵**開啟 PDF** 直接跳到當前規格頁碼（若有裝 SumatraPDF 就用它，
  否則呼叫系統預設 PDF 閱讀器）。

## 螢幕截圖

*(待補——之後放主視窗和 bit-field 表格截圖)*

## 功能特色

- 索引了約 238 個章節、41 個 Capability ID、163 個 register 完整 bit-field
  資訊全部內建在工具裡（不需要 runtime 解析 PDF）。
- 可折疊的 register cards（懶載入），因此開啟像 §7.5（54 registers、
  276 bit fields）這種大章節也是**瞬間顯示**。
- 快捷鍵：
  - `Ctrl+F` — 聚焦搜尋框
  - `Esc` — 清空搜尋 / 回首頁
  - `Ctrl+H` — 首頁
  - `Alt+←` — 上一頁
  - `Ctrl+1 / 2 / 3` — 切換左側 sidebar 分頁（TOC / Cap IDs / Registers）
- 搜尋框、過濾框都有 debounce（打字不卡頓）。
- 深色主題，適合長時間閱讀。

## 系統需求

- **Python 3.10 以上**（在 3.14 測試過）。只用標準函式庫
  （`tkinter`, `os`, `subprocess`）。
- **Windows**（因為目前的 PDF 開啟捷徑用 `os.startfile`，並可選用
  `C:\Program Files\SumatraPDF\SumatraPDF.exe`）。要移植到 macOS/Linux
  只需要改寫 `open_pdf()` 函式即可。

## 安裝

### 1. 取得 PCIe Base 規格 PDF

請看本 README 最上方的 ⚠️ 區塊，那裡列了官方取得管道。下載完
存到專案根目錄，檔名必須是：

```
NCB-PCI_Express_Base_5.0r1.0-2019-05-22.pdf
```

如果 PDF 沒有，GUI 依然能執行——只是無法跳到規格頁碼。

*(可選)* 安裝 [SumatraPDF](https://www.sumatrapdfreader.org/) 就能精準
跳頁；沒裝的話會用你的系統預設 PDF 閱讀器打開第 1 頁。

### 2. Clone 與執行

```powershell
git clone https://github.com/andycool55/pcie-ch7-quickref.git
cd pcie-ch7-quickref
python run_gui.py
```

或者在 Windows 上雙擊 `PCIe_Ch7_Reference.pyw`（無 console 視窗）。

## 檔案結構

| 檔案 | 用途 |
|---|---|
| `app/` | 非入口程式整合資料夾（GUI、資料、規格設定、MCP wrapper）。 |
| `app/pcie_ch7_tool.py` | 所有資料（TOC、Cap IDs、Registers、bit fields）+ 模糊搜尋函式。純 Python，無外部相依。 |
| `app/pcie_ch7_gui.py` | Tkinter GUI，畫面渲染與導航都在這裡。 |
| `run_gui.py` | 簡單的進入點（`python run_gui.py`）。 |
| `PCIe_Ch7_Reference.pyw` | Windows 無 console 啟動器（雙擊）。 |
| `PCIe_ch7_tool.bat` | 舊版 CLI 模式的 batch 啟動器。 |
| `app/pcie_ch7_mcp.py` | MCP server 包裝（實驗性質）。 |
| `DECISIONS.md` | 變更紀錄 + 非顯而易見的 bug 修法 + agent 規則。 |
| `PROJECT_MAP.md` | 檔案樹、程式碼區段導覽、prompt 範本。 |

## 授權

待定——公開推廣前應該選一個。

## 免責聲明

本工具是獨立的快速查詢輔助。Register 布局與 bit 說明是從公開的 PCIe 5.0
Base Specification 轉錄而來，但**任何攸關安全性或合規性的用途**都應該對
照官方規格再次確認。**規格才是權威，本工具不是**。
