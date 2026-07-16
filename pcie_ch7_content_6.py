#!/usr/bin/env python3
"""Derived PCIe 6.0 Chapter 7 content built from the PDF outline."""

from __future__ import annotations

import re

from pcie_ch7_toc_6 import CHAPTER7_TOC_6


_OFF_RE = re.compile(r"\(Offset(?:s)?\s+([^)]+)\)")


def _slug(text: str) -> str:
    out = []
    for ch in text.upper():
        if ch.isalnum():
            out.append(ch)
        else:
            out.append("_")
    s = "".join(out)
    while "__" in s:
        s = s.replace("__", "_")
    return s.strip("_")


def build_capability_id_map_6() -> dict:
    base = {
        "03h": ("Vital Product Data (VPD)", "7.9.18"),
        "0001h": ("AER", "7.8.4"),
        "0002h": ("Virtual Channel", "7.9.1"),
        "0003h": ("Device Serial Number", "7.9.3"),
        "0004h": ("Power Budgeting", "7.8.1"),
        "0005h": ("Root Complex Link Declaration", "7.9.8"),
        "0006h": ("Root Complex Internal Link Control", "7.9.9"),
        "0007h": ("RCEC Endpoint Association", "7.9.10"),
        "0009h": ("Multi-Function Virtual Channel", "7.9.2"),
        "000Ah": ("RCRB Header", "7.9.7"),
        "000Bh": ("Vendor-Specific Extended Capability", "7.9.5"),
        "000Dh": ("Access Control Services", "7.7.11"),
        "000Eh": ("ARI", "7.8.8"),
        "0012h": ("Multicast", "7.9.11"),
        "0014h": ("Enhanced Allocation", "7.8.5"),
        "0010h": ("SR-IOV", "7.8.16"),
        "0015h": ("Resizable BAR", "7.8.6"),
        "0016h": ("Dynamic Power Allocation", "7.9.12"),
        "0017h": ("TPH Requester", "7.9.13"),
        "0018h": ("Latency Tolerance Reporting", "7.8.2"),
        "0019h": ("Secondary PCI Express", "7.7.3"),
        "001Ah": ("Protocol Multiplexing", "7.9.21"),
        "001Bh": ("PASID", "7.8.9"),
        "001Ch": ("LN Requester", "7.9.14"),
        "001Dh": ("Downstream Port Containment", "7.9.14"),
        "001Eh": ("L1 PM Substates", "7.8.3"),
        "001Fh": ("Precision Time Measurement", "7.8.17"),
        "0021h": ("FRS Queueing", "7.8.10"),
        "0022h": ("Readiness Time Reporting", "7.9.16"),
        "0023h": ("Designated Vendor-Specific Extended Capability", "7.9.6"),
        "0025h": ("Data Link Feature", "7.7.4"),
        "0026h": ("Physical Layer 16.0 GT/s", "7.7.5"),
        "0027h": ("Lane Margining at the Receiver", "7.7.10"),
        "0028h": ("Hierarchy ID", "7.8.15"),
        "0029h": ("Native PCIe Enclosure Management", "7.8.18"),
        "002Ah": ("Physical Layer 32.0 GT/s", "7.7.6"),
        "002Bh": ("Alternate Protocol", "7.8.19"),
        "002Ch": ("System Firmware Intermediary", "7.8.20"),
        "002Dh": ("Shadow Functions", "7.8.21"),
        "002Eh": ("Data Object Exchange", "7.8.22"),
        "002Fh": ("Device 3", "7.7.9"),
        "0030h": ("Physical Layer 64.0 GT/s", "7.7.7"),
        "0031h": ("Flit Logging", "7.7.8"),
        "0032h": ("Flit Performance Measurement", "7.8.12"),
        "0033h": ("Flit Error Injection", "7.8.13"),
    }

    cap_map = {}
    for cap_id, (name, sec) in base.items():
        if sec in CHAPTER7_TOC_6:
            cap_map[cap_id] = {"name": name, "section": sec}
    return cap_map


def build_register_db_6_outline() -> dict:
    reg_db = {}
    for sec, info in CHAPTER7_TOC_6.items():
        title = info.get("title", "")
        if "Register" not in title:
            continue
        mo = _OFF_RE.search(title)
        if not mo:
            continue

        offset = mo.group(1).strip()
        reg_name = _slug(title.replace("Register", "").strip())
        if not reg_name:
            reg_name = _slug(sec)
        key = reg_name
        idx = 2
        while key in reg_db:
            key = f"{reg_name}_{idx}"
            idx += 1

        reg_db[key] = {
            "section": sec,
            "offset": offset,
            "page": info.get("page", 0),
            "bits": {
                "31:0": {
                    "name": "See PCIe 6.0 spec",
                    "attr": "RO",
                    "desc": "Auto-imported from Chapter 7 outline. Detailed bit fields are pending manual modeling.",
                }
            },
        }
    return reg_db


CAPABILITY_ID_MAP_6 = build_capability_id_map_6()
REGISTER_DB_6_OUTLINE = build_register_db_6_outline()
