import traceback, sys

try:
    import pcie_ch7_gui as gui
    gui.run()
except Exception:
    traceback.print_exc()
    # Keep the console window open so the user can see the error
    input('Press Enter to exit...')
