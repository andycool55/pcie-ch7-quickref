#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PCIe 5.0 Ch.7 Query Tool  — GUI (Python 3.14 safe, composition pattern)
右側直接以結構化表格顯示暫存器 bit fields / 章節資訊
"""

import tkinter as tk
from tkinter import ttk
import sys, os, subprocess

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from pcie_ch7_tool import (
    CHAPTER7_TOC, CAPABILITY_ID_MAP, REGISTER_ATTRIBUTES,
    REGISTER_DB, search_toc, search_keywords, fuzzy_search,
)

PDF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                        "NCB-PCI_Express_Base_5.0r1.0-2019-05-22.pdf")

# ── palette ───────────────────────────────────────────────────────────────────
BG       = "#1c2133"
SIDEBAR  = "#151929"
HDR      = "#0e1320"
PANEL    = "#222840"
BORDER   = "#2d3655"
ACCENT   = "#4f9cf9"
GREEN    = "#3ecf8e"
YELLOW   = "#e5c07b"
RED      = "#e06c75"
PURPLE   = "#c678dd"
CYAN     = "#56b6c2"
GRAY     = "#5c6370"
TEXT     = "#dce3f0"
DIM      = "#7b8aa0"
SEL_BG   = "#2c3a6e"
ROW0     = "#1c2133"
ROW1     = "#222840"
CODE_BG  = "#141820"

ATTR_CLR = {
    "RO":     CYAN,
    "RW":     GREEN,
    "RW1C":   RED,
    "RWS":    PURPLE,
    "RW1CS":  PURPLE,
    "ROS":    CYAN,
    "HwInit": YELLOW,
    "RsvdP":  GRAY,
    "RsvdZ":  GRAY,
}

def attr_color(attr_str):
    a = attr_str.split("/")[0].strip()
    return ATTR_CLR.get(a, DIM)


# ═════════════════════════════════════════════════════════════════════════════
def run():
    print("DEBUG: Starting run() function")
    root = tk.Tk()
    root.title("PCIe 5.0 — Chapter 7 Quick Reference")
    root.geometry("1440x900")
    root.minsize(1000, 650)
    root.configure(bg=BG)
    print("DEBUG: Tk root created")
    
    # ── ttk style ─────────────────────────────────────────────────────────────
    s = ttk.Style(root)
    s.theme_use("default")
    s.configure("Treeview", background=SIDEBAR, foreground=TEXT,
                fieldbackground=SIDEBAR, borderwidth=0, rowheight=26,
                font=("Segoe UI", 10))
    s.configure("Treeview.Heading", background=HDR, foreground=ACCENT,
                font=("Segoe UI", 10, "bold"), relief="flat")
    s.map("Treeview",
          background=[("selected", SEL_BG)],
          foreground=[("selected", "#ffffff")])
    s.configure("Vertical.TScrollbar", background=PANEL,
                troughcolor=SIDEBAR, arrowcolor=DIM, relief="flat", borderwidth=0)
    s.configure("TPanedwindow", background=BORDER)
    s.configure("TNotebook", background=SIDEBAR, borderwidth=0)
    s.configure("TNotebook.Tab", background=PANEL, foreground=DIM,
                padding=[14, 5], font=("Segoe UI", 10))
    s.map("TNotebook.Tab",
          background=[("selected", BG)],
          foreground=[("selected", ACCENT)])

    # ── top bar ───────────────────────────────────────────────────────────────
    topbar = tk.Frame(root, bg=HDR, height=46)
    topbar.pack(fill="x")
    topbar.pack_propagate(False)

    tk.Label(topbar, text="⚡ PCIe 5.0  Ch.7", bg=HDR, fg=ACCENT,
             font=("Segoe UI", 13, "bold")).pack(side="left", padx=(14, 6), pady=10)
    tk.Label(topbar, text="Software Initialization & Configuration  ·  pp.673–1000",
             bg=HDR, fg=DIM, font=("Segoe UI", 9)).pack(side="left")

    # ── nav buttons (Home / Back) — placed after content funcs are defined ────
    nav_frame = tk.Frame(topbar, bg=HDR)
    nav_frame.pack(side="left", padx=(16, 0))

    # ── Open PDF button (right side, before search) ───────────────────────────
    pdf_btn_frame = tk.Frame(topbar, bg=HDR)
    pdf_btn_frame.pack(side="right", padx=(0, 8), pady=8)

    # ── search bar ────────────────────────────────────────────────────────────
    sf = tk.Frame(topbar, bg=HDR)
    sf.pack(side="right", padx=(10, 4), pady=8)

    tk.Label(sf, text="🔍", bg=HDR, fg=DIM,
             font=("Segoe UI", 11)).pack(side="left", padx=(0, 4))

    sv = tk.StringVar()
    ent = tk.Entry(sf, textvariable=sv, bg="#252d47", fg=TEXT,
                 insertbackground=TEXT, relief="flat", highlightthickness=0,
                 font=("Segoe UI", 10), width=28)
    ent.pack(side="left", ipady=3)
    ent.focus_set()

    # placeholder overlay
    _placeholder = "Search  (Ctrl+F)…  aer aspm dpc msi l1pm ptm 0001h"
    def _apply_placeholder():
        if not sv.get():
            ent.config(fg=DIM)
            sv.set(_placeholder)
    def _clear_placeholder(_=None):
        if sv.get() == _placeholder:
            sv.set("")
            ent.config(fg=TEXT)
    def _restore_placeholder(_=None):
        if not sv.get():
            _apply_placeholder()
    ent.bind("<FocusIn>",  _clear_placeholder)
    ent.bind("<FocusOut>", _restore_placeholder)

    # ── main content area: PanedWindow (sidebar | content) ────────────────────
    main = ttk.Panedwindow(root, orient="horizontal")
    main.pack(fill="both", expand=True)

    # ---- LEFT sidebar ---------------------------------------------------------
    sidebar_wrap = tk.Frame(main, bg=SIDEBAR)
    main.add(sidebar_wrap, weight=0)

    nb = ttk.Notebook(sidebar_wrap)
    nb.pack(fill="both", expand=True, padx=0, pady=0)

    # tab: TOC tree
    tab_toc = tk.Frame(nb, bg=SIDEBAR)
    nb.add(tab_toc, text="📚 TOC")

    toc_filter_var = tk.StringVar()
    _toc_filter_ent = tk.Entry(tab_toc, textvariable=toc_filter_var, bg="#252d47",
                               fg=TEXT, insertbackground=TEXT, relief="flat",
                               highlightthickness=1, highlightbackground=BORDER,
                               highlightcolor=ACCENT, font=("Segoe UI", 9))
    _toc_filter_ent.pack(fill="x", padx=6, pady=(6, 4), ipady=3)

    toc_tree_frame = tk.Frame(tab_toc, bg=SIDEBAR)
    toc_tree_frame.pack(fill="both", expand=True, padx=(6, 0), pady=(0, 6))
    toc_tree = ttk.Treeview(toc_tree_frame, show="tree", selectmode="browse")
    toc_vsb = ttk.Scrollbar(toc_tree_frame, orient="vertical",
                            command=toc_tree.yview)
    toc_tree.configure(yscrollcommand=toc_vsb.set)
    toc_tree.pack(side="left", fill="both", expand=True)
    toc_vsb.pack(side="right", fill="y")

    # tab: Cap IDs
    tab_cap = tk.Frame(nb, bg=SIDEBAR)
    nb.add(tab_cap, text="🔌 Cap IDs")

    cap_filter_var = tk.StringVar()
    _cap_filter_ent = tk.Entry(tab_cap, textvariable=cap_filter_var, bg="#252d47",
                               fg=TEXT, insertbackground=TEXT, relief="flat",
                               highlightthickness=1, highlightbackground=BORDER,
                               highlightcolor=ACCENT, font=("Segoe UI", 9))
    _cap_filter_ent.pack(fill="x", padx=6, pady=(6, 4), ipady=3)

    cap_list_frame = tk.Frame(tab_cap, bg=SIDEBAR)
    cap_list_frame.pack(fill="both", expand=True, padx=(6, 0), pady=(0, 6))
    cap_tree = ttk.Treeview(cap_list_frame, show="tree", selectmode="browse")
    cap_vsb = ttk.Scrollbar(cap_list_frame, orient="vertical",
                            command=cap_tree.yview)
    cap_tree.configure(yscrollcommand=cap_vsb.set)
    cap_tree.pack(side="left", fill="both", expand=True)
    cap_vsb.pack(side="right", fill="y")

    # tab: Registers
    tab_reg = tk.Frame(nb, bg=SIDEBAR)
    nb.add(tab_reg, text="📋 Regs")

    reg_filter_var = tk.StringVar()
    _reg_filter_ent = tk.Entry(tab_reg, textvariable=reg_filter_var, bg="#252d47",
                               fg=TEXT, insertbackground=TEXT, relief="flat",
                               highlightthickness=1, highlightbackground=BORDER,
                               highlightcolor=ACCENT, font=("Segoe UI", 9))
    _reg_filter_ent.pack(fill="x", padx=6, pady=(6, 4), ipady=3)

    reg_list_frame = tk.Frame(tab_reg, bg=SIDEBAR)
    reg_list_frame.pack(fill="both", expand=True, padx=(6, 0), pady=(0, 6))
    reg_tree = ttk.Treeview(reg_list_frame, show="tree", selectmode="browse")
    reg_vsb = ttk.Scrollbar(reg_list_frame, orient="vertical",
                            command=reg_tree.yview)
    reg_tree.configure(yscrollcommand=reg_vsb.set)
    reg_tree.pack(side="left", fill="both", expand=True)
    reg_vsb.pack(side="right", fill="y")

    # ---- RIGHT content -------------------------------------------------------
    content = tk.Frame(main, bg=BG)
    main.add(content, weight=1)

    # breadcrumb bar
    crumb_bar = tk.Frame(content, bg=HDR, height=28)
    crumb_bar.pack(fill="x")
    crumb_bar.pack_propagate(False)
    crumb_var = tk.StringVar(value="🏠  Home")
    tk.Label(crumb_bar, textvariable=crumb_var, bg=HDR, fg=DIM,
             font=("Segoe UI", 9), anchor="w").pack(side="left", padx=12)

    # scrollable canvas
    canvas_wrap = tk.Frame(content, bg=BG)
    canvas_wrap.pack(fill="both", expand=True)
    canvas = tk.Canvas(canvas_wrap, bg=BG, highlightthickness=0)
    vsb = ttk.Scrollbar(canvas_wrap, orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=vsb.set)
    vsb.pack(side="right", fill="y")
    canvas.pack(side="left", fill="both", expand=True)

    content_frame = tk.Frame(canvas, bg=BG)
    _canvas_window = canvas.create_window((0, 0), window=content_frame, anchor="nw")

    def _on_content_configure(_e):
        canvas.configure(scrollregion=canvas.bbox("all"))
    content_frame.bind("<Configure>", _on_content_configure)

    def _on_canvas_configure(e):
        canvas.itemconfigure(_canvas_window, width=e.width)
    canvas.bind("<Configure>", _on_canvas_configure)

    # set initial sidebar width (~280px)
    root.update_idletasks()
    try:
        main.sashpos(0, 280)
    except tk.TclError:
        pass

    # ── status bar ─────────────────────────────────────────────────────────────
    status = tk.Frame(root, bg=SIDEBAR, height=24)
    status.pack(fill="x")
    status.pack_propagate(False)

    status_var = tk.StringVar()
    status_label = tk.Label(status, textvariable=status_var, bg=SIDEBAR, fg=TEXT,
                   font=("Segoe UI", 9))
    status_label.pack(side="left", padx=10, pady=2)

    hint_lbl = tk.Label(status,
                        text="Ctrl+F Search · Ctrl+H Home · Alt+← Back · "
                             "Ctrl+1/2/3 Tabs · Enter Open PDF · Esc Clear",
                        bg=SIDEBAR, fg=DIM, font=("Segoe UI", 9))
    hint_lbl.pack(side="right", padx=10, pady=2)

    # ── global state ───────────────────────────────────────────────────────────
    title_var = tk.StringVar()
    page_btn_var = tk.StringVar()
    _open_page = [673]
    _history = []           # navigation stack (excluding current)
    _current = [None]       # ("welcome",) | ("section", id) | ("cap", id) | ("reg", name) | ("search", q)
    # (was: _suppress_sel — replaced by _prog_toc/_prog_cap/_prog_reg markers)
    
    # ── helper functions ──────────────────────────────────────────────────────
    def clear_content():
        # Detach the <Configure> handler while destroying/rebuilding many
        # children — otherwise each destroy triggers a full bbox("all") recalc,
        # which is O(N²) and freezes the UI on register-heavy sections.
        try:
            content_frame.unbind("<Configure>")
        except Exception:
            pass
        for w in content_frame.winfo_children():
            w.destroy()
        # rebind after clearing; the new content will trigger one final recalc
        content_frame.bind("<Configure>", _on_content_configure)

    def set_status(text, page=None):
        if page:
            status_var.set(f"{text}   ·   p.{page}")
        else:
            status_var.set(text)

    def _kids(sec):
        """Return direct child section IDs of `sec` from CHAPTER7_TOC."""
        depth = len(sec.split(".")) + 1
        prefix = sec + "."
        return [k for k in CHAPTER7_TOC
                if k.startswith(prefix) and len(k.split(".")) == depth]
        
    def section_label(parent, text, fg=ACCENT, font=("Segoe UI",11,"bold"), pady=(12,4)):
        tk.Label(parent, text=text, bg=BG, fg=fg,
                 font=font, anchor="w").pack(fill="x", padx=16, pady=pady)

    def divider(parent):
        tk.Frame(parent, bg=BORDER, height=1).pack(fill="x", padx=16, pady=2)

    def info_row(parent, label, value, label_fg=DIM, value_fg=TEXT):
        row = tk.Frame(parent, bg=BG)
        row.pack(fill="x", padx=16, pady=1)
        tk.Label(row, text=label, bg=BG, fg=label_fg,
                 font=("Segoe UI",9), width=22, anchor="w").pack(side="left")
        tk.Label(row, text=value, bg=BG, fg=value_fg,
                 font=("Segoe UI",9), anchor="w").pack(side="left")

    # ── Register bit-field table (the main visual) ────────────────────────────
    COLS = [
        ("Bits",        10,  "center", TEXT),
        ("Field Name",  36,  "w",      TEXT),
        ("Attr",         8,  "center", TEXT),
        ("Description", 60,  "w",      TEXT),
    ]

    def bit_table(parent, reg_name, reg_data):
        wrap_w = 580   # description wrap width in pixels

        outer = tk.Frame(parent, bg=PANEL, bd=0)
        outer.pack(fill="x", padx=16, pady=6)

        # table header
        hdr_row = tk.Frame(outer, bg=HDR)
        hdr_row.pack(fill="x")
        widths = [80, 260, 70, wrap_w]
        hdr_texts = ["Bits", "Field Name", "Attr", "Description"]
        for i, (ht, w2) in enumerate(zip(hdr_texts, widths)):
            anchor = "center" if i in (0,2) else "w"
            tk.Label(hdr_row, text=ht, bg=HDR, fg=ACCENT,
                     font=("Segoe UI",9,"bold"),
                     width=0, anchor=anchor, padx=8, pady=4
                     ).pack(side="left",
                            ipadx=0,
                            padx=(0 if i else 0),
                            fill="x" if i==3 else "none",
                            expand=(i==3))

        # rows
        bits = reg_data["bits"]
        for i, (bp, bi) in enumerate(bits.items()):
            bg_row = ROW0 if i%2==0 else ROW1
            row = tk.Frame(outer, bg=bg_row)
            row.pack(fill="x")

            # Bits
            tk.Label(row, text=f"[{bp}]", bg=bg_row, fg=CYAN,
                     font=("Consolas",9,"bold"),
                     width=10, anchor="center", pady=5
                     ).pack(side="left")

            # Field Name
            tk.Label(row, text=bi["name"], bg=bg_row, fg=TEXT,
                     font=("Segoe UI",9),
                     width=30, anchor="w", padx=6
                     ).pack(side="left")

            # Attr badge
            ac = attr_color(bi["attr"])
            tk.Label(row, text=bi["attr"], bg=bg_row, fg=ac,
                     font=("Segoe UI",9,"bold"),
                     width=9, anchor="center"
                     ).pack(side="left")

            # Description (wrapping)
            tk.Label(row, text=bi["desc"], bg=bg_row, fg=DIM,
                     font=("Segoe UI",9),
                     anchor="w", justify="left", wraplength=wrap_w,
                     padx=8, pady=4
                     ).pack(side="left", fill="x", expand=True)

    # ── helper: bind click+hover to a widget and ALL its descendants ──────────
    def _bind_click(widget, on_click, hover_widget=None, hover_bg=ACCENT, normal_bg=BORDER):
        """Recursively bind Button-1 and Enter/Leave to widget and all children."""
        hw = hover_widget or widget
        widget.bind("<Button-1>", lambda e: on_click())
        widget.bind("<Enter>",    lambda e: hw.config(highlightbackground=hover_bg))
        widget.bind("<Leave>",    lambda e: hw.config(highlightbackground=normal_bg))
        for child in widget.winfo_children():
            child.bind("<Button-1>", lambda e: on_click())
            child.bind("<Enter>",    lambda e: hw.config(highlightbackground=hover_bg))
            child.bind("<Leave>",    lambda e: hw.config(highlightbackground=normal_bg))

    # ── clickable child-section cards ─────────────────────────────────────────
    def section_cards(parent, sections):
        """Show child sections as clickable cards in a 3-column grid."""
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="x", padx=16, pady=6)
        for col_i in range(3):
            frame.columnconfigure(col_i, weight=1)

        for idx, sec in enumerate(sections):
            info = CHAPTER7_TOC[sec]
            card = tk.Frame(frame, bg=PANEL, cursor="hand2",
                            highlightthickness=1, highlightbackground=BORDER)
            card.grid(row=idx//3, column=idx%3, padx=6, pady=5,
                      sticky="nsew", ipadx=4, ipady=4)

            lbl_sec = tk.Label(card, text=sec, bg=PANEL, fg=ACCENT,
                               font=("Segoe UI",8,"bold"), anchor="w",
                               cursor="hand2")
            lbl_sec.pack(fill="x", padx=8, pady=(6,0))

            lbl_title = tk.Label(card, text=info["title"], bg=PANEL, fg=TEXT,
                                 font=("Segoe UI",8), anchor="w",
                                 wraplength=180, justify="left", cursor="hand2")
            lbl_title.pack(fill="x", padx=8, pady=(2,0))

            lbl_page = tk.Label(card, text=f"p. {info['page']}", bg=PANEL,
                                fg=YELLOW, font=("Segoe UI",8), anchor="e",
                                cursor="hand2")
            lbl_page.pack(fill="x", padx=8, pady=(0,6))

            # capture sec in closure explicitly
            target = sec
            def _go(s=target):
                show_section(s)

            for w2 in (card, lbl_sec, lbl_title, lbl_page):
                w2.bind("<Button-1>", lambda e, fn=_go: fn())
                w2.bind("<Enter>",
                        lambda e, c=card: c.config(highlightbackground=ACCENT))
                w2.bind("<Leave>",
                        lambda e, c=card: c.config(highlightbackground=BORDER))

    # ── Capability ID badge strip ─────────────────────────────────────────────
    def cap_badge(parent, cap_id, cap_info):
        row = tk.Frame(parent, bg=PANEL, cursor="hand2",
                       highlightthickness=1, highlightbackground=BORDER)
        row.pack(fill="x", padx=16, pady=3, ipady=4)

        bg2 = "#1e2d50"
        lbl_id = tk.Label(row, text=f" {cap_id} ", bg=bg2, fg=CYAN,
                          font=("Consolas",9,"bold"), cursor="hand2",
                          padx=6, pady=2)
        lbl_id.pack(side="left", padx=(8,6), pady=4)

        sec = cap_info["section"]
        si  = CHAPTER7_TOC.get(sec, {})

        lbl_name = tk.Label(row, text=cap_info["name"], bg=PANEL, fg=TEXT,
                            font=("Segoe UI",9), cursor="hand2", anchor="w")
        lbl_name.pack(side="left", fill="x", expand=True)

        lbl_sec = tk.Label(row, text=f"§{sec}  p.{si.get('page','?')}",
                           bg=PANEL, fg=YELLOW, font=("Segoe UI",8,"bold"),
                           cursor="hand2")
        lbl_sec.pack(side="right", padx=8)

        def _go(cid=cap_id):
            show_capability(cid)

        for w2 in (row, lbl_id, lbl_name, lbl_sec):
            w2.bind("<Button-1>", lambda e, fn=_go: fn())
            w2.bind("<Enter>",
                    lambda e, r=row: r.config(highlightbackground=ACCENT))
            w2.bind("<Leave>",
                    lambda e, r=row: r.config(highlightbackground=BORDER))

    # ── open PDF ──────────────────────────────────────────────────────────────
    def open_pdf(page):
        if not os.path.exists(PDF_PATH):
            set_status(f"PDF not found: {PDF_PATH}"); return
        try:
            sp = r"C:\Program Files\SumatraPDF\SumatraPDF.exe"
            if os.path.exists(sp):
                subprocess.Popen([sp, "-page", str(page), PDF_PATH])
            else:
                os.startfile(PDF_PATH)
        except Exception as ex:
            set_status(f"Cannot open: {ex}")

    # ── header with count + "Expand/Collapse all" for a register list ────────
    def _reg_header_bar(parent, count, regs, auto_open=False):
        """Emit a 'Register Bit Fields (N)  [Expand all] [Collapse all]' header
        followed by one collapsible card per register. Cards are built lazily —
        clicking a header expands only that register.
        """
        bar = tk.Frame(parent, bg=BG)
        bar.pack(fill="x", padx=16, pady=(10, 2))

        tk.Label(bar, text=f"Register Bit Fields  ({count})",
                 bg=BG, fg=YELLOW, font=("Segoe UI", 10, "bold"),
                 anchor="w").pack(side="left")

        # keep references so buttons can drive them
        cards = []

        def _mk_pill(text, cmd, fg=ACCENT):
            b = tk.Label(bar, text=text, bg=PANEL, fg=fg,
                         font=("Segoe UI", 8, "bold"),
                         padx=8, pady=2, cursor="hand2")
            b.pack(side="right", padx=3)
            b.bind("<Button-1>", lambda e: cmd())
            b.bind("<Enter>",    lambda e: b.config(bg=SEL_BG))
            b.bind("<Leave>",    lambda e: b.config(bg=PANEL))
            return b

        def _expand_all():
            # Guard against huge cost — warn via status bar and cap at 60
            if len(cards) > 60:
                set_status(f"Too many registers ({len(cards)}) to expand at once")
                return
            for c in cards:
                if not c["state"]["open"]:
                    c["toggle"]()
        def _collapse_all():
            for c in cards:
                if c["state"]["open"]:
                    c["toggle"]()

        _mk_pill("▾ Expand all",   _expand_all,   fg=GREEN)
        _mk_pill("▸ Collapse all", _collapse_all, fg=DIM)

        # emit each card
        for rn, rd in regs:
            info = _make_register_card(parent, rn, rd, start_open=auto_open)
            cards.append(info)

    def _make_register_card(parent, reg_name, reg_data, start_open=False):
        """Same as register_card but returns dict with {state, toggle} handle."""
        card = tk.Frame(parent, bg=BG)
        card.pack(fill="x", padx=16, pady=(6, 0))

        header = tk.Frame(card, bg=PANEL, cursor="hand2",
                          highlightthickness=1, highlightbackground=BORDER)
        header.pack(fill="x")

        state = {"open": False, "built": False}
        chev = tk.Label(header, text="▸", bg=PANEL, fg=ACCENT,
                        font=("Segoe UI", 10, "bold"),
                        width=2, cursor="hand2")
        chev.pack(side="left", padx=(6, 0), pady=4)

        title = tk.Label(header,
                         text=f"{reg_name.replace('_',' ').upper()}",
                         bg=PANEL, fg=GREEN,
                         font=("Segoe UI", 10, "bold"),
                         cursor="hand2", anchor="w")
        title.pack(side="left", padx=(4, 8), pady=4)

        meta = tk.Label(header,
                        text=f"offset {reg_data['offset']}  ·  "
                             f"§{reg_data['section']}  ·  "
                             f"p.{reg_data.get('page','?')}  ·  "
                             f"{len(reg_data['bits'])} bits",
                        bg=PANEL, fg=DIM,
                        font=("Segoe UI", 9),
                        cursor="hand2", anchor="w")
        meta.pack(side="left", padx=6, pady=4)

        body = tk.Frame(card, bg=BG)

        def _toggle(_e=None):
            state["open"] = not state["open"]
            if state["open"]:
                chev.config(text="▾")
                header.config(highlightbackground=ACCENT)
                if not state["built"]:
                    bit_table(body, reg_name, reg_data)
                    state["built"] = True
                body.pack(fill="x")
            else:
                chev.config(text="▸")
                header.config(highlightbackground=BORDER)
                body.pack_forget()

        for w in (header, chev, title, meta):
            w.bind("<Button-1>", _toggle)

        def _hover_on(_e):
            if not state["open"]:
                header.config(highlightbackground=ACCENT)
        def _hover_off(_e):
            if not state["open"]:
                header.config(highlightbackground=BORDER)
        for w in (header, chev, title, meta):
            w.bind("<Enter>", _hover_on)
            w.bind("<Leave>", _hover_off)

        if start_open:
            _toggle()

        return {"card": card, "state": state, "toggle": _toggle}

    # ═════════════════════════════════════════════════════════════════════════
    # SHOW FUNCTIONS
    # ═════════════════════════════════════════════════════════════════════════

    def _impl_welcome():
        clear_content()
        title_var.set("PCIe 5.0 — Chapter 7 Quick Reference")
        page_btn_var.set("")
        _open_page[0] = 673

        section_label(content_frame, "PCIe 5.0 Base Spec — Chapter 7",
                      font=("Segoe UI",15,"bold"), pady=(20,4))
        section_label(content_frame, "Software Initialization and Configuration",
                      fg=GREEN, font=("Segoe UI",11), pady=(0,8))
        divider(content_frame)
        info_row(content_frame,"Source:", "NCB-PCI_Express_Base_5.0r1.0-2019-05-22.pdf")
        info_row(content_frame,"Coverage:", "pp. 673 – 1000  (328 pages)")
        info_row(content_frame,"Sections indexed:", str(len(CHAPTER7_TOC)))
        info_row(content_frame,"Cap IDs:", str(len(CAPABILITY_ID_MAP)))
        info_row(content_frame,"Registers with bit details:", str(len(REGISTER_DB)))

        divider(content_frame)
        section_label(content_frame,"How to use", fg=YELLOW,
                      font=("Segoe UI",10,"bold"), pady=(10,4))
        tips = [
            ("📚 TOC tab",      "Left sidebar · browse the chapter tree (Ctrl+1)"),
            ("🔌 Cap IDs tab",  "Left sidebar · jump straight to a Capability's registers (Ctrl+2)"),
            ("📋 Regs tab",     "Left sidebar · see all bit fields of a register (Ctrl+3)"),
            ("🔍 Search",       "Ctrl+F to focus  ·  type any keyword (aspm, dpc, aer …)"),
            ("📄 Open PDF",     "Top-right button (or press Enter) once a section is selected"),
            ("⌨  Navigation",   "Ctrl+H = Home · Alt+← = Back · Esc = clear search"),
        ]
        for icon_label, desc in tips:
            row = tk.Frame(content_frame, bg=BG)
            row.pack(fill="x", padx=16, pady=2)
            tk.Label(row, text=icon_label, bg=BG, fg=ACCENT,
                     font=("Segoe UI",9,"bold"), width=18, anchor="w"
                     ).pack(side="left")
            tk.Label(row, text=desc, bg=BG, fg=TEXT,
                     font=("Segoe UI",9), anchor="w").pack(side="left")

        divider(content_frame)
        section_label(content_frame,"Main sections", fg=YELLOW,
                      font=("Segoe UI",10,"bold"), pady=(10,4))
        top_secs = [s for s in CHAPTER7_TOC if len(s.split("."))==2]
        section_cards(content_frame, top_secs)
        set_status("Welcome")

    # ─────────────────────────────────────────────────────────────────────────
    def _impl_section(sec):
        if sec not in CHAPTER7_TOC:
            return
        info = CHAPTER7_TOC[sec]
        clear_content()
        title_var.set(f"§{sec}  {info['title']}")
        page_btn_var.set(f"📄 Open PDF  p.{info['page']}")
        _open_page[0] = info["page"]

        section_label(content_frame, f"§{sec}", fg=DIM,
                      font=("Segoe UI",9), pady=(10,0))
        section_label(content_frame, info["title"],
                      font=("Segoe UI",14,"bold"), pady=(0,2))
        info_row(content_frame,"Spec page:", str(info["page"]), value_fg=YELLOW)
        divider(content_frame)

        # child sections as cards
        kids = _kids(sec)
        if kids:
            section_label(content_frame,"Sub-sections", fg=YELLOW,
                          font=("Segoe UI",10,"bold"), pady=(10,2))
            section_cards(content_frame, kids)

        # register tables (collapsible cards — lazy build)
        regs = [(n,d) for n,d in REGISTER_DB.items()
                if d.get("section","").startswith(sec)]
        if regs:
            divider(content_frame)
            _reg_header_bar(content_frame, len(regs), regs, auto_open=(len(regs) == 1))

        if not kids and not regs:
            section_label(content_frame,
                          "No sub-sections or register details indexed.\n"
                          "See the PDF for full content.",
                          fg=DIM, font=("Segoe UI",9), pady=(12,4))

        canvas.yview_moveto(0)
        set_status(f"§{sec}: {info['title']}", info["page"])

    # ─────────────────────────────────────────────────────────────────────────
    def _impl_capability(cap_id):
        info = CAPABILITY_ID_MAP.get(cap_id)
        if not info:
            return
        sec  = info["section"]
        si   = CHAPTER7_TOC.get(sec, {})
        clear_content()
        title_var.set(f"Capability  {cap_id}  —  {info['name']}")
        page_btn_var.set(f"📄 Open PDF  p.{si.get('page','?')}")
        _open_page[0] = si.get("page", 1)

        section_label(content_frame, f"Capability ID: {cap_id}", fg=CYAN,
                      font=("Consolas",12,"bold"), pady=(14,0))
        section_label(content_frame, info["name"],
                      font=("Segoe UI",13,"bold"), pady=(0,4))
        info_row(content_frame,"Section:", sec)
        info_row(content_frame,"Spec page:", str(si.get("page","?")), value_fg=YELLOW)
        divider(content_frame)

        # child register sections as cards
        kids = _kids(sec)
        if kids:
            section_label(content_frame,"Registers", fg=YELLOW,
                          font=("Segoe UI",10,"bold"), pady=(10,2))
            section_cards(content_frame, kids)

        # bit tables (collapsible cards)
        regs = [(n,d) for n,d in REGISTER_DB.items()
                if d.get("section","").startswith(sec)]
        if regs:
            divider(content_frame)
            _reg_header_bar(content_frame, len(regs), regs, auto_open=(len(regs) == 1))

        canvas.yview_moveto(0)
        set_status(f"Capability {cap_id}: {info['name']}", si.get("page",""))

    # ─────────────────────────────────────────────────────────────────────────
    def _impl_register(reg_name):
        rd = REGISTER_DB.get(reg_name)
        if not rd:
            return
        sec  = rd["section"]
        si   = CHAPTER7_TOC.get(sec, {})
        clear_content()
        title_var.set(f"{reg_name.replace('_',' ').upper()}  —  §{sec}")
        page_btn_var.set(f"📄 Open PDF  p.{rd['page']}")
        _open_page[0] = rd["page"]

        section_label(content_frame, reg_name.replace("_"," ").upper(),
                      font=("Segoe UI",14,"bold"), pady=(14,2))
        info_row(content_frame,"Section:", f"§{sec}  {si.get('title','')}")
        info_row(content_frame,"Offset:", rd["offset"])
        info_row(content_frame,"Spec page:", str(rd["page"]), value_fg=YELLOW)
        divider(content_frame)

        section_label(content_frame,"Bit Fields", fg=YELLOW,
                      font=("Segoe UI",10,"bold"), pady=(8,2))
        bit_table(content_frame, reg_name, rd)

        # attribute legend
        divider(content_frame)
        section_label(content_frame,"Attribute Legend", fg=YELLOW,
                      font=("Segoe UI",10,"bold"), pady=(8,2))
        used = set()
        for bi in rd["bits"].values():
            for a in bi["attr"].split("/"):
                used.add(a.strip())
        for attr in sorted(used):
            row = tk.Frame(content_frame, bg=BG)
            row.pack(fill="x", padx=16, pady=2)
            ac = ATTR_CLR.get(attr, DIM)
            tk.Label(row, text=attr, bg=BG, fg=ac,
                     font=("Segoe UI",9,"bold"), width=10, anchor="w"
                     ).pack(side="left")
            tk.Label(row, text=REGISTER_ATTRIBUTES.get(attr,""),
                     bg=BG, fg=DIM, font=("Segoe UI",9), anchor="w"
                     ).pack(side="left")

        canvas.yview_moveto(0)
        set_status(f"Register: {reg_name.replace('_',' ').title()}", rd["page"])

    # ─────────────────────────────────────────────────────────────────────────
    # ── 搜尋結果卡片牆 ────────────────────────────────────────────────────────
    def _card_grid(parent, items, cols=4):
        """Create a simple, consistent card grid for search results.
        Each *item* dict must contain:
            tag, tag_fg, tag_bg, title, sub (optional), page, on_click
        The whole card reacts to hover and click, no reliance on
        win‑info or complex bindings.
        """
        # Card colours – a slightly lighter background and a subtle hover shade
        CARD_BG  = "#1e2a40"
        CARD_HOV = "#2a3c60"

        # Container that holds the grid of cards
        frame = tk.Frame(parent, bg=BG)
        frame.pack(fill="x", padx=12, pady=4)
        for c in range(cols):
            frame.columnconfigure(c, weight=1)

        # Helper to create a label that automatically binds the three mouse events
        def _make_label(parent_w, text, bg, fg, font_, anchor="w", wrap=0, pady=(0,0)):
            label = tk.Label(parent_w, text=text, bg=bg, fg=fg, font=font_,
                         anchor=anchor, padx=6, pady=pady, cursor="hand2")
            if wrap:
                label.configure(wraplength=wrap)
            # Bind click and hover to the *card* callbacks defined below
            label.bind("<Button-1>", _click)
            label.bind("<Enter>",    _enter)
            label.bind("<Leave>",    _leave)
            return label

        for idx, item in enumerate(items):
            fn   = item["on_click"]
            tag_bg = item["tag_bg"]
            tag_fg = item["tag_fg"]

            # Card frame – the visual container
            card = tk.Frame(frame, bg=CARD_BG, cursor="hand2",
                        highlightthickness=1, highlightbackground=BORDER)
            card.grid(row=idx // cols, column=idx % cols,
                      padx=5, pady=4, sticky="nsew", ipadx=6, ipady=4)

            # Mouse‑event helpers attached to this card instance
            def _click(e, f=fn): f()
            def _enter(e, c=card): c.configure(bg=CARD_HOV, highlightbackground=ACCENT)
            def _leave(e, c=card): c.configure(bg=CARD_BG, highlightbackground=BORDER)

            # Top coloured bar – visual tag indicator
            bar = tk.Frame(card, bg=tag_bg, height=4)
            bar.pack(fill="x")
            bar.bind("<Button-1>", _click)
            bar.bind("<Enter>",    _enter)
            bar.bind("<Leave>",    _leave)

            # Tag badge (small badge with the ID or offset)
            _make_label(card, f" {item['tag']} ", tag_bg, tag_fg,
                        ("Consolas", 8, "bold"), pady=(1,1)).pack(fill="x")

            # Main title – bold and a bit larger
            _make_label(card, item["title"], CARD_BG, TEXT,
                        ("Segoe UI", 10, "bold"), wrap=200, pady=(4,0)).pack(fill="x")

            # Optional subtitle – lighter colour and slightly smaller
            if item.get("sub"):
                _make_label(card, item["sub"], CARD_BG, DIM,
                            ("Segoe UI", 9), wrap=200, pady=(1,0)).pack(fill="x")

            # Page info – right‑aligned, yellow for visibility
            _make_label(card, item["page"], CARD_BG, YELLOW,
                        ("Segoe UI", 9, "bold"), anchor="e", pady=(2,4)).pack(fill="x")

            # Ensure the whole card responds to click/hover
            card.bind("<Button-1>", _click)
            card.bind("<Enter>",    _enter)
            card.bind("<Leave>",    _leave)

    # ─────────────────────────────────────────────────────────────────────────
    def _impl_search(query):
        q = query.strip()
        if not q or q == _placeholder:
            show_welcome()
            return

        # 模糊搜尋
        results = fuzzy_search(q)
        sec_hits = results["sections"]   # (sec_id, info, score)
        cap_hits = results["caps"]       # (cap_id, info, score)
        reg_hits = results["registers"]  # (reg_name, data, score)

        total = len(sec_hits) + len(cap_hits) + len(reg_hits)

        clear_content()
        title_var.set(f'Search: "{q}"')
        page_btn_var.set("")

        # ── 標題 + 統計列 ─────────────────────────────────────────────────
        hdr = tk.Frame(content_frame, bg=BG)
        hdr.pack(fill="x", padx=16, pady=(14, 6))

        tk.Label(hdr, text=f'🔍  "{q}"', bg=BG, fg=ACCENT,
                 font=("Segoe UI", 13, "bold")).pack(side="left")

        stat_frame = tk.Frame(hdr, bg=BG)
        stat_frame.pack(side="right")
        for lbl, cnt, fg in [
            (f"§ {len(sec_hits)} Sections", len(sec_hits), ACCENT),
            (f"⬡ {len(cap_hits)} Cap IDs",  len(cap_hits), GREEN),
            (f"▤ {len(reg_hits)} Registers", len(reg_hits), YELLOW),
        ]:
            tk.Label(stat_frame, text=lbl, bg=PANEL, fg=fg,
                     font=("Segoe UI", 9, "bold"),
                     padx=10, pady=3, cursor="hand2"
                     ).pack(side="left", padx=3)

        if total == 0:
            divider(content_frame)
            msg = tk.Frame(content_frame, bg=BG)
            msg.pack(fill="x", padx=24, pady=20)
            tk.Label(msg, text="No results found.",
                     bg=BG, fg=TEXT,
                     font=("Segoe UI", 11, "bold")).pack(anchor="w")
            tk.Label(msg,
                     text="Try:  aer  aspm  dpc  msi  l1 pm  ptm  link status  "
                          "0001h  acs  flr  ecam  32gt  vendor id",
                     bg=BG, fg=DIM, font=("Segoe UI", 9)).pack(anchor="w", pady=(4,0))
            canvas.yview_moveto(0)
            set_status(f'No results for "{q}"')
            return

        # ── Cap ID 卡片牆 ─────────────────────────────────────────────────
        if cap_hits:
            divider(content_frame)
            section_label(content_frame, f"⬡  Capability IDs  ({len(cap_hits)})",
                          fg=GREEN, font=("Segoe UI", 10, "bold"), pady=(8, 2))
            items = []
            for cap_id, info, score in cap_hits:
                si  = CHAPTER7_TOC.get(info["section"], {})
                pg  = f"p.{si.get('page','?')}  §{info['section']}"
                def _go(cid=cap_id): show_capability(cid)
                items.append({
                    "tag":      cap_id,
                    "tag_fg":   HDR,
                    "tag_bg":   GREEN,
                    "title":    info["name"],
                    "sub":      "",
                    "page":     pg,
                    "on_click": _go,
                })
            _card_grid(content_frame, items, cols=4)

        # ── Section 卡片_WALL ────────────────────────────────────────────────
        if sec_hits:
            divider(content_frame)
            section_label(content_frame, f"§  Sections  ({len(sec_hits)})",
                          fg=ACCENT, font=("Segoe UI", 10, "bold"), pady=(8, 2))
            items = []
            for sec_id, info, score in sec_hits:
                def _go(s=sec_id): show_section(s)
                depth = len(sec_id.split(".")) - 1
                sub   = ""
                # show parent section as subtitle for leaf nodes
                if depth >= 3:
                    parent_id = ".".join(sec_id.split(".")[:3])
                    parent_info = CHAPTER7_TOC.get(parent_id, {})
                    sub = parent_info.get("title", "")
                items.append({
                    "tag":      sec_id,
                    "tag_fg":   HDR,
                    "tag_bg":   ACCENT,
                    "title":    info["title"],
                    "sub":      sub,
                    "page":     f"p.{info['page']}",
                    "on_click": _go,
                })
            _card_grid(content_frame, items, cols=4)

        # ── Register 卡片牆 ───────────────────────────────────────────────
        if reg_hits:
            divider(content_frame)
            section_label(content_frame, f"▤  Registers  ({len(reg_hits)})",
                          fg=YELLOW, font=("Segoe UI", 10, "bold"), pady=(8, 2))
            items = []
            for rn, rd, score in reg_hits:
                display = rn.replace("_", " ").title()
                si      = CHAPTER7_TOC.get(rd["section"], {})
                sub     = si.get("title", "")
                pg      = f"p.{rd['page']}  offset {rd['offset']}"
                def _go(name=rn): show_register(name)
                items.append({
                    "tag":      rd["offset"],
                    "tag_fg":   HDR,
                    "tag_bg":   YELLOW,
                    "title":    display,
                    "sub":      sub,
                    "page":     pg,
                    "on_click": _go,
                })
            _card_grid(content_frame, items, cols=4)

        canvas.yview_moveto(0)
        set_status(f'Search "{q}" — {total} results  '
                   f'({len(sec_hits)} sec · {len(cap_hits)} cap · '
                   f'{len(reg_hits)} reg)')

    # ═════════════════════════════════════════════════════════════════════════
    # NAVIGATION WRAPPERS  (add history, breadcrumb, sidebar-highlight)
    # ═════════════════════════════════════════════════════════════════════════
    def _push_history():
        cur = _current[0]
        if cur is not None:
            # avoid pushing duplicates in a row
            if not _history or _history[-1] != cur:
                _history.append(cur)
            # cap length
            if len(_history) > 100:
                del _history[:len(_history) - 100]
        _refresh_nav_buttons()

    def _set_crumb(text):
        crumb_var.set(text)

    # ── programmatic selection guards ────────────────────────────────────────
    # We remember the *last selection we set ourselves*. When TreeviewSelect
    # fires, the handler compares against this and short-circuits if it's
    # our own selection. try/finally suppression doesn't work because Tk
    # dispatches <<TreeviewSelect>> asynchronously — the flag is already
    # reset by the time the handler runs.
    _prog_toc = [None]   # sec last set programmatically
    _prog_cap = [None]
    _prog_reg = [None]

    def _select_toc(sec):
        if not sec or not toc_tree.exists(sec):
            return
        # expand ancestors first
        parts = sec.split(".")
        for i in range(2, len(parts)):
            anc = ".".join(parts[:i])
            if toc_tree.exists(anc):
                toc_tree.item(anc, open=True)
        # only touch selection if different — avoids gratuitous events
        cur = toc_tree.selection()
        if cur and cur[0] == sec:
            toc_tree.see(sec)
            return
        _prog_toc[0] = sec
        toc_tree.selection_set(sec)
        toc_tree.see(sec)

    def _select_cap(cap_id):
        if not cap_tree.exists(cap_id):
            return
        cur = cap_tree.selection()
        if cur and cur[0] == cap_id:
            cap_tree.see(cap_id)
            return
        _prog_cap[0] = cap_id
        cap_tree.selection_set(cap_id)
        cap_tree.see(cap_id)

    def _select_reg(reg_name):
        if not reg_tree.exists(reg_name):
            return
        cur = reg_tree.selection()
        if cur and cur[0] == reg_name:
            reg_tree.see(reg_name)
            return
        _prog_reg[0] = reg_name
        reg_tree.selection_set(reg_name)
        reg_tree.see(reg_name)

    def show_welcome(record=True):
        if record:
            _push_history()
        _impl_welcome()
        _current[0] = ("welcome",)
        _set_crumb("🏠  Home")
        _refresh_nav_buttons()

    def show_section(sec, record=True):
        if sec not in CHAPTER7_TOC:
            return
        if record:
            _push_history()
        _impl_section(sec)
        _current[0] = ("section", sec)
        _select_toc(sec)
        info = CHAPTER7_TOC[sec]
        _set_crumb(f"🏠  Home  ›  §{sec}  {info['title']}")
        _refresh_nav_buttons()

    def show_capability(cap_id, record=True):
        if cap_id not in CAPABILITY_ID_MAP:
            return
        if record:
            _push_history()
        _impl_capability(cap_id)
        _current[0] = ("cap", cap_id)
        _select_cap(cap_id)
        info = CAPABILITY_ID_MAP[cap_id]
        _set_crumb(f"🏠  Home  ›  🔌 Cap {cap_id}  {info['name']}")
        _refresh_nav_buttons()

    def show_register(reg_name, record=True):
        if reg_name not in REGISTER_DB:
            return
        if record:
            _push_history()
        _impl_register(reg_name)
        _current[0] = ("reg", reg_name)
        _select_reg(reg_name)
        rd = REGISTER_DB[reg_name]
        _set_crumb(f"🏠  Home  ›  📋 {reg_name.replace('_',' ').title()}  "
                   f"(§{rd['section']})")
        _refresh_nav_buttons()

    def show_search(query, record=True):
        # (search calls are debounced, don't push history for every keystroke;
        #  push only when transitioning from non-search view)
        cur = _current[0]
        if record and (cur is None or cur[0] != "search"):
            _push_history()
        _impl_search(query)
        q = query.strip()
        if not q or q == _placeholder:
            _current[0] = ("welcome",)
            _set_crumb("🏠  Home")
        else:
            _current[0] = ("search", q)
            _set_crumb(f"🏠  Home  ›  🔍  \"{q}\"")
        _refresh_nav_buttons()

    def go_back(_e=None):
        if not _history:
            return
        prev = _history.pop()
        kind = prev[0]
        if kind == "welcome":
            show_welcome(record=False)
        elif kind == "section":
            show_section(prev[1], record=False)
        elif kind == "cap":
            show_capability(prev[1], record=False)
        elif kind == "reg":
            show_register(prev[1], record=False)
        elif kind == "search":
            sv.set(prev[1])
            ent.config(fg=TEXT)
            _impl_search(prev[1])
            _current[0] = ("search", prev[1])
            _set_crumb(f"🏠  Home  ›  🔍  \"{prev[1]}\"")
        _refresh_nav_buttons()

    # ── nav buttons (Home / Back) ────────────────────────────────────────────
    def _mk_topbtn(parent, text, cmd, fg=TEXT):
        b = tk.Label(parent, text=text, bg=PANEL, fg=fg,
                     font=("Segoe UI", 9, "bold"),
                     padx=10, pady=4, cursor="hand2")
        b.pack(side="left", padx=3)
        b.bind("<Button-1>", lambda e: cmd())
        b.bind("<Enter>",    lambda e: b.config(bg=SEL_BG))
        b.bind("<Leave>",    lambda e: b.config(bg=PANEL))
        return b

    btn_home = _mk_topbtn(nav_frame, "🏠 Home",  lambda: show_welcome(), fg=ACCENT)
    btn_back = _mk_topbtn(nav_frame, "← Back",   go_back,                fg=DIM)

    def _refresh_nav_buttons():
        btn_back.config(fg=ACCENT if _history else DIM,
                        cursor="hand2" if _history else "arrow")
        # PDF button
        if page_btn_var.get():
            pdf_btn.config(text=page_btn_var.get(), fg=YELLOW, bg=PANEL,
                           cursor="hand2")
        else:
            pdf_btn.config(text="📄 Open PDF", fg=DIM, bg=HDR, cursor="arrow")

    # ── Open PDF button ──────────────────────────────────────────────────────
    def _open_pdf_now():
        if page_btn_var.get():
            open_pdf(_open_page[0])

    pdf_btn = tk.Label(pdf_btn_frame, text="📄 Open PDF", bg=HDR, fg=DIM,
                       font=("Segoe UI", 9, "bold"), padx=10, pady=4)
    pdf_btn.pack(side="right")
    pdf_btn.bind("<Button-1>", lambda e: _open_pdf_now())
    pdf_btn.bind("<Enter>",    lambda e: pdf_btn.config(bg=SEL_BG)
                 if page_btn_var.get() else None)
    pdf_btn.bind("<Leave>",    lambda e: pdf_btn.config(bg=PANEL)
                 if page_btn_var.get() else None)

    # ═════════════════════════════════════════════════════════════════════════
    # SIDEBAR:  populate + filter + selection wiring
    # ═════════════════════════════════════════════════════════════════════════
    # tag styling
    toc_tree.tag_configure("leaf",   foreground=TEXT)
    toc_tree.tag_configure("branch", foreground=ACCENT)

    # ── pre-compute static data (sort order, has-children map) once ──────────
    def _sec_key(sec):
        return [int(p) if p.isdigit() else p for p in sec.split(".")]
    _sorted_secs = sorted(CHAPTER7_TOC.keys(), key=_sec_key)
    _sec_has_kid = {s: False for s in _sorted_secs}
    for s in _sorted_secs:
        parts = s.split(".")
        if len(parts) > 2:
            parent = ".".join(parts[:-1])
            if parent in _sec_has_kid:
                _sec_has_kid[parent] = True

    def _populate_toc(query=""):
        # Freeze the widget while we mutate — big perf win.
        toc_tree.delete(*toc_tree.get_children(""))
        q = query.strip().lower()

        if not q:
            # fast path: no filter, no matching, just insert everything
            for sec in _sorted_secs:
                info = CHAPTER7_TOC[sec]
                parts = sec.split(".")
                parent = ".".join(parts[:-1]) if len(parts) > 2 else ""
                if parent and not toc_tree.exists(parent):
                    parent = ""
                toc_tree.insert(parent, "end", iid=sec,
                                text=f"{sec}   {info['title']}",
                                tags=("branch" if _sec_has_kid[sec] else "leaf",),
                                open=False)
            return

        # Filtered: precompute the set of sections that themselves match,
        # then include all their ancestors so the tree still forms a path.
        self_matches = set()
        for sec in _sorted_secs:
            info = CHAPTER7_TOC[sec]
            if q in sec.lower() or q in info["title"].lower():
                self_matches.add(sec)

        visible = set(self_matches)
        # add all ancestors of every match so tree paths stay intact
        for sec in list(self_matches):
            parts = sec.split(".")
            for i in range(2, len(parts)):
                visible.add(".".join(parts[:i]))

        for sec in _sorted_secs:
            if sec not in visible:
                continue
            info = CHAPTER7_TOC[sec]
            parts = sec.split(".")
            parent = ".".join(parts[:-1]) if len(parts) > 2 else ""
            if parent and not toc_tree.exists(parent):
                parent = ""
            toc_tree.insert(parent, "end", iid=sec,
                            text=f"{sec}   {info['title']}",
                            tags=("branch" if _sec_has_kid[sec] else "leaf",),
                            open=True)

    def _populate_cap(query=""):
        cap_tree.delete(*cap_tree.get_children(""))
        q = query.strip().lower()
        for cid in sorted(CAPABILITY_ID_MAP.keys()):
            info = CAPABILITY_ID_MAP[cid]
            label = f"{cid}   {info['name']}   §{info['section']}"
            if q and q not in label.lower():
                continue
            cap_tree.insert("", "end", iid=cid, text=label)

    def _populate_reg(query=""):
        reg_tree.delete(*reg_tree.get_children(""))
        q = query.strip().lower()
        for rn in sorted(REGISTER_DB.keys()):
            rd = REGISTER_DB[rn]
            label = (f"{rn.replace('_',' ').title()}   "
                     f"[{rd.get('offset','?')}]   §{rd.get('section','?')}")
            if q and q not in label.lower() and q not in rn.lower():
                continue
            reg_tree.insert("", "end", iid=rn, text=label)

    _populate_toc(); _populate_cap(); _populate_reg()

    # ── filter events (debounced) ────────────────────────────────────────────
    _filter_jobs = {"toc": None, "cap": None, "reg": None}

    def _debounce_filter(kind, populate_fn, var):
        job = _filter_jobs[kind]
        if job is not None:
            root.after_cancel(job)
        _filter_jobs[kind] = root.after(180, lambda: populate_fn(var.get()))

    toc_filter_var.trace_add("write",
        lambda *_: _debounce_filter("toc", _populate_toc, toc_filter_var))
    cap_filter_var.trace_add("write",
        lambda *_: _debounce_filter("cap", _populate_cap, cap_filter_var))
    reg_filter_var.trace_add("write",
        lambda *_: _debounce_filter("reg", _populate_reg, reg_filter_var))

    # ── tree selection → show ────────────────────────────────────────────────
    # Handlers ignore selections we made ourselves (via _select_*), otherwise
    # every programmatic sync would loop back into show_* infinitely.
    def _on_toc_select(_e):
        sel = toc_tree.selection()
        if not sel:
            return
        sec = sel[0]
        if _prog_toc[0] == sec:
            _prog_toc[0] = None       # consume the marker
            return
        show_section(sec)

    def _on_cap_select(_e):
        sel = cap_tree.selection()
        if not sel:
            return
        cid = sel[0]
        if _prog_cap[0] == cid:
            _prog_cap[0] = None
            return
        show_capability(cid)

    def _on_reg_select(_e):
        sel = reg_tree.selection()
        if not sel:
            return
        rn = sel[0]
        if _prog_reg[0] == rn:
            _prog_reg[0] = None
            return
        show_register(rn)

    toc_tree.bind("<<TreeviewSelect>>", _on_toc_select)
    cap_tree.bind("<<TreeviewSelect>>", _on_cap_select)
    reg_tree.bind("<<TreeviewSelect>>", _on_reg_select)

    # double-click on TOC branch = toggle open
    def _on_toc_double(e):
        item = toc_tree.identify_row(e.y)
        if item and toc_tree.get_children(item):
            toc_tree.item(item, open=not toc_tree.item(item, "open"))
    toc_tree.bind("<Double-Button-1>", _on_toc_double)

    # ═════════════════════════════════════════════════════════════════════════
    # SEARCH: debounce top-bar search box
    # ═════════════════════════════════════════════════════════════════════════
    _search_job = [None]
    def _on_search_key(e=None):
        # ignore modifier/navigation keys so debounce doesn't fire for arrows etc.
        if e is not None and e.keysym in (
            "Shift_L","Shift_R","Control_L","Control_R","Alt_L","Alt_R",
            "Left","Right","Up","Down","Home","End","Tab","Caps_Lock",
        ):
            return
        if _search_job[0] is not None:
            try: root.after_cancel(_search_job[0])
            except Exception: pass
        # DON'T let placeholder text be searched
        current = sv.get()
        if current == _placeholder:
            return
        _search_job[0] = root.after(260, lambda: show_search(sv.get()))
    ent.bind("<KeyRelease>", _on_search_key)

    # ═════════════════════════════════════════════════════════════════════════
    # MOUSE WHEEL → scroll whichever widget is under the pointer
    # (bound once on the root; no more bind_all/unbind_all thrashing)
    # ═════════════════════════════════════════════════════════════════════════
    def _widget_scroll(w, delta):
        """Try to scroll widget `w` vertically. Return True if handled."""
        try:
            w.yview_scroll(int(-delta / 120), "units")
            return True
        except (tk.TclError, AttributeError):
            return False

    def _on_mousewheel_global(event):
        # find widget directly under the pointer
        w = event.widget
        # walk up until we find a scrollable ancestor (Canvas/Treeview/Text)
        while w is not None:
            if isinstance(w, (tk.Canvas, ttk.Treeview, tk.Text, tk.Listbox)):
                if _widget_scroll(w, event.delta):
                    return "break"
            w = getattr(w, "master", None)
        # default: scroll the main content canvas
        _widget_scroll(canvas, event.delta)
        return "break"

    root.bind_all("<MouseWheel>", _on_mousewheel_global)

    # ═════════════════════════════════════════════════════════════════════════
    # KEYBOARD SHORTCUTS  (scoped carefully — no global <Return> hijack)
    # ═════════════════════════════════════════════════════════════════════════
    def _focus_search(_e=None):
        ent.focus_set()
        # if placeholder present, clear so user can type immediately
        if sv.get() == _placeholder:
            sv.set(""); ent.config(fg=TEXT)
        else:
            ent.select_range(0, "end")
        return "break"

    def _clear_or_home(e=None):
        # Esc: if search box focused → clear + go home; else no-op
        if root.focus_get() is ent:
            sv.set("")
            ent.config(fg=TEXT)
            show_welcome()
            return "break"

    # Enter inside the search box only: run search immediately
    def _search_enter(_e=None):
        if _search_job[0] is not None:
            try: root.after_cancel(_search_job[0])
            except Exception: pass
        q = sv.get()
        if q == _placeholder:
            return "break"
        show_search(q)
        return "break"
    ent.bind("<Return>", _search_enter)

    root.bind_all("<Control-f>",  _focus_search)
    root.bind_all("<Control-F>",  _focus_search)
    root.bind_all("<Escape>",     _clear_or_home)
    root.bind_all("<Alt-Left>",   go_back)
    root.bind_all("<Control-h>",  lambda e: (show_welcome(), "break")[1])
    root.bind_all("<Control-H>",  lambda e: (show_welcome(), "break")[1])
    root.bind_all("<Control-Key-1>", lambda e: (nb.select(tab_toc), "break")[1])
    root.bind_all("<Control-Key-2>", lambda e: (nb.select(tab_cap), "break")[1])
    root.bind_all("<Control-Key-3>", lambda e: (nb.select(tab_reg), "break")[1])

    # ── launch ────────────────────────────────────────────────────────────────
    _apply_placeholder()
    show_welcome(record=False)
    root.mainloop()


if __name__ == "__main__":
    run()