# Decisions & Change Log

Short record of significant design decisions and non-obvious bug fixes for
this project. Chronological order (newest first). Use this to catch up on
project state without replaying the whole conversation history.

---

## 2026-07-02  ·  Sidebar infinite `<<TreeviewSelect>>` loop
**Commit:** `d7253df`
**Symptom:** Clicking any TOC item in the left sidebar froze the UI, even for
section §7.1 (which has zero registers to render). Perf logging showed
`show_section('7.1')` was called **200+ times per click**.

**Root cause:** `_suppress_sel` boolean guarded with `try/finally` was
ineffective because Tk dispatches `<<TreeviewSelect>>` **asynchronously**
(events are queued, handler runs later). By the time the handler executed,
the `finally` had already reset the flag to `False`, so every programmatic
`selection_set()` re-entered `show_section()` → `_select_toc()` →
`selection_set()` → …

**Fix** (see `pcie_ch7_gui.py:970-1020, 1268-1300`):
- Dropped `_suppress_sel` entirely.
- Added per-tree markers: `_prog_toc / _prog_cap / _prog_reg` that remember
  the iid we programmatically selected.
- `<<TreeviewSelect>>` handler compares incoming selection against the
  marker; if they match, consume the marker and short-circuit.
- Additional guard: `_select_*()` reads current selection first and skips
  `selection_set()` entirely when the tree is already on the target iid.

**Lesson:** Never guard Tk virtual events with synchronous `try/finally`
flags — use *value* markers instead.

---

## 2026-07-02  ·  Lazy-built collapsible register cards
**Commit:** included in `fc3267a` (initial).
**Symptom:** Opening a register-heavy section like §7.5 (54 registers, 276
bit fields) built ~1374 widgets synchronously, freezing the UI for
several seconds.

**Fix:** `_reg_header_bar` + `_make_register_card` render only the header
row for each register (~3 widgets each). Bit tables are constructed **on
first expand** (`state.built` flag) and cached (`pack_forget` on collapse,
not destroy). `Expand all` is capped at 60 registers with a status-bar
warning to prevent accidental thousand-widget builds.

## 2026-07-02  ·  `clear_content()` O(N²) blowup
**Commit:** included in `fc3267a`.
**Root cause:** Each widget destroyed inside `content_frame` triggered a
`<Configure>` on the parent, which called `canvas.bbox("all")` — an O(N)
scan across all remaining widgets. Destroying N widgets was O(N²).

**Fix:** Detach the `<Configure>` handler before the destroy loop, rebind
after all children are gone. One final recalc instead of N. See
`pcie_ch7_gui.py:272-283`.

## 2026-07-02  ·  Global `<Return>` binding hijacked all Enter presses
**Commit:** included in `fc3267a`.
**Root cause:** `root.bind_all("<Return>", _open_pdf_shortcut)` caught
Enter from every widget (sidebar filter boxes, tree nodes, notebook tabs),
producing "the UI stopped responding" symptoms.

**Fix:** Bind `<Return>` only on the search entry (`ent.bind`). Keep other
shortcuts (`Ctrl+F`, `Esc`, `Alt+←`, `Ctrl+H`, `Ctrl+1/2/3`) as `bind_all`
because they're modifier combos that don't clash with widget defaults.

## 2026-07-02  ·  MouseWheel churn on every hover
**Commit:** included in `fc3267a`.
**Root cause:** `canvas.<Enter>` / `<Leave>` reflexively called
`bind_all("<MouseWheel>")` / `unbind_all(...)`. This clobbered the
Treeview's own wheel handling permanently.

**Fix:** Single global `<MouseWheel>` handler on root. It walks up from
`event.widget` looking for a scrollable ancestor (Canvas / Treeview /
Text / Listbox) and dispatches to whichever is under the cursor.

---

## 2026-07-02  ·  Repo setup
**Repo:** https://github.com/andycool55/pcie-ch7-quickref (public)
**Identity for this repo only:**
- `user.name  = andycool55`
- `user.email = andycool5590380@gmail.com`

Set with `git config --local` — **global config
(`andy_hong@phison.com`) is deliberately untouched**. Verify with
`git config --local --get user.email`.

**Excluded from git** (see `.gitignore`):
- `*.pdf` — PCIe base spec is copyright, users must supply their own copy
  named `NCB-PCI_Express_Base_5.0r1.0-2019-05-22.pdf` in the project root
- `__pycache__/`, `*.pyc`, `.venv/`, IDE settings, logs

## 2026-07-02  ·  Left sidebar was missing in the original GUI
**Context:** The initial `pcie_ch7_gui.py` had no left panel at all despite
the welcome page's "How to use" text referencing three sidebar tabs. The
UI had only a top bar + single scrolling content canvas.

**Fix:** Rebuilt as `ttk.Panedwindow` with a resizable `ttk.Notebook` on
the left:
- 📚 **TOC** — 238 sections, tree view with instant filter (O(N) match
  computation, not O(N²))
- 🔌 **Cap IDs** — 41 capability ID list
- 📋 **Regs** — 163 register list

Filter boxes are debounced 180 ms. Breadcrumb bar shows current
navigation path. `Alt+←` (back) and `Ctrl+H` (home) walk a history stack
capped at 100 entries. Placeholder text in the search box is guarded
against being treated as a real query.

---

## Operating rules (agent behavior)

- **Auto-commit + push** after each completed task (unless user says "don't
  commit yet"). Not for questions or half-finished work.
- **Never touch `--global` git config.** All identity is per-repo.
- **Never commit the spec PDF** (`.gitignore` enforces this;
  `git check-ignore` confirms).
- **LSP type warnings** produced by pyright about `_current = [None]` and
  `tk.StringVar()` `__setitem__` are runtime-safe false positives from
  overly narrow inference — ignore them.

## Known perf ceilings

- `_populate_toc()` with a filter now runs O(N) (~238 iterations), was
  O(N²) (~57K).
- `Expand all` in a section refuses to open more than 60 register cards
  in one shot — the user can still click individual headers.
- Search box is debounced 220 ms.
- TOC / Cap / Reg filter boxes are debounced 180 ms.

## Things NOT yet done
- No LICENSE file
- No GitHub Actions / CI
- No screenshots in README
- `pcie_ch7_mcp.py` is experimental, not wired into GUI
- No cross-platform PDF launcher (currently Windows-only via
  `os.startfile` + optional SumatraPDF path)
