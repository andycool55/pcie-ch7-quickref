#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# PCIe 5.0 Ch.7 Quick Reference -- STANDALONE, double-click to run
# Source: NCB-PCI_Express_Base_5.0r1.0-2019-05-22.pdf

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