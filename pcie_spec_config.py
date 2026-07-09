#!/usr/bin/env python3
"""Project-level PCIe spec metadata and PDF resolution helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional


PROJECT_ROOT = Path(__file__).resolve().parent
SPEC_PDF_ENV = "PCIE_SPEC_PDF"


@dataclass(frozen=True)
class SpecProfile:
    key: str
    name: str
    revision: str
    chapter: str
    chapter_title: str
    page_start: int
    page_end: int
    page_offset: int
    pdf_candidates: List[str]

    @property
    def label(self) -> str:
        return f"{self.name} ({self.revision})"

    @property
    def coverage_pages_count(self) -> int:
        return self.page_end - self.page_start + 1


SPEC_PROFILES: Dict[str, SpecProfile] = {
    "pcie5": SpecProfile(
        key="pcie5",
        name="PCIe 5.0",
        revision="5.0r1.0",
        chapter="7",
        chapter_title="Software Initialization and Configuration",
        page_start=673,
        page_end=1000,
        page_offset=0,
        pdf_candidates=["NCB-PCI_Express_Base_5.0r1.0-2019-05-22.pdf"],
    ),
    "pcie6": SpecProfile(
        key="pcie6",
        name="PCIe 6.0",
        revision="6.0",
        chapter="7",
        chapter_title="Software Initialization and Configuration",
        page_start=859,
        page_end=1269,
        page_offset=186,
        pdf_candidates=["NCB-PCI_Express_Base_6.0.pdf"],
    ),
}

# Default startup profile (UI can switch at runtime).
DEFAULT_SPEC_KEY = "pcie5"


def get_profile(key: Optional[str]) -> SpecProfile:
    if key and key in SPEC_PROFILES:
        return SPEC_PROFILES[key]
    return SPEC_PROFILES[DEFAULT_SPEC_KEY]


def list_profiles() -> List[SpecProfile]:
    return list(SPEC_PROFILES.values())


def _iter_candidate_paths(profile: SpecProfile) -> Iterable[Path]:
    env_path = os.environ.get(SPEC_PDF_ENV, "").strip()
    if env_path:
        yield Path(env_path)

    for name in profile.pdf_candidates:
        yield PROJECT_ROOT / name

    discovered = sorted(
        PROJECT_ROOT.glob("NCB-PCI_Express_Base_*.pdf"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    for path in discovered:
        yield path


def resolve_pdf_path(profile: Optional[SpecProfile] = None) -> str:
    p = profile or get_profile(None)
    for path in _iter_candidate_paths(p):
        try:
            if path.is_file():
                return str(path)
        except OSError:
            continue
    return str(PROJECT_ROOT / p.pdf_candidates[0])


def current_pdf_name(profile: Optional[SpecProfile] = None) -> str:
    return os.path.basename(resolve_pdf_path(profile))
