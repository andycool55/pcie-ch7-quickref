#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PCIe Ch.7 Quick Reference -- STANDALONE, double-click to run
# Source PDF: configured in pcie_spec_config.py

import traceback, sys, os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import pcie_ch7_gui as gui
    print("Starting GUI...")
    gui.run()
    print("GUI finished")
except Exception as e:
    print("Error occurred:", str(e))
    traceback.print_exc()
    # Keep the console window open so the user can see the error
    input('Press Enter to exit...')
