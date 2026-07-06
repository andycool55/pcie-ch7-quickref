# AGENTS.md - OpenCode Agent Guide

## 專案概述
這是一個用 Tkinter 建構的桌面 GUI，用來瀏覽 PCIe 5.0 基礎規格第 7 章（軟體初始化與設定）。

## Agent 需知的重要事實

### 執行指令
- `python run_gui.py` - 主要進入點
- `python PCIe_Ch7_Reference.pyw` - Windows 無 console 啟動器（雙擊）
- `PCIe_ch7_tool.bat` - 舊版 CLI 模式啟動器

### 儲存庫規則（來自 DECISIONS.md）
- **永不修改 `--global` git 配置** - 所有身分識別都是透過 `git config --local` 
- **永遠不要提交規格 PDF** - `*.pdf` 被 `.gitignore` 排除
- **忽略 pyright/LSP 的誤報** 關於 `_current = [None]` 和 `tk.StringVar()` `__setitem__` 
- **不要重新引入 `bind_all("<Return>", …)`** - 請參閱 DECISIONS.md 了解原因
- **不要重新引入布林值 `_suppress_sel` 標記** - 改用 `_prog_*` 值標記

### 架構說明
- `pcie_ch7_tool.py` - 純數據檔案，包含 4 個字典（TOC、能力 ID、寄存器屬性、寄存器資料庫）加上搜尋功能。沒有 Tkinter 匯入。
- `pcie_ch7_gui.py` - 主 GUI 檔案，包含一個巨大的 `run()` 函數（約 1400 行）包含所有 GUI 邏輯
- `run_gui.py` - 簡單的進入點（`python run_gui.py`）
- `PCIe_Ch7_Reference.pyw` - Windows 無 console 啟動器（雙擊）
- `PCIe_ch7_tool.bat` - 舊版 CLI 模式啟動器

### 重要錯誤/修復（來自 DECISIONS.md）
1. **側邊欄無限 `<<TreeviewSelect>>` 迴圈** - 透過使用 `_prog_*` 值標記代替布林值 `_suppress_sel` 來修復
2. **延遲建構的可折疊寄存器卡片** - 在首次展開時建構，在收合時快取
3. **`clear_content()` O(N²) 爆炸** - 在刪除迴圈前卸載 `<Configure>` 處理常式
4. **全域 `<Return>` 綁定** - 僅綁定在搜尋輸入框，而非全域
5. **滑鼠滾輪爭用** - 在 root 上使用單一全域 `<MouseWheel>` 處理常式

### 資料結構
- `CHAPTER7_TOC`：238 個章節
- `CAPABILITY_ID_MAP`：41 個能力 ID  
- `REGISTER_ATTRIBUTES`：約 9 個屬性（RO、RW、RW1C 等）
- `REGISTER_DB`：163 個寄存器，含每位元描述

### 特殊需求
- 必須自己取得 PCIe 基礎規格 PDF（不包含在儲存庫中）
- 檔名必須為：`NCB-PCI_Express_Base_5.0r1.0-2019-05-22.pdf`
- 當前 PDF 啟動捷徑僅適用 Windows（使用 `os.startfile` 及可選的 `C:\Program Files\SumatraPDF\SumatraPDF.exe`）

### 測試/驗證
- 沒有特定測試指令 - 依賴手動 GUI 測試
- 所有資料處理發生在 `pcie_ch7_tool.py`（純 Python，無相依套件）