#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PCIe Ch.7 Quick Reference -- double-click launcher

import traceback

from run_gui import main


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        # Keep the console window open so the user can see the error
        input("Press Enter to exit...")
