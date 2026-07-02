# PROJECT_MAP — Code Layout & Onboarding for AI Agents

This file gives any AI model (Claude, GPT, Gemini, local Llama, …) enough
structural context to work on this project without reading every byte.

Companion documents:
- `README.md` — user-facing overview
- `DECISIONS.md` — **read this first** for non-obvious bugs, fixes, and
  operating rules already agreed with the author

---

## 1. File tree snapshot

Sizes and line counts as of 2026-07-02 (main = `ad14aec`).

| File | KB | Lines | Purpose |
|---|---:|---:|---|
| `pcie_ch7_tool.py` | 203 | 2707 | Pure data + CLI. Four big dicts (TOC / Cap IDs / Register attrs / Register DB) plus `fuzzy_search()` and a small `interactive_mode()` REPL. **No Tk imports.** |
| `pcie_ch7_gui.py` | 62 | ~1400 | Tkinter GUI. One giant `run()` function with everything: theme, layout, sidebar Notebook, canvas, register cards, navigation, keyboard shortcuts. |
| `pcie_ch7_mcp.py` | 2 | — | Experimental MCP server wrapper. Not wired into GUI. |
| `run_gui.py` | <1 | — | `python run_gui.py` entry point. |
| `PCIe_Ch7_Reference.pyw` | <1 | — | Windows no-console double-click launcher. |
| `PCIe_ch7_tool.bat` | 1 | — | Legacy CLI-mode launcher. |
| `README.md` | 3 | — | User-facing docs + short AI-agents pointer. |
| `DECISIONS.md` | 6 | — | **Authoritative change log & operating rules.** |
| `PROJECT_MAP.md` | this file | — | Structural map + prompt templates. |
| `.gitignore` | 1 | — | Excludes `*.pdf`, `__pycache__/`, IDE files. |

**Not in git** (deliberately): the PCIe Base Specification PDF
(`NCB-PCI_Express_Base_5.0r1.0-2019-05-22.pdf`, ~11 MB). Users supply
their own copy — see README.

---

## 2. `pcie_ch7_gui.py` section map

Everything lives inside one enormous `run()` function starting at
**L59**. Use these anchors when you need to locate code:

| Line | What lives here |
|---:|---|
| L21–56 | Colour palette (`BG`, `SIDEBAR`, `ACCENT`, `ATTR_CLR` …) and `attr_color()` |
| L59 | `def run():` — top of the whole GUI |
| L69–88 | ttk style configuration (Treeview, TNotebook, TPanedwindow …) |
| L90–98 | Top bar (title + subtitle) |
| L100–105 | Nav-button holder `nav_frame`, PDF button holder |
| L107–135 | Search entry + placeholder logic |
| L123 | `_apply_placeholder()` |
| **L137–225** | **Main PanedWindow layout** (sidebar \| content) |
| L138 | `main = ttk.Panedwindow(root, orient="horizontal")` |
| L145 | `nb = ttk.Notebook(sidebar_wrap)` |
| L161 / L181 / L201 | `toc_tree` / `cap_tree` / `reg_tree` (`ttk.Treeview`) |
| L226–240 | Content canvas + scrollbar + `content_frame` |
| L250–265 | Status bar with hint line |
| L267–283 | **`clear_content()`** — unbinds `<Configure>` before destroy to avoid the O(N²) blowup (see DECISIONS.md) |
| L285–319 | Small helpers: `set_status`, `_kids`, `section_label`, `divider`, `info_row` |
| L321–387 | `bit_table()` — draws the 4-column bit-field table |
| L389–429 | `section_cards()` — child sections as clickable cards |
| L431–463 | `cap_badge()` — capability ID row (legacy, still used?) |
| L465–475 | `open_pdf(page)` — SumatraPDF or `os.startfile` |
| **L478–522** | **`_reg_header_bar()`** — Expand/Collapse-all pills + emits register cards |
| **L524–592** | **`_make_register_card()`** — lazy-built collapsible register card (bit table only constructed on first expand; kept in memory after collapse) |
| L594–637 | `_impl_welcome()` — home page |
| **L639–677** | **`_impl_section(sec)`** — main "show a chapter" implementation |
| **L679–714** | **`_impl_capability(cap_id)`** |
| **L716–760** | **`_impl_register(reg_name)`** |
| L762–835 | `_card_grid()` — search-results card wall |
| L837–965 | `_impl_search(query)` — Sections / Caps / Regs card walls |
| L967–989 | `_push_history()`, `_set_crumb()` |
| **L991–1029** | **`_select_toc/cap/reg()`** — programmatic sidebar sync. Uses `_prog_toc/cap/reg` markers (see next section) |
| **L1031–1090** | **`show_welcome/section/capability/register/search()`** — public navigation entry points. These wrap `_impl_*`, push history, sync sidebar, set breadcrumb, refresh nav buttons |
| L1092–1125 | `go_back()` |
| L1127–1145 | `_refresh_nav_buttons()` |
| L1147–1170 | Pre-computed `_sorted_secs` and `_sec_has_kid` (built once at startup) |
| L1170–1216 | `_populate_toc()` — O(N) filter (see DECISIONS.md, was O(N²)) |
| L1217–1240 | `_populate_cap()`, `_populate_reg()` |
| L1243–1265 | `_debounce_filter()` + `trace_add` wiring for the three filter boxes |
| **L1259–1300** | **`_on_toc/cap/reg_select()`** — `<<TreeviewSelect>>` handlers with `_prog_*` marker guard (the loop-fix). Never re-add a boolean `_suppress_sel` flag here — see DECISIONS.md |
| L1304–1321 | Search box `<KeyRelease>` handler (debounced 260 ms) |
| L1325–1346 | `_widget_scroll()` + `_on_mousewheel_global()` — single global wheel handler that finds the scrollable ancestor under the pointer |
| L1351–1390 | Keyboard shortcuts: `Ctrl+F`, `Esc`, `Alt+←`, `Ctrl+H`, `Ctrl+1/2/3`. `<Return>` is bound **only on `ent`**, NOT globally (see DECISIONS.md for why) |
| L1391–end | `_apply_placeholder()` call + `show_welcome(record=False)` + `root.mainloop()` |

**Rule of thumb:** if you're touching selection/history/sidebar sync,
reread the sections between L991 and L1300 and the "Sidebar infinite
loop" entry in DECISIONS.md before writing code.

---

## 3. `pcie_ch7_tool.py` schema

| Symbol | Line | Type | Count | Shape |
|---|---:|---|---:|---|
| `CHAPTER7_TOC` | L29 | `dict[str, dict]` | 238 | `{"7.5.1": {"title": str, "page": int}}` |
| `CAPABILITY_ID_MAP` | L271 | `dict[str, dict]` | 41 | `{"01h": {"name": str, "section": str}}` |
| `REGISTER_ATTRIBUTES` | L318 | `dict[str, str]` | ~9 | `{"RO": "Read only …", "RW1C": …}` |
| `REGISTER_DB` | L331 | `dict[str, dict]` | 163 | `{"link_control": {"section": "7.5.3.7", "offset": "10h", "page": 726, "bits": {"[0]": {"name": …, "attr": "RW", "desc": …}}}}` |

Search / utility functions (all pure, no Tk):

| Function | Line | Notes |
|---|---:|---|
| `search_toc(q)` | L2195 | Substring search over TOC |
| `search_keywords(q)` | L2204 | Loose keyword expansion |
| `_score_token_match(tokens, target)` | L2217 | Internal scoring |
| `fuzzy_search(q)` | L2223 | **Main entrypoint used by GUI.** Returns `{"sections": [...], "caps": [...], "registers": [...]}`; each element is `(id, info, score)` |
| `format_register_info(rn, rd)` | L2321 | Human-readable text dump |
| `cmd_*()` | L2356+ | CLI mode commands (`toc`, `search`, `section`, `reg`, `cap`, `attr`, `list_caps`, `help`) |
| `interactive_mode()` | L2623 | Blocking REPL |
| `main()` | L2689 | Argparse dispatcher |

If a user asks about a register field, **quote from `REGISTER_DB`**, do
not invent bit descriptions. If the field is not indexed, say so — the
tool covers ~163 registers, not every register in the PCIe spec.

---

## 4. Repo & agent rules (mirror of DECISIONS.md)

- **Auto-commit + push** after each completed task, unless user says
  "don't commit yet". Skip commits for questions, exploration, or
  half-finished work.
- **Never touch `--global` git config.** This repo has
  `user.name = andycool55`, `user.email = andycool5590380@gmail.com`
  set with `git config --local`. Global identity belongs to another
  account and must remain untouched.
- **Never commit the spec PDF.** `.gitignore` enforces `*.pdf`. Verify
  with `git check-ignore -v <filename>` if in doubt.
- **Ignore pyright/LSP false positives** about `_current = [None]`,
  `tk.StringVar()` `__setitem__`, and `Literal["nw"]` anchor types.
  Runtime is fine; these are inference limitations.
- **Don't reintroduce `bind_all("<Return>", …)`** — see DECISIONS.md.
- **Don't reintroduce boolean `_suppress_sel` flag** for tree
  selection — Tk `<<TreeviewSelect>>` is async, use value markers
  like `_prog_toc[0]` (already in place).

---

## 5. Prompt templates for handing this repo to another model

Pick one based on what you want the model to do. Copy the block verbatim.

### Template A — "Take over development" (new Claude / GPT / IDE agent)

Give the model these three files: `README.md`, `DECISIONS.md`,
`pcie_ch7_gui.py`. Skip `pcie_ch7_tool.py` (47 K tokens of data) unless
the task actually needs it.

```
I want you to take over an existing Python/Tkinter project. Please read
these three files first:
  1. README.md         — project overview and how to run
  2. DECISIONS.md      — MUST READ. Non-obvious bug fixes, agent
                         operating rules, known perf ceilings, and
                         things not yet done.
  3. PROJECT_MAP.md    — file tree, code section map with line numbers,
                         and this exact prompt template.
  4. pcie_ch7_gui.py   — main GUI (~1400 lines, all inside run()).
                         Data file pcie_ch7_tool.py is 200 KB and only
                         needed if you're modifying data.

After reading, please answer these five questions in 1-2 sentences each
so I can confirm you understood:
  (a) What does this tool do for the user?
  (b) What caused the sidebar TOC click freeze, and how was it fixed?
  (c) Why are register cards lazy-built and collapsible?
  (d) According to DECISIONS.md, which LSP warnings should be ignored?
  (e) What is the auto-commit rule, and when does it NOT apply?

Then wait for my next instruction. Do not modify any file yet.
```

### Template B — "Just answer questions about PCIe registers"

Give the model `pcie_ch7_tool.py` and `README.md`.

```
Attached is a Python data file (pcie_ch7_tool.py) that indexes PCI
Express 5.0 Base Specification Chapter 7. It contains four dicts:
  - CHAPTER7_TOC        (238 sections)
  - CAPABILITY_ID_MAP    (41 Capability IDs)
  - REGISTER_ATTRIBUTES  (RO, RW, RW1C, RWS, HwInit, RsvdP/Z ... )
  - REGISTER_DB          (163 registers with per-bit descriptions)

When I ask about a register, capability, or bit field:
  1. Quote the answer directly from REGISTER_DB / CAPABILITY_ID_MAP.
  2. Include: offset, section (§x.y.z), spec page, and every bit's
     (bits, name, attr, description) as a table.
  3. If the register or field is NOT indexed in the file, say
     "not indexed in this dataset" instead of inventing values.
  4. Do not invoke general PCIe knowledge; the dataset is authoritative
     for this conversation.

My question: <your question here>
```

### Template C — "First contact for a model that doesn't know opencode / your workflow"

Wrap Template A with the extra context below.

```
Background:
  This is a personal utility living at
  D:\WorkData\AI_Usage\PCIe_Ch7_QueryTool
  and mirrored on GitHub as andycool55/pcie-ch7-quickref (public).
  The author is a firmware engineer who needs quick lookup of PCIe 5.0
  Base Spec Chapter 7 register fields without scrolling 328 PDF pages.

Repo identity rules (IMPORTANT):
  - The repo has local user.name = andycool55,
    user.email = andycool5590380@gmail.com (set via git config --local).
  - The author's global git identity belongs to a separate work
    account; DO NOT modify --global config under any circumstances.
  - Verify identity with:  git config --local --get user.email

Now do the following:  <paste Template A here>
```

---

## 6. Quick "did you actually read" checklist

If a downstream model claims to have read this file, its answers should
survive these fact-checks:

1. `pcie_ch7_gui.py` is one big function called `run()` — **true**
2. There are exactly **three** Treeviews in the sidebar (TOC / Cap /
   Reg) — **true**
3. The bit table is built **on demand**, not up front — **true**
4. `<Return>` is bound only on the search entry, not `bind_all` — **true**
5. `REGISTER_DB` has **163** entries, `CHAPTER7_TOC` has **238**,
   `CAPABILITY_ID_MAP` has **41** — **true**
6. The tool ships with the PCIe spec PDF in the repo — **FALSE**
   (deliberately excluded; user supplies own copy)
7. The `_suppress_sel` boolean flag is the correct way to guard
   `<<TreeviewSelect>>` — **FALSE** (it was the bug; use `_prog_*`
   markers instead)

If a model answers 6 or 7 wrong, ask it to re-read DECISIONS.md.
