# PCIe 5.0 Chapter 7 Quick Reference

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

The tool references page numbers in the official spec PDF. It is **not**
included in this repo due to copyright. Download the PCI Express Base
Specification revision 5.0 from
[pcisig.com](https://pcisig.com/specifications) (members only) and place it
next to the scripts as:

```
NCB-PCI_Express_Base_5.0r1.0-2019-05-22.pdf
```

If the PDF is missing the GUI still works — you just won't be able to jump
into the actual spec page.

*(Optional)* Install [SumatraPDF](https://www.sumatrapdfreader.org/) for
per-page deep-linking; otherwise the PDF opens at page 1 with your default
reader.

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
| `pcie_ch7_tool.py` | All data (TOC, Cap IDs, Registers, bit fields) + fuzzy search functions. Pure-Python, no deps. |
| `pcie_ch7_gui.py` | Tkinter GUI. Renders everything and handles navigation. |
| `run_gui.py` | Simple entry point (`python run_gui.py`). |
| `PCIe_Ch7_Reference.pyw` | Windows no-console launcher (double-click). |
| `PCIe_ch7_tool.bat` | Batch launcher (legacy CLI mode). |
| `pcie_ch7_mcp.py` | MCP server wrapper (experimental). |

## License

TBD — pick one before making the repo widely known.

## Disclaimer

This tool is an independent quick-reference aid. Register layouts and bit
descriptions are transcribed from the public PCIe 5.0 Base Specification but
should be cross-checked against the official spec for anything
safety- or compliance-critical. **The spec is authoritative; this tool is not.**
