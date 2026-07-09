# PCIe Spec Upgrade Guide

This project supports multiple spec profiles and runtime switching from UI.

## Switch in UI

1. Start app: `python run_gui.py`
2. In the top bar, use the profile dropdown (for example `PCIe 5.0` / `PCIe 6.0`).
3. The app will refresh current page and `Open PDF` target immediately.

## Add a new spec profile (7.0, 8.0...)

1. Open `pcie_spec_config.py`.
2. Add one entry in `SPEC_PROFILES` with:
   - `key`
   - `name`
   - `revision`
   - `chapter`
   - `chapter_title`
   - `page_start`, `page_end`
   - `page_offset` (new_spec_ch7_start - 673)
   - `pdf_candidates` (one or more filenames)
3. Put your PDF into project root.
4. Restart GUI; the new profile appears in dropdown.

## Example `page_offset`

- Dataset page numbers are based on PCIe 5.0 Chapter 7.
- If your new spec Chapter 7 starts at p.859, then:
  - `page_offset = 859 - 673 = 186`

This keeps section/register mapping from current dataset while opening the corresponding page in newer PDF.

## Temporary override (optional)

Use environment variable to force a specific PDF path:

```powershell
$env:PCIE_SPEC_PDF = "D:\Path\To\NCB-PCI_Express_Base_6.0.pdf"
python run_gui.py
```

Priority order for PDF path:

1. `PCIE_SPEC_PDF` env var
2. active profile `pdf_candidates`
3. auto-discovered `NCB-PCI_Express_Base_*.pdf` (newest first)

## Important note

Profile switching updates labels and PDF jump pages.
The register/chapter dataset still comes from `pcie_ch7_tool.py`.
If a newer spec changes Chapter 7 definitions, update dataset separately.
