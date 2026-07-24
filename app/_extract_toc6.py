#!/usr/bin/env python3
import re
from pathlib import Path

from pypdf import PdfReader


def main() -> None:
    project_root = Path(__file__).resolve().parent.parent
    pdf = str(project_root / "NCB-PCI_Express_Base_6.0.pdf")
    reader = PdfReader(pdf)
    items = []

    def walk(nodes):
        for node in nodes:
            if isinstance(node, list):
                walk(node)
                continue
            try:
                title = getattr(node, "title", "").replace("\xa0", " ").strip()
                page_index = reader.get_destination_page_number(node)
                if page_index is None:
                    continue
                page = page_index + 1
                items.append((title, page))
            except Exception:
                continue

    walk(reader.outline)

    pat = re.compile(r"^Section\s+(7(?:\.\d+)+)\s+(.+)$")
    toc = {}
    for title, page in items:
        m = pat.match(title)
        if m:
            toc[m.group(1)] = {"title": m.group(2).strip(), "page": page}

    out = Path(__file__).resolve().parent / "pcie_ch7_toc_6.py"
    with out.open("w", encoding="utf-8", newline="\n") as f:
        f.write("#!/usr/bin/env python3\n")
        f.write('"""Auto-generated TOC for PCIe 6.0 Chapter 7 from PDF outline."""\n\n')
        f.write("CHAPTER7_TOC_6 = {\n")
        for key in sorted(toc, key=lambda s: [int(x) for x in s.split(".")]):
            value = toc[key]
            title = value["title"].replace("\\", "\\\\").replace('"', '\\"')
            f.write(f'    "{key}": {{"title": "{title}", "page": {value["page"]}}},\n')
        f.write("}\n")

    print(f"wrote {out} sections={len(toc)}")


if __name__ == "__main__":
    main()
